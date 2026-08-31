"""
Logistic regression — minimal runnable example.

Companion code for README.md's "Simple example" section: the classic
hours-studied vs. pass/fail dataset (20 students), fit by unregularized
maximum likelihood so the coefficients match the hand-derived
Newton-Raphson/IRLS values documented in the README.

Run:
    python logistic_regression.py
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss


def fit_and_report(X: np.ndarray, y: np.ndarray, query_point: float) -> LogisticRegression:
    """Fit LogisticRegression on (X, y) and print coefficients, a prediction, and fit metrics."""
    # penalty=None recovers the plain, unregularized MLE fit (requires
    # scikit-learn >= 1.2; on older versions use penalty="none" instead).
    # Without this, scikit-learn's default L2 penalty would shrink the
    # coefficients slightly relative to the classical textbook values.
    model = LogisticRegression(penalty=None)
    model.fit(X, y)

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    print("Intercept:", model.intercept_[0])
    print("Coefficient:", model.coef_[0][0])
    print(f"P(pass) at {query_point} hours:", model.predict_proba([[query_point]])[0][1])
    print("Accuracy:", accuracy_score(y, predictions))
    print("Log loss:", log_loss(y, probabilities))

    return model


if __name__ == "__main__":
    # X must be two-dimensional: 20 observations, 1 feature (hours studied).
    X = np.array([[0.5], [0.75], [1.0], [1.25], [1.5], [1.75], [1.75], [2.0],
                  [2.25], [2.5], [2.75], [3.0], [3.25], [3.5], [4.0], [4.25],
                  [4.5], [4.75], [5.0], [5.5]])
    y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])

    fit_and_report(X, y, query_point=3)
