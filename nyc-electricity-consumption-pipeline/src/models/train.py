"""Trains the regression suite on a time-based split, evaluates each model,
and writes a leaderboard + best-model predictions into DuckDB, plus saves the
best estimator as a joblib artifact.

Time-based split (not random shuffle): the most recent HOLDOUT_MONTHS of
history is held out as the test set, since shuffling a time series would
leak future information into training.
"""

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src import config
from src.models.features import build_features, load_panel
from src.models.registry import MODEL_REGISTRY

HOLDOUT_MONTHS = 12
HIT_RATE_TOLERANCE = 0.10


def time_based_split(metadata: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    cutoff = metadata["revenue_month"].max() - pd.DateOffset(months=HOLDOUT_MONTHS)
    is_test = metadata["revenue_month"] > cutoff
    return ~is_test, is_test


def evaluate(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    with np.errstate(divide="ignore", invalid="ignore"):
        pct_error = np.abs((y_pred - y_true) / y_true)

    # A handful of developments report 0 kWh in a given month (vacant/unmetered
    # periods) — sklearn's mean_absolute_percentage_error floors that division
    # at a tiny epsilon instead of excluding it, so a single such row inflates
    # the mean by ~1e15x. Excluding non-finite terms keeps MAPE meaningful.
    finite_pct_error = pct_error[np.isfinite(pct_error)]

    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mape": float(np.mean(finite_pct_error)) * 100,
        "r2": float(r2_score(y_true, y_pred)),
        "hit_rate_10pct": float(np.mean(pct_error <= HIT_RATE_TOLERANCE)) * 100,
    }


def train_and_evaluate() -> None:
    df = load_panel()
    X, y, metadata = build_features(df)
    train_mask, test_mask = time_based_split(metadata)

    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    leaderboard_rows = []
    best_name, best_rmse, best_model, best_predictions = None, np.inf, None, None

    for name, model in MODEL_REGISTRY.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        metrics = evaluate(y_test.to_numpy(), y_pred)
        metrics["model_name"] = name
        leaderboard_rows.append(metrics)
        print(
            f"{name}: RMSE={metrics['rmse']:.1f} MAE={metrics['mae']:.1f} "
            f"R2={metrics['r2']:.3f} hit_rate={metrics['hit_rate_10pct']:.1f}%"
        )

        if metrics["rmse"] < best_rmse:
            best_name, best_rmse, best_model = name, metrics["rmse"], model
            best_predictions = metadata[test_mask].copy()
            best_predictions["actual_kwh"] = y_test.to_numpy()
            best_predictions["predicted_kwh"] = y_pred

    leaderboard = pd.DataFrame(leaderboard_rows).sort_values("rmse").reset_index(drop=True)
    leaderboard["is_best"] = leaderboard["model_name"] == best_name

    config.MODEL_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, config.MODEL_ARTIFACT_DIR / f"{best_name}.joblib")

    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    con.execute("CREATE OR REPLACE TABLE analytics.model_leaderboard AS SELECT * FROM leaderboard")
    con.execute("CREATE OR REPLACE TABLE analytics.model_predictions AS SELECT * FROM best_predictions")
    con.close()

    print(f"Best model: {best_name} (RMSE={best_rmse:.1f})")


if __name__ == "__main__":
    train_and_evaluate()
