"""Downloads NYISO's public monthly zonal load archives and rolls them up to one
NYC-zone row per month.

Each monthly zip (`{YYYYMM}01pal_csv.zip`) holds one CSV per day of 5-minute
"Present Actual Load" readings for every NYISO zone. We only need the NYC zone
("N.Y.C.") at monthly grain, so everything else is discarded in-memory rather
than persisted — no raw 5-minute data ever touches disk.
"""

import io
import zipfile
from datetime import date

import pandas as pd
import requests

from src import config


def _month_range(start_year_month: str, end_year_month: str) -> list[str]:
    start = date.fromisoformat(f"{start_year_month}-01")
    end = date.fromisoformat(f"{end_year_month}-01")

    months = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        months.append(f"{year:04d}{month:02d}")
        month = month + 1 if month < 12 else 1
        year = year if month != 1 else year + 1
    return months


def _fetch_month(year_month: str) -> pd.DataFrame | None:
    url = config.NYISO_PAL_URL_TEMPLATE.format(year_month=year_month)
    response = requests.get(url, timeout=60)
    if response.status_code == 404:
        return None  # month not yet published (e.g. current/future month)
    response.raise_for_status()

    frames = []
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        for name in archive.namelist():
            with archive.open(name) as f:
                df = pd.read_csv(f, usecols=["Time Stamp", "Name", "Load"])
            frames.append(df[df["Name"] == config.NYISO_ZONE_NAME])

    return pd.concat(frames, ignore_index=True) if frames else None


def extract_nyiso_monthly_load(end_year_month: str) -> list[dict]:
    """Returns one row per month: {year_month, avg_load_mw, max_load_mw}."""
    rows = []
    for year_month in _month_range(config.NYISO_START_YEAR_MONTH, end_year_month):
        month_df = _fetch_month(year_month)
        if month_df is None or month_df.empty:
            print(f"NYISO: no data for {year_month}, skipping")
            continue

        rows.append(
            {
                "year_month": f"{year_month[:4]}-{year_month[4:]}",
                "avg_load_mw": float(month_df["Load"].mean()),
                "max_load_mw": float(month_df["Load"].max()),
            }
        )
        print(f"NYISO: aggregated {year_month} ({len(month_df)} readings)")

    return rows
