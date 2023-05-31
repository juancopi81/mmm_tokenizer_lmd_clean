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

import pydantic_argparse

from source.datasetcreatorconfig import LMDCleanDatasetCreatorBarConfig
from source import datasetcreator
from source import logging
from source.preprocess.loading.loaderiterator import LoaderIterator
from source.preprocess.loading.serialization import Music21Serializer


logger = logging.create_logger("main")
# Create dataset if it does not exist yet
# dataset_creator_config = datasetcreatorconfig.CustomDatasetCreatorTrackConfig()
# dataset_creator.create(dataset_path=os.path.join("datasets"), overwrite=True)


def main() -> None:
    # Create Parser and Parse Args
    parser = pydantic_argparse.ArgumentParser(
        model=LMDCleanDatasetCreatorBarConfig,
        prog="MMM Tokenizer LMD Clean",
        description="This programs tokenize the LMD clean dataset using the MMM tokenizer",
        version="0.0.1",
        epilog="Based on the implemenatation of Dr. Tristan Behrens.",
    )
    dataset_creator_config = parser.parse_typed_args()

    # Print Args
    logger.info("Creating DatasetCreator")
    dataset_creator = datasetcreator.DatasetCreator(dataset_creator_config)

    # Get songs from folder and iterate in batches
    logger.info("Creating list of path files...")
    midi_paths = sorted(
        list(Path(dataset_creator_config.midi_source).glob("**/*.mid"))
        + list(Path(dataset_creator_config.midi_source).glob("**/*.midi"))
    )
    logger.info(f"There are {len(midi_paths)} midi files in the directory")
    batch_size = dataset_creator_config.num_files_per_iteration

    logger.info("Creating loader iterator...")
    loader_iterator = LoaderIterator(Music21Serializer(), batch_size, midi_paths)
    logger.info(f"Loader iterator ready.")

    # Try to recover last iteration from a file
    iteration_file = (
        dataset_creator_config.save_path
        / dataset_creator_config.dataset_name
        / "last_iteration.txt"
    )
    if os.path.exists(iteration_file):
        with open(iteration_file, "r") as f:
            last_iteration = int(f.read().strip())
            loader_iterator.set_current_iteration(last_iteration)

    # Iterate over the batches
    logger.info(f"Loading songs")
    for batch_data in loader_iterator:
        logger.info(f"Got {len(batch_data)} songs")
        # Do some processing
        dataset_creator.create(
            dataset_path=dataset_creator_config.save_path,
            m21_streams=batch_data,
            current_iteration=loader_iterator._current_iteration,
            overwrite=True,
        )

        # Keep some how the information in long-term storage so if the computer breaks, we can resume the processing
        # Write current iteration to a file
        loader_iterator.write_current_iteration(iteration_file)


if __name__ == "__main__":
    main()
