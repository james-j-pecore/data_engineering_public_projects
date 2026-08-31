"""
Random forest classifier — minimal runnable example.

Companion code for README.md's "Simple example" section, applied to the same
hours-studied-vs-pass dataset used in ../2.logistic-regression and
../3.decision-tree. Unlike those two examples, this one is NOT hand-verified
to an exact number: a random forest's fit depends on scikit-learn's internal
bootstrap/feature-subsampling RNG, which isn't practical to reproduce by hand.
See README.md's "Note on expected output" for what to expect qualitatively.

Run:
    python random_forest.py
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def fit_and_report(X: np.ndarray, y: np.ndarray, n_estimators: int = 200) -> RandomForestClassifier:
    """Fit a RandomForestClassifier on (X, y) and print training + out-of-bag accuracy."""
    model = RandomForestClassifier(n_estimators=n_estimators, oob_score=True, random_state=42)
    model.fit(X, y)

    predictions = model.predict(X)

    print("Training accuracy:", accuracy_score(y, predictions))
    print("Out-of-bag accuracy:", model.oob_score_)
    print("Feature importance (hours_studied):", model.feature_importances_[0])

    return model


if __name__ == "__main__":
    # X must be two-dimensional: 20 observations, 1 feature (hours studied).
    X = np.array([[0.5], [0.75], [1.0], [1.25], [1.5], [1.75], [1.75], [2.0],
                  [2.25], [2.5], [2.75], [3.0], [3.25], [3.5], [4.0], [4.25],
                  [4.5], [4.75], [5.0], [5.5]])
    y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])

    fit_and_report(X, y)
