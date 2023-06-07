import pytest
import music21
from music21 import meter, note, chord, instrument
from music21.stream import Score, Part, Measure
from source.preprocess.music21lmd import (
    preprocess_music21_song,
    preprocess_music21_part,
    preprocess_music21_measure,
)
from source.test.expected_output import json_output
from source.preprocess.preprocessutilities import events_to_events_data


# Helper function to create a simple song with 1 measure and 1 note
def create_simple_song():
    # Create first part with 2 measures
    part1 = Part()
    part1.insert(instrument.Violin())
    for i in range(2):
        m = Measure(number=i + 1)
        for j in range(4):
            m.append(note.Note("C4" if i % 2 == 0 else "D4"))
        part1.append(m)

    # Create second part with 2 measures
    part2 = Part()
    part2.insert(instrument.Guitar())
    for i in range(2):
        m = Measure(number=i + 1)
        for j in range(4):
            if j == 3:
                m.append(chord.Chord(["D", "F#", "A"]))
            else:
                m.append(note.Note("E4" if i % 2 == 0 else "F4"))
        part2.append(m)

    # Create a score and add the parts
    s = Score()
    s.insert(0, part1)
    s.insert(0, part2)
    ts = meter.TimeSignature("4/4")
    part1.insert(0, ts)

    # Add metadata
    s.metadata = music21.metadata.Metadata()
    s.metadata.title = "Test Song"
    s.metadata.number = 1
    s.metadata.setCustom("genre", "TEST GENRE")
    return s


@pytest.fixture
def sample_song():
    return create_simple_song()


def test_preprocess_music21_song(sample_song):
    output = preprocess_music21_song(sample_song, True)
    expected_output = json_output
    assert output == expected_output


def test_preprocess_music21_part(sample_song):
    # Use the first part of the sample song for testing
    part1 = sample_song.parts[0]

    # Preprocess the part
    output1 = preprocess_music21_part(part1, 0, True)

    # Here's what we expect the output to be, based on how create_simple_song works
    expected_output1 = json_output["tracks"][0]
    assert output1 == expected_output1

    # Use the second part of the sample song for testing
    part2 = sample_song.parts[1]

    # Preprocess the part
    output2 = preprocess_music21_part(part2, 1, True)

    # Here's what we expect the output to be, based on how create_simple_song works
    expected_output2 = json_output["tracks"][1]
    assert output2 == expected_output2


def test_preprocess_music21_measure(sample_song):
    # Get the measures of the first part
    part1 = sample_song.parts[0]
    part2 = sample_song.parts[1]
    measure1 = part1.measure(1)
    measure2 = part2.measure(2)

    # Preprocess the measures
    output1 = preprocess_music21_measure(measure1, True)
    output2 = preprocess_music21_measure(measure2, True)

    # Here's what we expect the output to be, based on the contents of the measures
    expected_output1 = json_output["tracks"][0]["bars"][0]
    expected_output2 = json_output["tracks"][1]["bars"][1]

    assert output1 == expected_output1
    assert output2 == expected_output2


def test_events_to_events_data():
    # Define a test list of events
    events = [
        ("NOTE_ON", 67, 0.0),
        ("NOTE_OFF", 67, 4.0),
        ("NOTE_ON", 68, 8.0),
        ("NOTE_OFF", 68, 12.0),
    ]

    # Preprocess the events
    output = events_to_events_data(events)

    # Define the expected output
    expected_output = [
        {"type": "NOTE_ON", "pitch": 67},
        {"type": "TIME_DELTA", "delta": 4.0},
        {"type": "NOTE_OFF", "pitch": 67},
        {"type": "TIME_DELTA", "delta": 4.0},
        {"type": "NOTE_ON", "pitch": 68},
        {"type": "TIME_DELTA", "delta": 4.0},
        {"type": "NOTE_OFF", "pitch": 68},
    ]

    # Check if the output matches the expected result
    assert output == expected_output
