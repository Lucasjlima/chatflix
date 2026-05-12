import logging
import time

from models import MovieCard
from services.gemini import GeminiClient
from services.tmdb import TMDBClient

log = logging.getLogger("chatflix.recommender")


def recommend(
    prompt: str,
    exclude_titles: list[str],
    gemini: GeminiClient,
    tmdb: TMDBClient,
) -> MovieCard:
    log.info("prompt=%r exclude_count=%d", prompt[:200], len(exclude_titles))

    t0 = time.perf_counter()
    rec = gemini.suggest(prompt, exclude_titles)
    log.info("gemini_latency_ms=%d title=%r year=%s",
             int((time.perf_counter() - t0) * 1000), rec.title, rec.year)

    t0 = time.perf_counter()
    match = tmdb.search_movie(rec.title, rec.year)
    log.info("tmdb_search_latency_ms=%d",
             int((time.perf_counter() - t0) * 1000))

    t0 = time.perf_counter()
    card = tmdb.get_movie_details(movie_id=match["id"], justification=rec.justification)
    log.info("tmdb_details_latency_ms=%d",
             int((time.perf_counter() - t0) * 1000))
    return card
