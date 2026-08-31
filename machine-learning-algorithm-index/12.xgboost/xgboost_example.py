"""
XGBoost regressor — minimal runnable example.

Companion code for README.md's "Simple example" section: the same tiny
regression dataset used in ../11.gradient-boosting, run for 2 boosting
rounds. The gradients, Hessians, regularized leaf weights, and stage-by-stage
predictions were all hand-derived from XGBoost's closed-form optimal-leaf-
weight formula (w* = -G/(H+lambda)) before this script was written (see
README.md).

Requires: pip install xgboost

Run:
    python xgboost_example.py
"""

import numpy as np
from xgboost import XGBRegressor


def fit_and_report(X: np.ndarray, y: np.ndarray, n_estimators: int = 2) -> XGBRegressor:
    """Fit XGBRegressor on (X, y) and print predictions after every boosting stage."""
    # base_score set explicitly to the target mean (XGBoost otherwise
    # defaults base_score to 0.5 regardless of the target's scale — see
    # README's "base_score gotcha"); reg_lambda=1 is XGBoost's default,
    # shown explicitly since it's exactly what shrinks the leaf values in
    # the hand-derivation.
    model = XGBRegressor(
        n_estimators=n_estimators, learning_rate=1.0, max_depth=1,
        reg_lambda=1.0, base_score=float(np.mean(y)),
    )
    model.fit(X, y)

    for stage in range(1, n_estimators + 1):
        preds = model.predict(X, iteration_range=(0, stage))
        print(f"After stage {stage}:", preds)

    return model


if __name__ == "__main__":
    X = np.array([[1], [2], [3], [4], [5], [6]])
    y = np.array([1, 2, 6, 8, 4, 5])

    fit_and_report(X, y)
