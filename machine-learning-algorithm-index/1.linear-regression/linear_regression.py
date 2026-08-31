"""
Ordinary least squares linear regression — minimal runnable example.

Companion code for README.md's "Simple example" section: fits y = 1 + 2x on a
toy dataset that lies exactly on a line, then reports the fitted coefficients,
residuals, and the two most common regression metrics (MSE, R^2).

Run:
    python linear_regression.py
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


def fit_and_report(X: np.ndarray, y: np.ndarray, query_point: float) -> LinearRegression:
    """Fit LinearRegression on (X, y) and print coefficients, a prediction, and fit metrics."""
    model = LinearRegression()
    model.fit(X, y)

    predictions = model.predict(X)
    residuals = y - predictions

    print("Intercept:", model.intercept_)
    print("Coefficient:", model.coef_[0])
    print(f"Prediction for x={query_point}:", model.predict([[query_point]])[0])
    print("Residuals:", residuals)
    print("MSE:", mean_squared_error(y, predictions))
    print("R^2:", r2_score(y, predictions))

    return model


if __name__ == "__main__":
    # X must be two-dimensional: 4 observations, 1 feature.
    X = np.array([[1], [2], [3], [4]])
    y = np.array([3, 5, 7, 9])  # lies exactly on y = 1 + 2x

    fit_and_report(X, y, query_point=5)
