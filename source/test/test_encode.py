import numpy as np
import pytest

from source.preprocess.encode import (
    get_bars_number,
    get_bar_indices,
    get_density_bins,
    encode_event_data,
    encode_bar_data,
    encode_track_data,
    encode_song_data,
)
from source.test.expected_output import json_output


def test_get_bars_number():
    # Create a sample song_data dict
    song_data = {
        "tracks": [
            {"bars": [1, 2, 3]},  # 3 bars in the first track
            {"bars": [1, 2]},  # 2 bars in the second track
            {"bars": [1, 2, 3, 4]},  # 4 bars in the third track
        ]
    }

    expected_bars_number = 4  # The maximum number of bars in any track
    output_bars_number = get_bars_number(song_data)

    assert (
        output_bars_number == expected_bars_number
    ), f"Expected {expected_bars_number} but got {output_bars_number}"


def test_get_bar_indices():
    # Define input values
    bars = 10
    window_size_bars = 4
    hop_length_bars = 2

    # Calculate output
    output_indices = get_bar_indices(bars, window_size_bars, hop_length_bars)

    # Define expected output
    expected_indices = [(0, 4), (2, 6), (4, 8), (6, 10), (8, 10)]

    # Assert that the output matches the expected output
    assert (
        output_indices == expected_indices
    ), f"Expected {expected_indices} but got {output_indices}"

    # Define input values
    bars_2 = get_bars_number(json_output)
    window_size_bars_2 = 2
    hop_length_bars_2 = 1

    # Calculate output
    output_indices_2 = get_bar_indices(bars_2, window_size_bars_2, hop_length_bars_2)

    # Define expected output
    expected_indices_2 = [(0, 2), (1, 2)]

    # Assert that the output matches the expected output
    assert (
        output_indices_2 == expected_indices_2
    ), f"Expected {expected_indices_2} but got {output_indices_2}"


def test_get_density_bins():
    # Load the song data
    songs_data = [json_output]

    # Define the input parameters for get_density_bins
    window_size_bars = 1  # Use a window size of 1 bar for simplicity
    hop_length_bars = 1  # Use a hop length of 1 bar for simplicity
    bins = 2  # Use 2 bins for simplicity

    # Calculate output
    output_bins = get_density_bins(songs_data, window_size_bars, hop_length_bars, bins)

    # These values will depend on the number of NOTE_ON events
    # Here, each bar in each track has 4 NOTE_ON events, so the distribution is [4, 4, 4, 4, 4, 4, 7, 7]
    # So the percentiles are calculated based on this.
    expected_bins = [5.0]

    # Assert that the output matches the expected output
    assert (
        output_bins == expected_bins
    ), f"Expected {expected_bins} but got {output_bins}"


def test_encode_event_data():
    # Test 1: with "NOTE_ON" type event and no transposition
    event_data_1 = {"type": "NOTE_ON", "pitch": 60}
    expected_result_1 = "NOTE_ON=60"
    assert encode_event_data(event_data_1, 0) == expected_result_1

    # Test 2: with "NOTE_ON" type event and a positive transposition
    event_data_2 = {"type": "NOTE_ON", "pitch": 60}
    expected_result_2 = "NOTE_ON=62"
    assert encode_event_data(event_data_2, 2) == expected_result_2

    # Test 3: with "NOTE_ON" type event and a negative transposition
    event_data_3 = {"type": "NOTE_ON", "pitch": 60}
    expected_result_3 = "NOTE_ON=58"
    assert encode_event_data(event_data_3, -2) == expected_result_3

    # Test 4: with "NOTE_OFF" type event and a negative transposition
    event_data_3 = {"type": "NOTE_OFF", "pitch": 60}
    expected_result_3 = "NOTE_OFF=58"
    assert encode_event_data(event_data_3, -2) == expected_result_3

    # Test 5: with "TIME_DELTA" type event
    event_data_4 = {"type": "TIME_DELTA", "delta": 4.0}
    expected_result_4 = "TIME_DELTA=4.0"
    assert encode_event_data(event_data_4, 0) == expected_result_4

    # Test 6: with unrecognized event type
    with pytest.raises(KeyError):
        encode_event_data({"type": "UNRECOGNIZED_TYPE", "value": 1}, 0)


def test_encode_bar_data():
    # Test 1: with normal bar and no transposition
    bar_data_1 = {
        "events": [{"type": "NOTE_ON", "pitch": 60}, {"type": "NOTE_OFF", "pitch": 60}]
    }
    expected_result_1 = ["BAR_START", "NOTE_ON=62", "NOTE_OFF=62", "BAR_END"]
    assert encode_bar_data(bar_data_1, 2, False) == expected_result_1

    # Test 2: with normal bar and negative transposition
    bar_data_2 = {
        "events": [{"type": "NOTE_ON", "pitch": 60}, {"type": "NOTE_OFF", "pitch": 60}]
    }
    expected_result_2 = ["BAR_START", "NOTE_ON=58", "NOTE_OFF=58", "BAR_END"]
    assert encode_bar_data(bar_data_2, -2, False) == expected_result_2

    # Test 3: with bar fill and no transposition
    bar_data_3 = {"events": "bar_fill"}
    expected_result_3 = ["FILL_START", "FILL_IN", "FILL_END"]
    assert encode_bar_data(bar_data_3, 0, True) == expected_result_3

    # Test 4: with bar fill and transposition, transposition should not affect the fill bar
    bar_data_4 = {"events": "bar_fill"}
    expected_result_4 = ["FILL_START", "FILL_IN", "FILL_END"]
    assert encode_bar_data(bar_data_4, 2, True) == expected_result_4

    # Test 5: More complex bar with time deltas
    bar_data_5 = {
        "events": [
            {"pitch": 60, "type": "NOTE_ON"},
            {"delta": 4.0, "type": "TIME_DELTA"},
            {"pitch": 60, "type": "NOTE_OFF"},
            {"pitch": 60, "type": "NOTE_ON"},
            {"delta": 4.0, "type": "TIME_DELTA"},
            {"pitch": 60, "type": "NOTE_OFF"},
            {"pitch": 60, "type": "NOTE_ON"},
            {"delta": 4.0, "type": "TIME_DELTA"},
            {"pitch": 60, "type": "NOTE_OFF"},
            {"pitch": 60, "type": "NOTE_ON"},
            {"delta": 4.0, "type": "TIME_DELTA"},
            {"pitch": 60, "type": "NOTE_OFF"},
        ]
    }
    expected_result_5 = [
        "BAR_START",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "BAR_END",
    ]
    assert encode_bar_data(bar_data_5, 0, False) == expected_result_5


