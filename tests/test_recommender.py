import pytest
from unittest.mock import MagicMock

from services.recommender import recommend
from models import (
    Recommendation,
    MovieCard,
    MovieNotFound,
    AIQuotaExceeded,
    OffTopicRequest,
    TMDBError,
)


def make_card():
    return MovieCard(
        title="O Iluminado", year=1980,
        poster_url="https://image.tmdb.org/t/p/w500/abc.jpg",
        imdb_rating="8.4", director="Stanley Kubrick",
        synopsis="...", genres=["Terror"], justification="Atmosfera sombria",
    )


def test_recommend_happy_path_returns_movie_card(mocker, fake_recommendation):
    gemini = MagicMock()
    gemini.suggest.return_value = fake_recommendation
    tmdb = MagicMock()
    tmdb.search_movie.return_value = {"id": 694, "title": "O Iluminado"}
    tmdb.get_movie_details.return_value = make_card()

    card = recommend("quero suspense", exclude_titles=[], gemini=gemini, tmdb=tmdb)

    assert isinstance(card, MovieCard)
    assert card.title == "O Iluminado"
    gemini.suggest.assert_called_once_with("quero suspense", [])
    tmdb.search_movie.assert_called_once_with("O Iluminado", 1980)
    tmdb.get_movie_details.assert_called_once_with(
        movie_id=694, justification=fake_recommendation.justification
    )
