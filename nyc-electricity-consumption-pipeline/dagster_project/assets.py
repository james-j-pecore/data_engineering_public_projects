"""Dagster assets: raw ingestion (NYCHA + NYISO), the dbt DAG on top of it, and a
final model-training asset on top of the dbt marts.

The raw ingestion asset's output keys are set to match the AssetKeys
dagster-dbt derives for each dbt source table (`[source_name, table_name]`),
so Dagster wires the dependency edges from raw ingestion into the staging
models automatically — no manual `deps=` wiring needed there. The training
asset depends explicitly on the `mart_development_monthly` dbt model, since
it's a plain Python step downstream of the dbt DAG rather than a dbt model
itself.
"""

from pathlib import Path

import dagster as dg
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

from src.extract import extract_all
from src.load import load_all
from src.models.train import train_and_evaluate

RAW_TABLES = ["nycha_electric_bills", "nyiso_monthly_load"]

dbt_project = DbtProject(
    project_dir=Path(__file__).parent.parent / "dbt_project",
    profiles_dir=Path(__file__).parent.parent / "dbt_project",
)
dbt_project.prepare_if_dev()


@dg.multi_asset(
    outs={table: dg.AssetOut(key=dg.AssetKey(["raw", table])) for table in RAW_TABLES},
    group_name="ingestion",
)
def raw_nyc_electricity_tables(context: dg.AssetExecutionContext):
    """One pass over both source APIs, loaded into DuckDB's `raw` schema."""
    data = extract_all()
    load_all(data)

    for table in RAW_TABLES:
        yield dg.Output(value=None, output_name=table, metadata={"row_count": len(data[table])})


@dbt_assets(manifest=dbt_project.manifest_path)
def nyc_electricity_dbt_assets(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


@dg.asset(deps=[dg.AssetKey("mart_development_monthly")], group_name="modeling")
def model_leaderboard(context: dg.AssetExecutionContext):
    """Trains the regression suite and writes the leaderboard + best-model predictions."""
    train_and_evaluate()
