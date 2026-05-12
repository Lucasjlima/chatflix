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


def test_recommend_propagates_off_topic_without_calling_tmdb(mocker):
    gemini = MagicMock()
    gemini.suggest.side_effect = OffTopicRequest()
    tmdb = MagicMock()

    with pytest.raises(OffTopicRequest):
        recommend("qual a capital da França?", exclude_titles=[],
                  gemini=gemini, tmdb=tmdb)

    tmdb.search_movie.assert_not_called()
    tmdb.get_movie_details.assert_not_called()


def test_recommend_propagates_quota_exceeded_without_calling_tmdb(mocker):
    gemini = MagicMock()
    gemini.suggest.side_effect = AIQuotaExceeded()
    tmdb = MagicMock()

    with pytest.raises(AIQuotaExceeded):
        recommend("x", exclude_titles=[], gemini=gemini, tmdb=tmdb)

    tmdb.search_movie.assert_not_called()


def test_recommend_propagates_movie_not_found(mocker, fake_recommendation):
    gemini = MagicMock()
    gemini.suggest.return_value = fake_recommendation
    tmdb = MagicMock()
    tmdb.search_movie.side_effect = MovieNotFound()

    with pytest.raises(MovieNotFound):
        recommend("x", exclude_titles=[], gemini=gemini, tmdb=tmdb)

    tmdb.get_movie_details.assert_not_called()


def test_recommend_propagates_tmdb_error(mocker, fake_recommendation):
    gemini = MagicMock()
    gemini.suggest.return_value = fake_recommendation
    tmdb = MagicMock()
    tmdb.search_movie.side_effect = TMDBError()

    with pytest.raises(TMDBError):
        recommend("x", exclude_titles=[], gemini=gemini, tmdb=tmdb)


def test_recommend_passes_exclude_titles_to_gemini(mocker, fake_recommendation):
    gemini = MagicMock()
    gemini.suggest.return_value = fake_recommendation
    tmdb = MagicMock()
    tmdb.search_movie.return_value = {"id": 694, "title": "X"}
    tmdb.get_movie_details.return_value = make_card()

    recommend("x", exclude_titles=["A", "B"], gemini=gemini, tmdb=tmdb)
    gemini.suggest.assert_called_once_with("x", ["A", "B"])
