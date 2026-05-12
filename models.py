from dataclasses import dataclass


@dataclass(frozen=True)
class Recommendation:
    title: str
    year: int | None
    justification: str


@dataclass(frozen=True)
class MovieCard:
    title: str
    year: int | None
    poster_url: str | None
    imdb_rating: str
    director: str
    synopsis: str
    genres: list[str]
    justification: str
