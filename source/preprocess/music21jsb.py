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
import music21
from music21 import corpus
from music21 import converter
from music21 import meter, tempo
from music21 import metadata
from source import logging
from source.preprocess.preprocessutilities import events_to_events_data

logger = logging.create_logger("music21jsb")

def preprocess_music21(midi_source=""):
    
    logger.info("Loading songs...")
    if midi_source == "":
        songs = load_jsb_chorales()
    else:
        songs = load_custom_dir(midi_source)
    logger.info(f"Got {len(songs)} songs.")
    
    split_index = int(0.8*len(songs))
    songs_train = songs[:split_index]
    songs_valid = songs[split_index:]
    
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
    meters = [meter.ratioString for meter in song.recurse().getElementsByClass(music21.meter.TimeSignature)]
    meters = list(set(meters))
    if len(meters) != 1:
        logger.debug(f"Skipping because of multiple meters.")
        return None
    
    song_data = {}
    song_data["title"] = song.metadata.title
    song_data["number"] = song.metadata.number
    song_data["tracks"] = []
    
    # Add the time signature to the song
    first_part = song.parts[0]
    
    # Get time signature of first measure of first part
    first_measure_ts = first_part.recurse().getElementsByClass(meter.TimeSignature)[0]
    song_data["time_signature_numerator"] = first_measure_ts.numerator
    song_data["time_signature_denominator"] = first_measure_ts.denominator
    
    # Get tempo of first measure of first part
    first_measure_bpm = first_part.recurse().getElementsByClass(tempo.MetronomeMark)[0]
    song_data["bpm"] = int(first_measure_bpm.getQuarterBPM())
    
    for part_index, part in enumerate(song.parts):
        track_data = preprocess_music21_part(part, part_index, train)
        song_data["tracks"] += [track_data]

    return song_data

def preprocess_music21_part(part, part_index, train):
    
    track_data = {}
    track_data["name"] = part.partName
    track_data["number"] = part_index
    track_data["bars"] = []

    for measure_index in range(1, 1000):
        measure = part.measure(measure_index)
        if measure is None:
            break

        bar_data = preprocess_music21_measure(measure, train)
        track_data["bars"] += [bar_data]
    
    return track_data

def preprocess_music21_measure(measure, train):
    
    bar_data = {}
    bar_data["events"] = []
    
    events = []
    for event in measure.recurse():
        # E.g. note.pitch.midi: 67, note.pitch: G4, note.offset: 0.0, note.duration.quarterLength: 1.0
        # Becomes [('NOTE_ON', 67, 0.0), ('NOTE_OFF', 67, 4.0)]
        # First check if it is note
        if isinstance(event, music21.note.Note):
            events += [("NOTE_ON", event.pitch.midi, 4 * event.offset)]
            events += [("NOTE_OFF", event.pitch.midi, 4 * event.offset + 4 * event.duration.quarterLength)]
        
        # Do same as above in case notes are considered as chords
        if isinstance(event, music21.chord.Chord):
            for note in event:
                events += [("NOTE_ON", note.pitch.midi, 4 * event.offset)]
                events += [("NOTE_OFF", note.pitch.midi, 4 * event.offset + 4 * event.duration.quarterLength)]
        
    bar_data["events"] += events_to_events_data(events)
    
    return bar_data

def load_jsb_chorales():
    # Return chorales from music21 corpus as list
    return list(corpus.chorales.Iterator())

def load_custom_dir(save_dir):
    
    # This will be returned
    originalScores = []
    
    # List of midi files in custom dir
    songList = os.listdir(save_dir)
    
    # Load and make list of stream objects
    for idx, song in enumerate(songList):
        # Check that song is a MIDI file
        if song.endswith(".mid") or song.endswith(".midi"):
            score = converter.parse(save_dir + song, quantizePost=False)
            score.insert(0, metadata.Metadata())
            score.metadata.title = song.split(".")[0]
            score.metadata.number = idx
            originalScores.append(score)
            
    return originalScores