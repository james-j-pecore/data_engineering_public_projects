"""Dagster assets: raw Spotify ingestion, then the full dbt DAG on top of it.

The raw ingestion asset's output keys are set to match the AssetKeys dagster-dbt
derives for each dbt source table (`[source_name, table_name]`), so Dagster wires
the dependency edges from raw ingestion into the staging models automatically —
no manual `deps=` wiring needed.
"""

from pathlib import Path

import dagster as dg
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

from src.extract import extract_all
from src.load import load_all
from src.spotify_client import SpotifyClient

RAW_TABLES = [
    "profile",
    "playlists",
    "playlist_tracks",
    "saved_tracks",
    "recently_played",
    "tracks",
    "albums",
    "artists",
]

dbt_project = DbtProject(
    project_dir=Path(__file__).parent.parent / "dbt_project",
    profiles_dir=Path(__file__).parent.parent / "dbt_project",
)
dbt_project.prepare_if_dev()


@dg.multi_asset(
    outs={table: dg.AssetOut(key=dg.AssetKey(["raw", table])) for table in RAW_TABLES},
    group_name="ingestion",
)
def raw_spotify_tables(context: dg.AssetExecutionContext):
    """One authenticated Spotify API pass, loaded into DuckDB's `raw` schema."""
    client = SpotifyClient()
    data = extract_all(client)
    load_all(data)

    for table in RAW_TABLES:
        row_count = 1 if table == "profile" else len(data[table])
        yield dg.Output(value=None, output_name=table, metadata={"row_count": row_count})


@dbt_assets(manifest=dbt_project.manifest_path)
def spotify_dbt_assets(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
