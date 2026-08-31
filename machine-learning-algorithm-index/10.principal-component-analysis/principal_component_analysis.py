"""
Principal component analysis — minimal runnable example.

Companion code for README.md's "Simple example" section: the classic
10-point PCA tutorial dataset (Smith, 2002). The covariance matrix,
eigenvalues, first eigenvector, and first point's projection were all
hand-computed via the 2x2 symmetric-matrix eigenvalue formula before this
script was written (see README.md).

Run:
    python principal_component_analysis.py
"""

import numpy as np
from sklearn.decomposition import PCA


def fit_and_report(X: np.ndarray, n_components: int = 2) -> PCA:
    """Fit PCA on X and print explained variance, the first component, and its top projection."""
    model = PCA(n_components=n_components)
    X_transformed = model.fit_transform(X)

    print("Explained variance ratio:", model.explained_variance_ratio_)
    print("First principal component direction:", model.components_[0])
    print("First data point's PC1 score:", X_transformed[0, 0])

    return model


if __name__ == "__main__":
    X = np.array([
        [2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], [3.1, 3.0],
        [2.3, 2.7], [2.0, 1.6], [1.0, 1.1], [1.5, 1.6], [1.1, 0.9],
    ])

    fit_and_report(X)
