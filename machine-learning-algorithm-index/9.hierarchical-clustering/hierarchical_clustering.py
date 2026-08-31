"""
Agglomerative (hierarchical) clustering — minimal runnable example.

Companion code for README.md's "Simple example" section: five points on a
number line, single-linkage clustered down to 2 clusters. The merge order
and distances were hand-computed (see README.md) before this script was
written. Because n_clusters=2 is passed, scikit-learn stops building the
tree early (see AgglomerativeClustering's compute_full_tree behavior), so
only the first 3 of the 4 possible merges are recorded in distances_.

Run:
    python hierarchical_clustering.py
"""

import numpy as np
from sklearn.cluster import AgglomerativeClustering


def fit_and_report(X: np.ndarray, n_clusters: int = 2) -> AgglomerativeClustering:
    """Fit single-linkage AgglomerativeClustering on X and print labels + merge distances."""
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage="single", compute_distances=True)
    model.fit(X)

    print("Labels:", model.labels_)
    print("Merge distances:", sorted(model.distances_))

    return model


if __name__ == "__main__":
    X = np.array([[1], [2], [4], [7], [8]])  # A, B, C, D, E

    fit_and_report(X)
