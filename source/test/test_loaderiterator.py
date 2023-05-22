from pathlib import Path

import pytest

from source.preprocess.loading.loaderiterator import LoaderIterator
from source.preprocess.loading.serialization import Music21Serializer


@pytest.fixture
def loader_iterator():
    test_folder_path = Path.home() / "mmm_tokenizer_lmd_clean/source/test/test_files"
    paths = [
        Path(test_folder_path / '"Weird Al" Yankovic/Amish Paradise.mid'),
        Path(test_folder_path / '"Weird Al" Yankovic/Dare to Be Stupid.mid'),
        Path("non-existing-path"),
        Path(test_folder_path / '"Weird Al" Yankovic/Eat It.mid'),
        Path(test_folder_path / "ABBA/Chiquitita.1.mid"),
        Path(test_folder_path / "ABBA/Dance (While the Music Still Goes on).2.mid"),
        Path(test_folder_path / "ABBA/Dancing Queen.1.mid"),
        Path(test_folder_path / "Aerosmith/Crazy.1.mid"),
        Path(test_folder_path / "Aerosmith/Cryin'.mid"),
    ]
    return LoaderIterator(Music21Serializer(), 2, paths)


def test_loader_iterator_init():
    loader_iterator = LoaderIterator(Music21Serializer(), 3, "dummy_paths")
    assert type(loader_iterator) == LoaderIterator
    assert type(loader_iterator.serializer) == Music21Serializer
    assert loader_iterator.load_paths == "dummy_paths"
    assert loader_iterator.num_files_per_iteration == 3


def test_loop_through_loaded_data(loader_iterator):
    expected_data = [
        ["Amish Paradise", "Dare to Be Stupid"],
        [
            "Eat It",
        ],
        ["Chiquitita", "Dance (While the Music Still Goes on)"],
        ["Dancing Queen", "Crazy"],
        ["Cryin'"],
    ]

    for i, data in enumerate(loader_iterator):
        for j, stream in enumerate(data):
            assert stream.metadata.title == expected_data[i][j]


def test_loop_through_loaded_data_genre(loader_iterator):
    expected_data = [
        ["Other", "Other"],
        [
            "Other",
        ],
        ["Pop", "Pop"],
        ["Pop", "Rock"],
        ["Rock"],
    ]

    for i, data in enumerate(loader_iterator):
        for j, stream in enumerate(data):
            assert str(stream.metadata.getCustom("genre")[0]) == expected_data[i][j]


def test_iter(loader_iterator):
    assert loader_iterator._current_iteration == None
    iterator = iter(loader_iterator)
    assert loader_iterator._current_iteration == 0
    assert type(iterator) == LoaderIterator


def test_did_load_all_batches(loader_iterator):
    loader_iterator._current_iteration = 0
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 1
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 2
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 3
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 4
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 5
    assert loader_iterator._did_load_all_batches() == True

    loader_iterator.load_paths = [1, 2, 3, 4, 5, 6, 7]
    loader_iterator._current_iteration = 3
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 4
    assert loader_iterator._did_load_all_batches() == True

    loader_iterator.load_paths = [1, 2, 3, 4, 5, 6, 7, 8]
    assert loader_iterator._did_load_all_batches() == True

    loader_iterator.num_files_per_iteration = 3
    loader_iterator.load_paths = [1, 2, 3, 4, 5]
    loader_iterator._current_iteration = 0
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 1
    assert loader_iterator._did_load_all_batches() == False

    loader_iterator._current_iteration = 2
    assert loader_iterator._did_load_all_batches() == True


def test_set_current_iteration(loader_iterator):
    loader_iterator.set_current_iteration(5)
    assert loader_iterator._current_iteration == 5


def test_write_current_iteration(tmp_path, loader_iterator):
    # tmp_path is a pytest fixture that provides a temporary directory unique to the test invocation
    iteration_file = tmp_path / "iteration.txt"
    loader_iterator.set_current_iteration(10)
    loader_iterator.write_current_iteration(iteration_file)

    # Read the file and check the written iteration
    with open(iteration_file, "r") as f:
        written_iteration = int(f.read().strip())
    assert written_iteration == 10
