import requests

from models import MovieNotFound, TMDBError


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
