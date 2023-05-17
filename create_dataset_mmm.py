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

import pydantic_argparse

from source.datasetcreatorconfig import LMDCleanDatasetCreatorBarConfig
from source import datasetcreator


# Create dataset if it does not exist yet
# dataset_creator_config = datasetcreatorconfig.CustomDatasetCreatorTrackConfig()
# dataset_creator = datasetcreator.DatasetCreator(dataset_creator_config)
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
    print(dataset_creator_config)


if __name__ == "__main__":
    main()
