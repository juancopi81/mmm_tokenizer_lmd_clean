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

from typing import List, Dict

import music21
from music21 import meter, instrument
from music21.stream import Score

from source import logging
from source.preprocess.preprocessutilities import events_to_events_data


logger = logging.create_logger("music21lmd")


def preprocess_music21(m21_streams: List[Score]) -> Dict:
    split_index = int(0.8 * len(m21_streams))
    songs_train = m21_streams[:split_index]
    songs_valid = m21_streams[split_index:]

    logger.info(f"Using {len(songs_train)} for training.")
    logger.info(f"Using {len(songs_valid)} for validation.")

    songs_data_train = preprocess_music21_songs(songs_train, train=True)
    songs_data_valid = preprocess_music21_songs(songs_valid, train=False)

    return songs_data_train, songs_data_valid


def preprocess_music21_songs(songs, train):
    songs_data = []

    for song in songs:
        song_data = preprocess_music21_song(song, train)
        if song_data is not None:
            songs_data += [song_data]

    return songs_data


def preprocess_music21_song(song, train):
    # TODO add multiple measures

    # Skip songs with multiple measures
    meters = [
        meter.ratioString
        for meter in song.recurse().getElementsByClass(music21.meter.TimeSignature)
    ]
    meters = list(set(meters))

    if len(meters) > 1:
        logger.debug(f"Skipping because of multiple meters.")
        return None

    song_data = {}
    song_data["title"] = song.metadata.title
    song_data["number"] = song.metadata.number
    song_data["genre"] = str(song.metadata.getCustom("genre")[0]).upper()
    song_data["tracks"] = []

    # Add the time signature to the song
    first_part = song.parts[0]

    # Get time signature of first measure of first part
    first_measure_ts = first_part.recurse().getElementsByClass(meter.TimeSignature)[0]
    song_data["time_signature_numerator"] = first_measure_ts.numerator
    song_data["time_signature_denominator"] = first_measure_ts.denominator

    stream_by_parts = instrument.partitionByInstrument(song)

    for part in stream_by_parts.parts:
        part.makeRests(fillGaps=True, inPlace=True)

    for part_index, part in enumerate(stream_by_parts.parts):
        part_instrument = part.getInstrument()
        part.makeMeasures(inPlace=True)
        part.makeTies(inPlace=True)
        part.insert(0, part_instrument)
        track_data = preprocess_music21_part(part, part_index, train)
        song_data["tracks"] += [track_data]

    return song_data


def preprocess_music21_part(part, part_index, train):
    # Get the instrument for this part.
    instrument = part.getInstrument()
    is_drum = part.partName == "Percussion"
    # Create track_data dictionary.
    # Extract the MIDI program number, if available.
    # If no specific instrument is found, use a default value (e.g., 0 for Piano).
    track_data = {
        "name": part.partName,
        "number": part_index,
        "midi_program": "DRUMS"
        if part.partName == "Percussion"
        else instrument.midiProgram
        if isinstance(instrument.midiProgram, int)
        else 0,
        "bars": [],
    }

    # Iterate over measures.
    for measure_index in range(1, 100000):
        measure = part.measure(measure_index)
        if measure is None:
            break
        bar_data = preprocess_music21_measure(measure, train, is_drum)
        track_data["bars"] += [bar_data]

    return track_data


def preprocess_music21_measure(measure, train, is_drum):
    bar_data = {}
    bar_data["events"] = []
    # Create precussion mapper
    pm = music21.midi.percussion.PercussionMapper()
    events = []
    for event in measure.recurse():
        if is_drum:
            if isinstance(event, music21.note.Unpitched):
                # Catch instruments that are not in GM Percussion Map
                try:
                    per_pitch = pm.midiInstrumentToPitch(event._storedInstrument)
                except music21.midi.percussion.MIDIPercussionException:
                    default_perc = music21.instrument.SnareDrum()
                    per_pitch = pm.midiInstrumentToPitch(default_perc)

                events += [("NOTE_ON", per_pitch.midi, 4 * event.offset)]
                events += [
                    (
                        "NOTE_OFF",
                        per_pitch.midi,
                        4 * event.offset + 4 * event.duration.quarterLength,
                    )
                ]
            if isinstance(event, music21.percussion.PercussionChord):
                for note in event:
                    try:
                        per_pitch = pm.midiInstrumentToPitch(note._storedInstrument)
                    except music21.midi.percussion.MIDIPercussionException:
                        default_perc = music21.instrument.SnareDrum()
                        per_pitch = pm.midiInstrumentToPitch(default_perc)
                    events += [("NOTE_ON", per_pitch.midi, 4 * event.offset)]
                    events += [
                        (
                            "NOTE_OFF",
                            per_pitch.midi,
                            4 * event.offset + 4 * event.duration.quarterLength,
                        )
                    ]
            # print(f"Drums events {dir(event)} {event.offset}")
        # E.g. note.pitch.midi: 67, note.pitch: G4, note.offset: 0.0, note.duration.quarterLength: 1.0
        # Becomes [('NOTE_ON', 67, 0.0), ('NOTE_OFF', 67, 4.0)]
        # First check if it is note
        if isinstance(event, music21.note.Note):
            events += [("NOTE_ON", event.pitch.midi, 4 * event.offset)]
            events += [
                (
                    "NOTE_OFF",
                    event.pitch.midi,
                    4 * event.offset + 4 * event.duration.quarterLength,
                )
            ]

        # Do same as above in case notes are considered as chords
        if isinstance(event, music21.chord.Chord):
            for note in event:
                events += [("NOTE_ON", note.pitch.midi, 4 * event.offset)]
                events += [
                    (
                        "NOTE_OFF",
                        note.pitch.midi,
                        4 * event.offset + 4 * event.duration.quarterLength,
                    )
                ]

    bar_data["events"] += events_to_events_data(events)

    return bar_data
