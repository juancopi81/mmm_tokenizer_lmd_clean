# Encode MIDI files from the Mutopia Project as text tokens.

## Tokenize the Mutopia Guitar Dataset using the Multi-Track Music Machine (MMM) representation.

This code was built on top of the (implementation)[https://github.com/AI-Guru/MMM-JSB] of (Dr. Tristan Behrens)[https://www.linkedin.com/in/dr-tristan-behrens-734967a2/] of the "MMM: Exploring Conditional Multi-Track Music Generation with the Transformer" [paper](https://arxiv.org/abs/2008.06048). The changes to the original code are just a few adaptations so the repo could work with the [Mutopia Guitar Dataset](https://huggingface.co/datasets/juancopi81/mutopia_guitar_dataset).

This repo is part of the tutorial **(MMM Mutopia Guitar)[https://github.com/juancopi81/MMM_Mutopia_Guitar]**.

## About.

This repository allows the user to represent the guitar MIDI files from the Mutopia Project as text tokens, as explained in the paper "MMM: Exploring Conditional Multi-Track Music Generation with the Transformer" [paper](https://arxiv.org/abs/2008.06048). It can be used to create the datasets using the MMMTrack version from the paper.

The code can also be used for the Johann Sebastian Bach chorale dataset from music21.

## How to run.

Requirements:

```
pip install music21
```

Creating the dataset:

1. Clone this repository.
2. Add the MIDI files to the folder `datasets/custom_midi_dataset/`.
3. Create the MMMTrack datasets with `python create_dataset_mmm.py`.

The code will create two text files:

* `datasets/mutopia_guitar_mmmtrack/token_sequences_train.txt`
* `datasets/mutopia_guitar_mmmtrack/token_sequences_valid.txt`

The `datasetcreatorcongif.py` comes with default configurations that users can change to their necessities.

## License.

Released under the Apache-2.0 License.