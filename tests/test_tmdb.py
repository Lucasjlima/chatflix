import pytest
import requests
from services.tmdb import TMDBClient
from models import MovieNotFound, TMDBError, MovieCard


def test_search_movie_returns_first_match_id_and_title(requests_mock, fake_tmdb_search_response):
    requests_mock.get(
        "https://api.themoviedb.org/3/search/movie",
        json=fake_tmdb_search_response,
    )
    client = TMDBClient(api_key="test")
    result = client.search_movie("O Iluminado", year=1980)
    assert result["id"] == 694
    assert result["title"] == "O Iluminado"


def test_search_movie_with_year_none_still_works(requests_mock, fake_tmdb_search_response):
    requests_mock.get(
        "https://api.themoviedb.org/3/search/movie",
        json=fake_tmdb_search_response,
    )
    client = TMDBClient(api_key="test")
    result = client.search_movie("O Iluminado", year=None)
    assert result["id"] == 694


def test_search_movie_no_results_raises_movie_not_found(requests_mock):
    requests_mock.get(
        "https://api.themoviedb.org/3/search/movie",
        json={"results": []},
    )
    client = TMDBClient(api_key="test")
    with pytest.raises(MovieNotFound):
        client.search_movie("Filme Inexistente XYZ", year=2099)
