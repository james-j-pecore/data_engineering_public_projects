"""
Naive Bayes classifier — minimal runnable example.

Companion code for README.md's "Simple example" section: the classic
"Play Tennis" dataset (Mitchell, Machine Learning, 1997), predicting whether
a Sunny/Cool/High-humidity/Strong-wind day is good for tennis. The expected
probabilities were hand-derived directly from Bayes' theorem and the raw
class-conditional frequencies (see README.md) before this script was written.

Run:
    python naive_bayes.py
"""

import numpy as np
from sklearn.naive_bayes import CategoricalNB
from sklearn.preprocessing import OrdinalEncoder


def fit_and_report(X_raw: list, y: list, query_raw: list) -> CategoricalNB:
    """Fit a CategoricalNB on (X_raw, y) and print class probabilities for query_raw."""
    encoder = OrdinalEncoder()
    X = encoder.fit_transform(X_raw)

    # alpha near 0 approximates the unsmoothed, hand-computed probabilities in
    # README.md; scikit-learn's default alpha=1.0 (Laplace smoothing) would
    # shift them slightly, which is what you want in practice, not just here.
    model = CategoricalNB(alpha=1e-10)
    model.fit(X, y)

    query = encoder.transform([query_raw])
    probabilities = model.predict_proba(query)[0]

    for class_name, p in zip(model.classes_, probabilities):
        print(f"P({class_name} | x) = {p:.3f}")
    print("Prediction:", model.predict(query)[0])

    return model


if __name__ == "__main__":
    # Columns: Outlook, Temperature, Humidity, Wind
    X_raw = [
        ["Sunny", "Hot", "High", "Weak"], ["Sunny", "Hot", "High", "Strong"],
        ["Overcast", "Hot", "High", "Weak"], ["Rain", "Mild", "High", "Weak"],
        ["Rain", "Cool", "Normal", "Weak"], ["Rain", "Cool", "Normal", "Strong"],
        ["Overcast", "Cool", "Normal", "Strong"], ["Sunny", "Mild", "High", "Weak"],
        ["Sunny", "Cool", "Normal", "Weak"], ["Rain", "Mild", "Normal", "Weak"],
        ["Sunny", "Mild", "Normal", "Strong"], ["Overcast", "Mild", "High", "Strong"],
        ["Overcast", "Hot", "Normal", "Weak"], ["Rain", "Mild", "High", "Strong"],
    ]
    y = ["No", "No", "Yes", "Yes", "Yes", "No", "Yes", "No",
         "Yes", "Yes", "Yes", "Yes", "Yes", "No"]

    fit_and_report(X_raw, y, query_raw=["Sunny", "Cool", "High", "Strong"])
