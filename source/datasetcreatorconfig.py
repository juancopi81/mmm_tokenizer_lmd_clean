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
from typing import List
from pathlib import Path

from pydantic import BaseModel, validator, Field

from source import logging


logger = logging.create_logger("datasetcreatorconfig")


class LMDCleanDatasetCreatorBarConfig(BaseModel):
    """
    A configuration class for the LMDCleanDatasetCreatorBar.

    This class contains various fields that represent configuration parameters
    for the LMDCleanDatasetCreatorBar, including dataset name, encoding method,
    json data method, window size in bars, hop length in bars, number of density
    bins, list of transpositions for training, a boolean indicating whether to
    permute tracks, and a list of paths to MIDI files.

    Attributes:
        dataset_name: A string indicating the name of the dataset.
        encoding_method: A string indicating the encoding method.
        json_data_method: A string indicating the JSON data method.
        window_size_bars: An integer indicating the number of bars per track.
        hop_length_bars: An integer indicating the number of bars to jump in each window_size_bars.
        density_bins_number: An integer indicating the number of density bins.
        transpositions_train: A list of integers indicating transpositions for training.
        permute_tracks: A boolean indicating whether to permute tracks.
        num_files_per_iteration: Number of files to process at a time.
        midi_paths: A list of strings indicating paths to MIDI files.
        save_path: This is a folder where the tokenized dataset will be saved.

    Methods:
        check_if_paths_exists(cls, value: List): Validates that the provided MIDI file paths exist.
    """

    # Optional arguments
    dataset_name: str = Field(
        "lmd_dataset_mmmtrack",
        description="Name of dataset: Folder with results of tokenization",
    )
    encoding_method: str = Field(
        "mmmtrack", description="Encoding method, could be mmmtrack or mmmbar"
    )
    json_data_method: str = Field(
        "preprocess_music21", description="Json method to encode Midi files"
    )
    window_size_bars: int = Field(8, description="Number of bars per track to tokenize")
    hop_length_bars: int = Field(
        8, description="Number of bars to jumps in each windos_size_bars"
    )
    density_bins_number: int = Field(
        5, description="Bins used to stablish density. Default '5'"
    )
    transpositions_train: List = Field(
        [0], description="Transposition to implement for data augmentation"
    )
    permute_tracks: bool = Field(True, description="Permute tracks randomly")
    num_files_per_iteration: int = Field(
        10, description="Number of files to process at a time"
    )
    # Mandatory arguments
    midi_source: str = Field(description="Folder with the LMD dataset")
    save_path: Path = Field(description="Path where tokenized dataset will be saved")

    @validator("save_path", pre=True)
    @classmethod
    def convert_to_path(cls, value: str) -> Path:
        """
        Converts the provided save_path to a Path object.

        Args:
            value: A string representing the save_path.

        Returns:
            The Path object representing the save_path.
        """
        return Path(value)

    @validator("midi_source")
    @classmethod
    def check_if_paths_exists(cls, value: Path) -> List:
        """
        Validates that the provided MIDI file paths exist.

        Args:
            value: A list of strings representing MIDI file paths.

        Raises:
            FileExistsError: If any of the provided paths do not point to an existing file.

        Returns:
            The original list of MIDI file paths, if all paths point to an existing file.
        """
        if not os.path.isdir(value):
            message = f"'{value}' folder does not exist."
            raise FileExistsError(message)
        return value
