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
import numpy as np
import itertools
import random


def get_density_bins(songs_data, window_size_bars, hop_length_bars, bins):
    # Go through all songs and count the NOTE_ON events for each
    # window_size_bars
    distribution = []
    for song_data in songs_data:
        # Count the bars
        bars = get_bars_number(song_data)
        # Iterate over the tracks and the bars
        bar_indices = get_bar_indices(bars, window_size_bars, hop_length_bars)
        for track_data in song_data["tracks"]:
            for bar_start_index, bar_end_index in bar_indices:
                # Go through the bars and count the notes
                count = 0
                for bar in track_data["bars"][bar_start_index:bar_end_index]:
                    count += len(
                        [event for event in bar["events"] if event["type"] == "NOTE_ON"]
                    )

                # Do not count empty tracks
                if count != 0:
                    distribution += [count]

    # Comput the quantiles, which will become the density bins
    quantiles = []
    for i in range(100 // bins, 100, 100 // bins):
        quantile = np.percentile(distribution, i)
        quantiles += [quantile]

    return quantiles


def get_bars_number(song_data):
    bars = [len(track_data["bars"]) for track_data in song_data["tracks"]]
    bars = max(bars)
    return bars


def get_bar_indices(bars, window_size_bars, hop_length_bars):
    """
    Gets the indices of the bars that will be used for encoding.

    Args:
        bars: The number of bars in the song.
        window_size_bars: The size of the window in bars.
        hop_length_bars: The hop length in bars.

    Returns:
        A list of tuples, where each tuple contains the start index and end index of a window.
    """

    indices = []
    start = 0
    while start + window_size_bars <= bars:
        indices.append((start, start + window_size_bars))
        start += hop_length_bars
    print(indices)
    return indices


def encode_songs_data(
    songs_data,
    transpositions,
    permute,
    window_size_bars,
    hop_length_bars,
    density_bins,
    bar_fill,
):
    # This will be returned
    token_sequences = []

    # Go through all songs
    for song_data in songs_data:
        token_sequences += encode_song_data(
            song_data,
            transpositions,
            permute,
            window_size_bars,
            hop_length_bars,
            density_bins,
            bar_fill,
        )

    return token_sequences


def encode_song_data(
    song_data,
    transpositions,
    permute,
    window_size_bars,
    hop_length_bars,
    density_bins,
    bar_fill,
):
    # This will be returned
    token_sequences = []

    # Count the bars
    bars = get_bars_number(song_data)

    # For iterating over the bars
    bar_indices = get_bar_indices(bars, window_size_bars, hop_length_bars)

    # Go through all combinations
    count = 0
    for (bar_start_index, bar_end_index), transposition in itertools.product(
        bar_indices, transpositions
    ):
        # Start empty
        token_sequence = []

        # Do bar fill if necessary
        if bar_fill:
            track_data = random.choice(song_data["tracks"])
            bar_data = random.choice(track_data["bars"][bar_start_index:bar_end_index])
            bar_data_fill = {"events": bar_data["events"]}
            bar_data["events"] = "bar_fill"

        # Start with the tokens
        token_sequence += ["PIECE_START"]
        token_sequence += [
            "TIME_SIGNATURE="
            + str(song_data["time_signature_numerator"])
            + ("_")
            + str(song_data["time_signature_denominator"])
        ]
        token_sequence += ["GENRE=" + str(song_data["genre"])]

        # Get the indices. Permute if necessary
        track_data_indices = list(range(len(song_data["tracks"])))
        if permute:
            random.shuffle(track_data_indices)

        # Encode the tracks
        for track_data_index in track_data_indices:
            track_data = song_data["tracks"][track_data_index]

            # Encode the track. Insert density tokens and transpose
            encoded_track_data = encode_track_data(
                track_data, density_bins, bar_start_index, bar_end_index, transposition
            )
            token_sequence += encoded_track_data

        # Encode the fill tokens
        if bar_fill:
            token_sequence += encode_bar_data(
                bar_data_fill, transposition, bar_fill=True
            )

        token_sequences += [token_sequence]
        count += 1

    # Done
    return token_sequences


def encode_track_data(
    track_data, density_bins, bar_start_index, bar_end_index, transposition
):
    tokens = []

    tokens += ["TRACK_START"]

    # Set an instrument
    number = track_data["midi_program"]

    # Set the instrument if it is not a drum
    if not track_data.get("drums", False):
        tokens += [f"INST={number}"]

    # Set the instrument if it is drums. Do not transpose
    else:
        tokens += ["INST=DRUMS"]
        transposition = 0

    # Count NOTE_ON events
    note_on_events = 0
    for bar_data in track_data["bars"][bar_start_index:bar_end_index]:
        if bar_data["events"] == "bar_fill":
            continue
        for event_data in bar_data["events"]:
            if event_data["type"] == "NOTE_ON":
                note_on_events += 1

    # Determine density
    density = np.digitize(note_on_events, density_bins)
    tokens += [f"DENSITY={density}"]

    # Encode the bars
    for bar_data in track_data["bars"][bar_start_index:bar_end_index]:
        tokens += encode_bar_data(bar_data, transposition, bar_fill=False)

    tokens += ["TRACK_END"]

    return tokens


def encode_bar_data(bar_data, transposition, bar_fill=False):
    tokens = []

    if not bar_fill:
        tokens += ["BAR_START"]
    else:
        tokens += ["FILL_START"]

    if bar_data["events"] == "bar_fill":
        tokens += ["FILL_IN"]
    else:
        for event_data in bar_data["events"]:
            tokens += [encode_event_data(event_data, transposition)]

    if not bar_fill:
        tokens += ["BAR_END"]
    else:
        tokens += ["FILL_END"]

    return tokens


def encode_event_data(event_data, transposition):
    if event_data["type"] != "TIME_DELTA":
        return event_data["type"] + "=" + str(event_data["pitch"] + transposition)
    else:
        return event_data["type"] + "=" + str(event_data["delta"])
