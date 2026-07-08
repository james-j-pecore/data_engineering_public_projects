"""Loads extracted Spotify entities into DuckDB `raw` tables (full refresh each run).

Raw tables keep the source API shape untouched (id + the full JSON blob) — flattening
and typing happens in dbt staging models, not here. Full-refresh (CREATE OR REPLACE)
is idempotent by construction and appropriate at personal-library scale.
"""

import json

import duckdb
import pandas as pd

from src import config
from src.extract import extract_all
from src.spotify_client import SpotifyClient

RAW_SCHEMA = "raw"

# table_name -> function that derives a stable row id from the raw dict
ID_EXTRACTORS = {
    "playlists": lambda row: row["id"],
    "playlist_tracks": lambda row: f"{row['playlist_id']}:{row['track']['id']}:{row['added_at']}",
    "saved_tracks": lambda row: row["track"]["id"],
    "recently_played": lambda row: f"{row['track']['id']}:{row['played_at']}",
    "tracks": lambda row: row["id"],
    "albums": lambda row: row["id"],
    "artists": lambda row: row["id"],
}


def _write_table(con: duckdb.DuckDBPyConnection, table_name: str, ids: list[str], records: list[dict]) -> None:
    df = pd.DataFrame({"id": ids, "data": [json.dumps(r) for r in records]})
    df["loaded_at"] = pd.Timestamp.now(tz="UTC")
    con.execute(
        f"CREATE OR REPLACE TABLE {RAW_SCHEMA}.{table_name} AS "
        "SELECT id, data::JSON AS data, loaded_at FROM df"
    )
    print(f"Loaded {len(records)} rows into {RAW_SCHEMA}.{table_name}")


def _load_table(con: duckdb.DuckDBPyConnection, table_name: str, rows: list[dict]) -> None:
    id_fn = ID_EXTRACTORS[table_name]
    _write_table(con, table_name, [id_fn(row) for row in rows], rows)


def _load_profile(con: duckdb.DuckDBPyConnection, profile: dict) -> None:
    _write_table(con, "profile", [profile["id"]], [profile])


def load_all(data: dict) -> None:
    config.DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")

    _load_profile(con, data["profile"])
    for table_name in ID_EXTRACTORS:
        _load_table(con, table_name, data[table_name])

    con.close()


if __name__ == "__main__":
    client = SpotifyClient()
    load_all(extract_all(client))
