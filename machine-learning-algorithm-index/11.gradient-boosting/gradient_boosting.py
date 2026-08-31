"""
Gradient boosting regressor — minimal runnable example.

Companion code for README.md's "Simple example" section: 2 boosting stages
with depth-1 stumps and learning_rate=1.0, on a tiny regression dataset.
The stage-by-stage residuals, split thresholds, and predictions were all
hand-computed via exhaustive threshold search before this script was
written (see README.md).

Run:
    python gradient_boosting.py
"""

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor


def fit_and_report(X: np.ndarray, y: np.ndarray, n_estimators: int = 2) -> GradientBoostingRegressor:
    """Fit GradientBoostingRegressor on (X, y) and print predictions after every stage."""
    # criterion="squared_error" (rather than scikit-learn's default
    # "friedman_mse") so each tree's split matches the plain
    # weighted-SSE-minimizing split used in the hand computation in README.md.
    model = GradientBoostingRegressor(
        n_estimators=n_estimators, learning_rate=1.0, max_depth=1, criterion="squared_error"
    )
    model.fit(X, y)

    for i, pred in enumerate(model.staged_predict(X), start=1):
        print(f"After stage {i}:", pred)

    return model


if __name__ == "__main__":
    X = np.array([[1], [2], [3], [4], [5], [6]])
    y = np.array([1, 2, 6, 8, 4, 5])

    fit_and_report(X, y)
