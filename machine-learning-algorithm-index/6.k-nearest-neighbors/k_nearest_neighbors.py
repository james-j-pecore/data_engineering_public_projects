"""
K-nearest neighbors classifier — minimal runnable example.

Companion code for README.md's "Simple example" section: two well-separated
2-D clusters and a query point whose distances to its 3 nearest neighbors
were hand-computed via Euclidean distance (see README.md).

Run:
    python k_nearest_neighbors.py
"""

import numpy as np
from sklearn.neighbors import KNeighborsClassifier


def fit_and_report(X: np.ndarray, y: np.ndarray, query: np.ndarray, k: int = 3) -> KNeighborsClassifier:
    """Fit a KNeighborsClassifier on (X, y) and report the neighbors and prediction for query."""
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X, y)

    distances, indices = model.kneighbors(query)

    print(f"Distances to {k} nearest neighbors:", distances[0])
    print(f"Prediction for {query[0].tolist()}:", model.predict(query)[0])

    return model


if __name__ == "__main__":
    X = np.array([[1, 2], [2, 3], [2, 1], [3, 2],
                  [6, 5], [7, 7], [8, 6], [6, 8]])
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])

    fit_and_report(X, y, query=np.array([[5, 5]]), k=3)
