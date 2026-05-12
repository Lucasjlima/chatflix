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


class RecommendError(Exception):
    user_message: str = ""


class MovieNotFound(RecommendError):
    user_message = "Não foi possível encontrar um filme correspondente."


class AIQuotaExceeded(RecommendError):
    user_message = "Ocorreu um erro nas configurações internas da IA."


class AIInternalError(RecommendError):
    user_message = "Ocorreu um erro nas configurações internas da IA."


class TMDBError(RecommendError):
    user_message = "Ocorreu um erro interno na API."


class OffTopicRequest(RecommendError):
    user_message = "Meu objetivo é apenas recomendar filmes com base nas suas preferências."
