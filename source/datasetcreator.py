# Original License:
# Copyright 2021 Tristan Behrens.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3

import os
from pathlib import Path
from typing import List

from music21.stream import Score

from source import logging
from source.preprocess.music21lmd import preprocess_music21
from source.preprocess.encode import get_density_bins, encode_songs_data

logger = logging.create_logger("datasetcreator")


class DatasetCreator:
    def __init__(self, config):
        self.config = config

    def create(
        self,
        dataset_path: Path,
        m21_streams: List[Score],
        current_iteration: int,
        overwrite=False,
    ) -> None:
        # Make sure the dataset_path exists
        if not os.path.exists(dataset_path):
            os.mkdir(dataset_path)

        # Make sure that path for this specific dataset exists
        dataset_path = os.path.join(dataset_path, self.config.dataset_name)
        if os.path.exists(dataset_path) and overwrite is False:
            logger.info("Dataset already exists.")
            return
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)

        # Prepare for getting music data as json
        json_data_method = None
        if self.config.json_data_method == "preprocess_music21":
            json_data_method = preprocess_music21
        elif callable(self.config.json_data_method):
            json_data_method = self.config.json_data_method
        else:
            error_string = f"Unexpected {self.config.json_data_method}"
            logger.error(error_string)
            raise Exception(error_string)

        # Get music data as json
        songs_data_train, songs_data_valid = json_data_method(m21_streams)

        # Get density bins
        density_bins = get_density_bins(
            songs_data_train,
            self.config.window_size_bars,
            self.config.hop_length_bars,
            self.config.density_bins_number,
        )

        # Process and save training data
        token_sequences_train = encode_songs_data(
            songs_data_train,
            transpositions=self.config.transpositions_train,
            permute=self.config.permute_tracks,
            window_size_bars=self.config.window_size_bars,
            hop_length_bars=self.config.hop_length_bars,
            density_bins=density_bins,
            bar_fill=self.config.encoding_method == "mmmbar",
        )

        dataset_path_train = os.path.join(
            dataset_path, f"token_sequences_train_{current_iteration}.txt"
        )
        self.__save_token_sequences(token_sequences_train, dataset_path_train)
        logger.info(f"Saved training data to {dataset_path_train}")

        # Process and save validation data
        token_sequences_valid = encode_songs_data(
            songs_data_valid,
            transpositions=[0],
            permute=self.config.permute_tracks,
            window_size_bars=self.config.window_size_bars,
            hop_length_bars=self.config.hop_length_bars,
            density_bins=density_bins,
            bar_fill=self.config.encoding_method == "mmmbar",
        )

        dataset_path_valid = os.path.join(
            dataset_path, f"token_sequences_valid_{current_iteration}.txt"
        )
        self.__save_token_sequences(token_sequences_valid, dataset_path_valid)
        logger.info(f"Saved validation data to {dataset_path_valid}")

    def __save_token_sequences(self, token_sequences, path):
        with open(path, "w") as file:
            for token_sequence in token_sequences:
                print(" ".join(token_sequence), file=file)
