"""Central config: loads .env and exposes settings as module-level constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

# No auth required at this dataset's volume — an app token just raises the anonymous rate limit.
SOCRATA_APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN") or None

NYCHA_DATASET_ID = "jr24-e7cr"
NYCHA_RESOURCE_URL = f"https://data.cityofnewyork.us/resource/{NYCHA_DATASET_ID}.json"

NYISO_PAL_URL_TEMPLATE = "http://mis.nyiso.com/public/csv/pal/{year_month}01pal_csv.zip"
NYISO_ZONE_NAME = "N.Y.C."
NYISO_START_YEAR_MONTH = "2010-01"

DUCKDB_PATH = PROJECT_ROOT / os.environ.get("DUCKDB_PATH", "data/nyc_electricity.duckdb")
MODEL_ARTIFACT_DIR = PROJECT_ROOT / "data" / "model_artifacts"
