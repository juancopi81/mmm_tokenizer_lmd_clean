from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd
from music21 import converter
from music21.stream.base import Score
from music21 import metadata


class Serializer(ABC):
    """Interface for concrete Seralization methods."""

    @abstractmethod
    def dump(self, obj: Any, save_path: Path) -> None:
        pass

    @abstractmethod
    def load(self, load_path: Path) -> Any:
        pass


class Music21Serializer(Serializer):

    """Saves and loads a Music21 file. It's a concrete serializer."""

    def __init__(
        self,
        save_format: str = "midi",
        genre_file: Path = "source/preprocess/loading/lmd_genres.csv",
    ) -> None:
        self.save_format = save_format

        # Read the genre CSV file into a DataFrame.
        self.genre_df = pd.read_csv(genre_file)

    def dump(self, m21_stream: Score, save_path: Path) -> None:
        m21_stream.write(fmt=self.save_format, fp=save_path, quantizePost=False)

    def load(self, load_path: Path) -> Score:
        # Extract the artist name from the load_path.
        artist_name = load_path.parts[-2]
        print(load_path.parts)

        # Search for the artist name in the DataFrame.
        genre_row = self.genre_df.loc[self.genre_df["Artist"] == artist_name]

        # Get the genre if the artist was found.
        genre = genre_row["Genre_ChatGPT"].values[0] if not genre_row.empty else None
        print(f"genre: {genre}, artist: {artist_name}")

        # Load the score from the file.
        stream = converter.parse(load_path, quantizePost=False)
        stream.insert(0, metadata.Metadata())

        # Set metadata
        stream.metadata.title = load_path.parts[-1].split(".")[0]
        if genre is not None:
            print("genre")
            stream.metadata.setCustom("genre", genre)

        return stream