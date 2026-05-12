import requests

from models import MovieNotFound, TMDBError, MovieCard


TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
TIMEOUT = 5


class TMDBClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def search_movie(self, title: str, year: int | None) -> dict:
        params = {"api_key": self._api_key, "query": title, "language": "pt-BR"}
        if year is not None:
            params["year"] = year
        try:
            r = requests.get(f"{TMDB_BASE}/search/movie", params=params, timeout=TIMEOUT)
            r.raise_for_status()
        except requests.RequestException as e:
            raise TMDBError() from e

        results = r.json().get("results", [])
        if not results:
            raise MovieNotFound()
        return results[0]

    def get_movie_details(self, movie_id: int, justification: str) -> MovieCard:
        params = {
            "api_key": self._api_key,
            "language": "pt-BR",
            "append_to_response": "credits",
        }
        try:
            r = requests.get(f"{TMDB_BASE}/movie/{movie_id}", params=params, timeout=TIMEOUT)
            r.raise_for_status()
        except requests.RequestException as e:
            raise TMDBError() from e

        data = r.json()
        return self._to_movie_card(data, justification)

    @staticmethod
    def _to_movie_card(data: dict, justification: str) -> MovieCard:
        poster_path = data.get("poster_path")
        poster_url = f"{POSTER_BASE}{poster_path}" if poster_path else None

        release = data.get("release_date") or ""
        year = int(release[:4]) if release[:4].isdigit() else None

        vote = data.get("vote_average") or 0
        rating = f"{vote:.1f}" if vote else "Não disponível"

        crew = (data.get("credits") or {}).get("crew") or []
        directors = [c["name"] for c in crew if c.get("job") == "Director"]
        director = directors[0] if directors else "Não encontrado"

        synopsis = data.get("overview") or "Sinopse não encontrada"
        genres = [g["name"] for g in (data.get("genres") or [])]

        return MovieCard(
            title=data.get("title") or "",
            year=year,
            poster_url=poster_url,
            imdb_rating=rating,
            director=director,
            synopsis=synopsis,
            genres=genres,
            justification=justification,
        )
