import dagster as dg
from dagster_dbt import DbtCliResource

from dagster_project.assets import (
    dbt_project,
    model_leaderboard,
    nyc_electricity_dbt_assets,
    raw_nyc_electricity_tables,
)

defs = dg.Definitions(
    assets=[raw_nyc_electricity_tables, nyc_electricity_dbt_assets, model_leaderboard],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)},
)
