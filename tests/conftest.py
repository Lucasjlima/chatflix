import pytest
from models import Recommendation


@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
    """Garante que testes nunca toquem chaves reais."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("TMDB_API_KEY", "test-tmdb-key")


@pytest.fixture
def fake_recommendation():
    return Recommendation(
        title="O Iluminado",
        year=1980,
        justification="Atmosfera sombria e ritmo deliberadamente lento.",
    )


@pytest.fixture
def fake_tmdb_search_response():
    return {
        "results": [
            {"id": 694, "title": "O Iluminado", "release_date": "1980-05-23"}
        ]
    }


@pytest.fixture
def fake_tmdb_details_response():
    return {
        "id": 694,
        "title": "O Iluminado",
        "release_date": "1980-05-23",
        "poster_path": "/abc123.jpg",
        "overview": "Um escritor aceita ser zelador de um hotel isolado durante o inverno.",
        "vote_average": 8.4,
        "genres": [{"id": 27, "name": "Terror"}, {"id": 53, "name": "Suspense"}],
        "credits": {
            "crew": [
                {"job": "Director", "name": "Stanley Kubrick"},
                {"job": "Writer", "name": "Stephen King"},
            ]
        },
    }
