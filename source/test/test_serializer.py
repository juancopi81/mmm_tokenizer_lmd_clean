import os
from pathlib import Path

from music21.stream.base import Score
from music21 import *

from source.preprocess.loading.serialization import Music21Serializer


def test_music21_serializer_load():
    test_folder_path = Path.home() / "mmm_tokenizer_lmd_clean/source/test/test_files"
    m21_serializer = Music21Serializer()
    m21_stream = m21_serializer.load(
        test_folder_path / '"Weird Al" Yankovic/Amish Paradise.mid'
    )
    assert m21_stream.metadata.title == "Amish Paradise"
    assert str(m21_stream.metadata.getCustom("genre")[0]) == "Other"
    assert type(m21_stream) == Score


def test_music21_serializer_dump():
    test_folder_path = Path.home() / "mmm_tokenizer_lmd_clean/source/test/test_files"
    m21_serializer = Music21Serializer()
    s = stream.Score()
    p = stream.Part()
    m = stream.Measure()
    m.append(note.Note())
    p.append(m)
    s.append(p)
    s.insert(0, metadata.Metadata())
    s.metadata.title = "title"
    s.metadata.composer = "composer"
    save_path = test_folder_path / "test_midi_file.mid"
    m21_serializer.dump(m21_stream=s, save_path=save_path)
    assert save_path.is_file() == True
    os.remove(save_path)
