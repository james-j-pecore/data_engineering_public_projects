"""Panel feature engineering for one-step-ahead development-month kWh prediction.

The target is the current row's consumption_kwh; every feature is derived
from information available at the start of that month (lags, rolling means,
calendar position), so there's no leakage from the value being predicted.
"""

import duckdb
import numpy as np
import pandas as pd

from src import config

CATEGORICAL_COLUMNS = ["borough", "dominant_rate_class"]
NUMERIC_FEATURE_COLUMNS = ["lag_1_kwh", "lag_12_kwh", "rolling_mean_3_kwh", "avg_billing_days"]
TARGET_COLUMN = "consumption_kwh"


def load_panel() -> pd.DataFrame:
    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    df = con.execute("select * from main_marts.mart_development_monthly").fetchdf()
    con.close()
    return df


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Returns (X, y, metadata), dropping rows without a full 12-month lag history.

    `metadata` carries development_name/borough/revenue_month alongside X/y so
    predictions can be joined back to their source row without ever being fed
    into the model itself.
    """
    required = NUMERIC_FEATURE_COLUMNS + [TARGET_COLUMN]
    clean = df.dropna(subset=required).copy()

    clean["month_sin"] = np.sin(2 * np.pi * clean["month_of_year"] / 12)
    clean["month_cos"] = np.cos(2 * np.pi * clean["month_of_year"] / 12)

    encoded = pd.get_dummies(clean[CATEGORICAL_COLUMNS], dummy_na=True)
    X = pd.concat(
        [
            clean[NUMERIC_FEATURE_COLUMNS + ["month_sin", "month_cos"]].reset_index(drop=True),
            encoded.reset_index(drop=True),
        ],
        axis=1,
    )
    y = clean[TARGET_COLUMN].reset_index(drop=True)
    metadata = clean[["development_name", "borough", "revenue_month"]].reset_index(drop=True)

    return X, y, metadata
