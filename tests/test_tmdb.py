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


def test_get_movie_details_returns_movie_card(requests_mock, fake_tmdb_details_response):
    requests_mock.get(
        "https://api.themoviedb.org/3/movie/694",
        json=fake_tmdb_details_response,
    )
    client = TMDBClient(api_key="test")
    card = client.get_movie_details(movie_id=694, justification="por que combina")

    assert isinstance(card, MovieCard)
    assert card.title == "O Iluminado"
    assert card.year == 1980
    assert card.poster_url == "https://image.tmdb.org/t/p/w500/abc123.jpg"
    assert card.imdb_rating == "8.4"
    assert card.director == "Stanley Kubrick"
    assert card.synopsis.startswith("Um escritor")
    assert "Terror" in card.genres
    assert "Suspense" in card.genres
    assert card.justification == "por que combina"


def test_get_movie_details_no_poster_path_returns_none(requests_mock, fake_tmdb_details_response):
    data = {**fake_tmdb_details_response, "poster_path": None}
    requests_mock.get("https://api.themoviedb.org/3/movie/694", json=data)
    client = TMDBClient(api_key="test")
    card = client.get_movie_details(movie_id=694, justification="x")
    assert card.poster_url is None


def test_get_movie_details_no_director_returns_fallback(requests_mock, fake_tmdb_details_response):
    data = {**fake_tmdb_details_response,
            "credits": {"crew": [{"job": "Writer", "name": "Foo"}]}}
    requests_mock.get("https://api.themoviedb.org/3/movie/694", json=data)
    client = TMDBClient(api_key="test")
    card = client.get_movie_details(movie_id=694, justification="x")
    assert card.director == "Não encontrado"


def test_get_movie_details_zero_vote_average_returns_fallback(requests_mock, fake_tmdb_details_response):
    data = {**fake_tmdb_details_response, "vote_average": 0}
    requests_mock.get("https://api.themoviedb.org/3/movie/694", json=data)
    client = TMDBClient(api_key="test")
    card = client.get_movie_details(movie_id=694, justification="x")
    assert card.imdb_rating == "Não disponível"


def test_get_movie_details_empty_overview_returns_fallback(requests_mock, fake_tmdb_details_response):
    data = {**fake_tmdb_details_response, "overview": ""}
    requests_mock.get("https://api.themoviedb.org/3/movie/694", json=data)
    client = TMDBClient(api_key="test")
    card = client.get_movie_details(movie_id=694, justification="x")
    assert card.synopsis == "Sinopse não encontrada"


def test_get_movie_details_invalid_release_date_returns_year_none(requests_mock, fake_tmdb_details_response):
    data = {**fake_tmdb_details_response, "release_date": ""}
    requests_mock.get("https://api.themoviedb.org/3/movie/694", json=data)
    client = TMDBClient(api_key="test")
    card = client.get_movie_details(movie_id=694, justification="x")
    assert card.year is None


def test_get_movie_details_empty_genres_returns_empty_list(requests_mock, fake_tmdb_details_response):
    data = {**fake_tmdb_details_response, "genres": []}
    requests_mock.get("https://api.themoviedb.org/3/movie/694", json=data)
    client = TMDBClient(api_key="test")
    card = client.get_movie_details(movie_id=694, justification="x")
    assert card.genres == []
