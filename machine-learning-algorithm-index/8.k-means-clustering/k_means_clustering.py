"""
K-means clustering — minimal runnable example.

Companion code for README.md's "Simple example" section: six points forming
two visible groups, clustered with centroids initialized at two of the
actual data points. Convergence (after one update) and the final centroids
were hand-computed via Lloyd's algorithm before this script was written
(see README.md).

Run:
    python k_means_clustering.py
"""

import numpy as np
from sklearn.cluster import KMeans


def fit_and_report(X: np.ndarray, init: np.ndarray) -> KMeans:
    """Fit KMeans on X from a fixed initialization and print centroids/labels/inertia."""
    # n_init=1 because init is an explicit array, not a random-restart strategy.
    model = KMeans(n_clusters=len(init), init=init, n_init=1, random_state=42)
    model.fit(X)

    print("Cluster centers:", model.cluster_centers_)
    print("Labels:", model.labels_)
    print("Inertia:", model.inertia_)

    return model


if __name__ == "__main__":
    X = np.array([[1, 1], [1, 2], [2, 1], [8, 8], [8, 9], [9, 8]])
    initial_centroids = np.array([[1, 1], [8, 8]])

    fit_and_report(X, initial_centroids)
