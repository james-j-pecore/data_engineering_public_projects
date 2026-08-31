"""
Support vector machine — minimal runnable example.

Companion code for README.md's "Simple example" section: a linearly
separable 1-D toy dataset whose maximum-margin boundary (w=1, b=-2) and
support vectors (x=1, x=3) were hand-derived by solving the two support
vector equality constraints directly (see README.md).

Run:
    python support_vector_machine.py
"""

import numpy as np
from sklearn.svm import SVC


def fit_and_report(X: np.ndarray, y: np.ndarray) -> SVC:
    """Fit a linear-kernel SVC on (X, y) and print the boundary and support vectors."""
    # Large C approximates a hard margin (heavily penalizes any violation),
    # matching the by-hand hard-margin solution since this data is linearly
    # separable with room to spare.
    model = SVC(kernel="linear", C=1000)
    model.fit(X, y)

    print("Coefficient (w):", model.coef_[0][0])
    print("Intercept (b):", model.intercept_[0])
    print("Support vectors:", model.support_vectors_.ravel())

    return model


if __name__ == "__main__":
    X = np.array([[0], [1], [3], [4]])
    y = np.array([-1, -1, 1, 1])

    fit_and_report(X, y)
