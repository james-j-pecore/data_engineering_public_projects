import dagster as dg
from dagster_dbt import DbtCliResource

from dagster_project.assets import dbt_project, raw_spotify_tables, spotify_dbt_assets

defs = dg.Definitions(
    assets=[raw_spotify_tables, spotify_dbt_assets],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)},
)
