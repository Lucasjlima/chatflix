from models import Recommendation, MovieCard


def test_recommendation_holds_title_year_and_justification():
    rec = Recommendation(title="O Iluminado", year=1980,
                         justification="Atmosfera sombria")
    assert rec.title == "O Iluminado"
    assert rec.year == 1980
    assert rec.justification == "Atmosfera sombria"


def test_recommendation_year_can_be_none():
    rec = Recommendation(title="Filme Sem Ano", year=None, justification="X")
    assert rec.year is None


def test_movie_card_holds_all_required_fields():
    card = MovieCard(
        title="O Iluminado",
        year=1980,
        poster_url="https://image.tmdb.org/t/p/w500/abc.jpg",
        imdb_rating="8.4",
        director="Stanley Kubrick",
        synopsis="Um escritor...",
        genres=["Terror", "Suspense"],
        justification="Atmosfera sombria",
    )
    assert card.title == "O Iluminado"
    assert card.poster_url.startswith("https://")
    assert card.genres == ["Terror", "Suspense"]


def test_movie_card_poster_url_can_be_none():
    card = MovieCard(
        title="X", year=2020, poster_url=None, imdb_rating="N/A",
        director="N/A", synopsis="N/A", genres=[], justification="N/A",
    )
    assert card.poster_url is None