def test_encode_track_data():
    # Define input values
    track_data = json_output["tracks"][0]
    density_bins = np.array([5, 10])
    bar_start_index = 0
    bar_end_index = 2
    transposition = 0

    # Calculate output
    output_tokens = encode_track_data(
        track_data, density_bins, bar_start_index, bar_end_index, transposition
    )

    # Define expected output
    expected_tokens = [
        "TRACK_START",
        "INST=40",
        "DENSITY=1",
        "BAR_START",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "NOTE_ON=60",
        "TIME_DELTA=4.0",
        "NOTE_OFF=60",
        "BAR_END",
        "BAR_START",
        "NOTE_ON=62",
        "TIME_DELTA=4.0",
        "NOTE_OFF=62",
        "NOTE_ON=62",
        "TIME_DELTA=4.0",
        "NOTE_OFF=62",
        "NOTE_ON=62",
        "TIME_DELTA=4.0",
        "NOTE_OFF=62",
        "NOTE_ON=62",
        "TIME_DELTA=4.0",
        "NOTE_OFF=62",
        "BAR_END",
        "TRACK_END",
    ]

    # Assert that the output matches the expected output
    assert (
        output_tokens == expected_tokens
    ), f"Expected {expected_tokens} but got {output_tokens}"


def test_encode_song_data():
    # Define input values
    song_data = json_output
    transpositions = [0]
    permute = False
    window_size_bars = 2
    hop_length_bars = 1
    density_bins = np.array([5, 10])
    bar_fill = False

    # Calculate output
    output_token_sequences = encode_song_data(
        song_data,
        transpositions,
        permute,
        window_size_bars,
        hop_length_bars,
        density_bins,
        bar_fill,
    )

    # Define expected output
    expected_token_sequences = [
        [
            "PIECE_START",
            "TIME_SIGNATURE=4_4",
            "GENRE=TEST GENRE",
            "TRACK_START",
            "INST=40",
            "DENSITY=1",
            "BAR_START",
            "NOTE_ON=60",
            "TIME_DELTA=4.0",
            "NOTE_OFF=60",
            "NOTE_ON=60",
            "TIME_DELTA=4.0",
            "NOTE_OFF=60",
            "NOTE_ON=60",
            "TIME_DELTA=4.0",
            "NOTE_OFF=60",
            "NOTE_ON=60",
            "TIME_DELTA=4.0",
            "NOTE_OFF=60",
            "BAR_END",
            "BAR_START",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "BAR_END",
            "TRACK_END",
            "TRACK_START",
            "INST=24",
            "DENSITY=2",
            "BAR_START",
            "NOTE_ON=64",
            "TIME_DELTA=4.0",
            "NOTE_OFF=64",
            "NOTE_ON=64",
            "TIME_DELTA=4.0",
            "NOTE_OFF=64",
            "NOTE_ON=64",
            "TIME_DELTA=4.0",
            "NOTE_OFF=64",
            "NOTE_ON=62",
            "NOTE_ON=66",
            "NOTE_ON=69",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_OFF=66",
            "NOTE_OFF=69",
            "BAR_END",
            "BAR_START",
            "NOTE_ON=65",
            "TIME_DELTA=4.0",
            "NOTE_OFF=65",
            "NOTE_ON=65",
            "TIME_DELTA=4.0",
            "NOTE_OFF=65",
            "NOTE_ON=65",
            "TIME_DELTA=4.0",
            "NOTE_OFF=65",
            "NOTE_ON=62",
            "NOTE_ON=66",
            "NOTE_ON=69",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_OFF=66",
            "NOTE_OFF=69",
            "BAR_END",
            "TRACK_END",
        ],
        [
            "PIECE_START",
            "TIME_SIGNATURE=4_4",
            "GENRE=TEST GENRE",
            "TRACK_START",
            "INST=40",
            "DENSITY=0",
            "BAR_START",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_ON=62",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "BAR_END",
            "TRACK_END",
            "TRACK_START",
            "INST=24",
            "DENSITY=1",
            "BAR_START",
            "NOTE_ON=65",
            "TIME_DELTA=4.0",
            "NOTE_OFF=65",
            "NOTE_ON=65",
            "TIME_DELTA=4.0",
            "NOTE_OFF=65",
            "NOTE_ON=65",
            "TIME_DELTA=4.0",
            "NOTE_OFF=65",
            "NOTE_ON=62",
            "NOTE_ON=66",
            "NOTE_ON=69",
            "TIME_DELTA=4.0",
            "NOTE_OFF=62",
            "NOTE_OFF=66",
            "NOTE_OFF=69",
            "BAR_END",
            "TRACK_END",
        ],
    ]

    # Assert that the output matches the expected output
    assert (
        output_token_sequences == expected_token_sequences
    ), f"Expected {expected_token_sequences} but got {output_token_sequences}"
