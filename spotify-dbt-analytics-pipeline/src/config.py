"""Central config: loads .env and exposes settings as module-level constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SPOTIFY_CLIENT_ID = _require("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = _require("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback")

SPOTIFY_SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-library-read",
    "user-read-recently-played",
    "user-read-private",
]

DUCKDB_PATH = PROJECT_ROOT / os.environ.get("DUCKDB_PATH", "data/spotify.duckdb")
TOKEN_CACHE_PATH = PROJECT_ROOT / os.environ.get("TOKEN_CACHE_PATH", ".spotify_token_cache.json")
