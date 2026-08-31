"""
Decision tree classifier — minimal runnable example.

Companion code for README.md's "Simple example" section: a depth-1 tree
("decision stump") on the same hours-studied-vs-pass dataset used in
../2.logistic-regression, so the two algorithms can be compared directly.
The split threshold and accuracy below were hand-verified by exhaustively
scoring every candidate threshold's weighted Gini impurity (see README.md).

Run:
    python decision_tree.py
"""

import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score


def fit_and_report(X: np.ndarray, y: np.ndarray, feature_name: str) -> DecisionTreeClassifier:
    """Fit a depth-1 DecisionTreeClassifier on (X, y) and print its structure and accuracy."""
    model = DecisionTreeClassifier(max_depth=1, criterion="gini")
    model.fit(X, y)

    predictions = model.predict(X)

    print(export_text(model, feature_names=[feature_name]))
    print("Accuracy:", accuracy_score(y, predictions))

    return model


if __name__ == "__main__":
    # X must be two-dimensional: 20 observations, 1 feature (hours studied).
    X = np.array([[0.5], [0.75], [1.0], [1.25], [1.5], [1.75], [1.75], [2.0],
                  [2.25], [2.5], [2.75], [3.0], [3.25], [3.5], [4.0], [4.25],
                  [4.5], [4.75], [5.0], [5.5]])
    y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])

    fit_and_report(X, y, feature_name="hours_studied")
