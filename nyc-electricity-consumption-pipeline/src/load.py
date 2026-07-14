"""Loads extracted records into DuckDB `raw` tables (full refresh each run).

Raw tables keep the source shape untouched (id + the full JSON blob) — typing
and casting happens in dbt staging models, not here. Full-refresh
(CREATE OR REPLACE) is idempotent by construction and appropriate at this
dataset's scale (~554K NYCHA bill rows, ~190 NYISO monthly rows).
"""

import json

import duckdb
import pandas as pd

from src import config
from src.extract import extract_all

RAW_SCHEMA = "raw"

# table_name -> function that derives a stable row id from the raw dict + its
# position in the extracted list. NYCHA's umis_bill_id is a billing-account id
# shared by every meter/rate-class line on the same bill, so it repeats within
# a revenue month (~23K collisions observed) — the index makes each row unique.
ID_EXTRACTORS = {
    "nycha_electric_bills": lambda row, idx: f"{row['umis_bill_id']}-{idx}",
    "nyiso_monthly_load": lambda row, idx: row["year_month"],
}


def _write_table(con: duckdb.DuckDBPyConnection, table_name: str, ids: list[str], records: list[dict]) -> None:
    df = pd.DataFrame({"id": ids, "data": [json.dumps(r) for r in records]})
    df["loaded_at"] = pd.Timestamp.now(tz="UTC")
    con.execute(
        f"CREATE OR REPLACE TABLE {RAW_SCHEMA}.{table_name} AS "
        "SELECT id, data::JSON AS data, loaded_at FROM df"
    )
    print(f"Loaded {len(records)} rows into {RAW_SCHEMA}.{table_name}")


def load_all(data: dict) -> None:
    config.DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")

    for table_name, id_fn in ID_EXTRACTORS.items():
        rows = data[table_name]
        _write_table(con, table_name, [id_fn(row, i) for i, row in enumerate(rows)], rows)

    con.close()


if __name__ == "__main__":
    load_all(extract_all())
