import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    gemini_key: str
    tmdb_key: str


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        gemini_key=os.environ.get("GEMINI_API_KEY", ""),
        tmdb_key=os.environ.get("TMDB_API_KEY", ""),
    )
