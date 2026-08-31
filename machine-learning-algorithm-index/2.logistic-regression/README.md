# Logistic Regression

## Overview

Logistic regression is a **supervised learning algorithm** used for **binary classification**: predicting which of two classes an observation belongs to (and, more usefully, the *probability* of that class membership).

Examples include predicting:

- Whether a customer will churn (yes/no)
- Whether an email is spam (spam/not spam)
- Whether a loan applicant will default (default/no default)
- Whether a student passes an exam given hours studied (pass/fail)

Despite the name, logistic regression is a **classification** algorithm, not a regression algorithm in the linear-regression sense — the "regression" is on the *log-odds* of the outcome, which is then mapped to a probability:

$$\hat{p} = \sigma(\beta_0 + \beta_1 x_1 + \cdots + \beta_p x_p), \qquad \sigma(z) = \frac{1}{1+e^{-z}}$$

Here:

- $\hat{p}$ is the predicted probability that the outcome equals 1.
- $\sigma$ is the **sigmoid (logistic) function**, which squashes any real number into $(0, 1)$.
- $x_1, \ldots, x_p$ are the input features, and $\beta_0, \ldots, \beta_p$ are learned coefficients, fit by maximizing the likelihood of the observed labels rather than by minimizing squared error.

---

## Intuition

Imagine plotting whether students passed an exam (0 or 1) against hours studied.

A straight line (plain linear regression) is a poor fit here — it can predict probabilities below 0 or above 1, which is meaningless, and it treats "definitely fails" and "definitely passes" the same as any other numeric distance. Logistic regression instead fits an **S-shaped curve**: probability rises smoothly from near 0 to near 1 as hours studied increases, without ever leaving the $(0, 1)$ range.

For one feature:

$$\hat{p} = \sigma(\beta_0 + \beta_1 x)$$

Fit to a small hours-studied-vs-pass dataset (see [Simple example](#simple-example)), the model comes out to approximately:

$$\hat{p} = \sigma(-4.08 + 1.50 \cdot \text{Hours Studied})$$

Interpretation:

- **Slope $\beta_1 > 0$:** more hours studied is associated with a higher predicted probability of passing.
- The curve crosses $\hat{p} = 0.5$ (the **decision boundary**) at $x = -\beta_0/\beta_1 \approx 2.71$ hours — below that, the model predicts "fail"; above it, "pass."

### From probability to a class label

The model itself outputs a probability. Turning that into a hard prediction requires a **threshold** (0.5 by default, but not required to be):

$$\hat{y} = \begin{cases} 1 & \hat{p} \geq \text{threshold} \\ 0 & \hat{p} < \text{threshold} \end{cases}$$

Moving the threshold trades off false positives against false negatives — this is what an ROC curve visualizes.

---

## Mathematical formulation

### Log-odds (logit)

Logistic regression models the **log-odds** of the positive class as a linear function of the features:

$$\log\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 x_1 + \cdots + \beta_p x_p$$

Solving for $p$ gives the sigmoid form shown in Overview. This is why the coefficients are linear in log-odds space even though the probability curve itself is nonlinear.

### Objective function

Unlike ordinary least squares, logistic regression is fit by **maximum likelihood estimation (MLE)**, not by minimizing squared error. Equivalently, it minimizes the **log loss** (binary cross-entropy):

$$\mathcal{L}(\boldsymbol{\beta}) = -\frac{1}{n}\sum_{i=1}^{n} \Big[ y_i \log(\hat{p}_i) + (1 - y_i)\log(1 - \hat{p}_i) \Big]$$

where $\hat{p}_i = \sigma(\beta_0 + \beta_1 x_{i1} + \cdots + \beta_p x_{ip})$.

There is no closed-form solution (unlike OLS's normal equations). In practice, this is solved numerically — scikit-learn's default solver (`lbfgs`) and classical **IRLS** (iteratively reweighted least squares, i.e., Newton-Raphson on the log-likelihood) both converge to the same MLE for well-behaved data.

### Regularized objective

By default, scikit-learn adds an L2 penalty to keep coefficients from growing unboundedly (which otherwise can happen when classes are close to perfectly separable):

$$\mathcal{L}_{\text{reg}}(\boldsymbol{\beta}) = \mathcal{L}(\boldsymbol{\beta}) + \frac{1}{C}\lVert \boldsymbol{\beta} \rVert_2^2$$

Smaller `C` means stronger regularization (shrinks coefficients toward zero); `C=np.inf` (or `penalty=None`) recovers the unregularized MLE.

### Odds ratios

Exponentiating a coefficient gives an **odds ratio**: $e^{\beta_1}$ is the multiplicative change in the odds of the positive class for a one-unit increase in $x_1$, holding other features fixed. This is the standard way logistic regression coefficients are reported in applied statistics (e.g., epidemiology, medicine).

---

## Typical hyperparameters

### `C`

Inverse of regularization strength (smaller = stronger regularization). Default is `1.0`.

```python
LogisticRegression(C=1.0)
```

Tuned via cross-validation in practice; too small underfits, too large risks unstable coefficients on separable data.

### `penalty`

Which regularization term to apply: `'l2'` (default), `'l1'` (drives some coefficients to exactly zero — feature selection), `'elasticnet'` (mix of both, requires `l1_ratio`), or `None` (no regularization, plain MLE).

```python
LogisticRegression(penalty="l2")
```

### `solver`

The optimization algorithm. `'lbfgs'` (default) works well for most cases; `'liblinear'` is a good choice for small datasets and L1 penalties; `'saga'` supports all penalties including elastic net and scales to large datasets.

```python
LogisticRegression(solver="lbfgs")
```

### `class_weight`

Reweights the loss to counteract class imbalance. `class_weight="balanced"` automatically weighs classes inversely proportional to their frequency.

```python
LogisticRegression(class_weight="balanced")
```

### `max_iter`

Maximum solver iterations. The default (`100`) is sometimes too low to reach convergence on unscaled features — a `ConvergenceWarning` usually means either scale the features (standardize them) or raise this value.

### Modeling choices that matter more than any single constructor argument

- Whether features are scaled (gradient-based solvers converge faster and more reliably on standardized features)
- Where the decision threshold is set (0.5 is a default, not a law — see [Intuition](#intuition))
- Whether to add interaction or polynomial terms to capture nonlinear decision boundaries
- How class imbalance is handled (`class_weight`, resampling, or an appropriate evaluation metric)

---

## Advantages

**Probabilistic output** — predicts a calibrated-ish probability, not just a class label, which is useful whenever the downstream decision needs a confidence level (e.g., ranking leads by likelihood to convert).

**Easy to interpret** — coefficients translate directly into odds ratios, a standard, well-understood way to communicate feature effects in applied statistics and many regulated domains (credit, healthcare).

**Fast to train and predict** — a convex optimization problem with a small number of parameters; scales comfortably to large datasets, especially with `saga` or `liblinear`.

**Strong, well-understood baseline** — like linear regression, it's usually the first model tried for a binary classification problem before reaching for anything more complex.

**Extends naturally to multiclass** — via one-vs-rest or a multinomial (softmax) formulation, without changing the underlying idea.

**Regularization built in** — L1/L2/elastic-net penalties are first-class options, not an afterthought, which helps when there are many correlated or noisy features.

---

## Limitations

**Assumes a linear decision boundary in log-odds space** — logistic regression can only separate classes with a linear boundary (in the original feature space, or whatever transformed feature space is fed in). Genuinely nonlinear class boundaries require feature engineering (polynomial/interaction terms) or a different model entirely.

**Perfect or near-perfect separation is a real failure mode** — if a feature (or combination of features) perfectly separates the classes, the unregularized MLE coefficients diverge toward infinity and the optimizer may fail to converge or report a warning. Regularization (`penalty="l2"`, finite `C`) is the usual fix, not just a tuning knob.

**Sensitive to unscaled features when using gradient-based solvers** — features on very different scales can slow or destabilize convergence; standardizing inputs is common practice.

**Sensitive to outliers and high-leverage points**, similar to linear regression, since a single unusual observation can noticeably shift the fitted boundary.

**Assumes independent observations** — like most classical statistical models, it doesn't natively account for correlated observations (repeated measures, clustered data) without extensions (e.g., GEE, mixed-effects logistic regression).

**Coefficients do not prove causation** — the same caveat as linear regression: a coefficient can reflect confounding, selection effects, or correlation rather than a causal mechanism.

**Class imbalance can distort default thresholding** — with a rare positive class, the default 0.5 threshold can produce a model that almost never predicts the minority class, even if its predicted probabilities are informative; threshold tuning or `class_weight` is often necessary.

---

## Simple example

The classic textbook example: predicting whether a student passes an exam from hours studied.

| Hours studied, $x$ | Pass, $y$ |
|---:|---:|
| 0.50 | 0 |
| 1.00 | 0 |
| 1.75 | 1 |
| 2.25 | 1 |
| 2.75 | 1 |
| 3.25 | 1 |
| 4.00 | 1 |
| 4.75 | 1 |
| 5.50 | 1 |

(the full 20-point dataset, including a few borderline hour values with mixed outcomes, is in [`logistic_regression.py`](logistic_regression.py))

Fitting an unregularized logistic regression (`penalty=None`) by maximum likelihood gives:

$$\hat{p} = \sigma(-4.0777 + 1.5046 \cdot \text{Hours Studied})$$

which puts the 50% decision boundary at $x = 4.0777 / 1.5046 \approx 2.71$ hours.

### Python example

See [`logistic_regression.py`](logistic_regression.py) for the runnable version:

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

X = np.array([[0.5], [0.75], [1.0], [1.25], [1.5], [1.75], [1.75], [2.0],
              [2.25], [2.5], [2.75], [3.0], [3.25], [3.5], [4.0], [4.25],
              [4.5], [4.75], [5.0], [5.5]])
y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])

# penalty=None recovers the plain, unregularized MLE fit so the coefficients
# match the classical hand-derived (IRLS/Newton-Raphson) values below.
model = LogisticRegression(penalty=None)
model.fit(X, y)

predictions = model.predict(X)
probabilities = model.predict_proba(X)[:, 1]

print("Intercept:", model.intercept_[0])
print("Coefficient:", model.coef_[0][0])
print("P(pass) at 3 hours:", model.predict_proba([[3]])[0][1])
print("Accuracy:", accuracy_score(y, predictions))
print("Log loss:", log_loss(y, probabilities))
```

Expected output (values independently verified via Newton-Raphson/IRLS, not just scikit-learn):

```text
Intercept: -4.0777
Coefficient: 1.5046
P(pass) at 3 hours: 0.6074
Accuracy: 0.8
Log loss: 0.4015
```

Accuracy is 0.8 (16/20) rather than 1.0 because — unlike the exact-fit linear regression example — this dataset has genuine class overlap around 1.75–3.5 hours: some students who studied similar amounts passed while others didn't, so no boundary separates the classes perfectly. That's realistic and expected, not a bug.

### Interpreting the metrics

**Accuracy** is the fraction of correct predictions at the chosen threshold (0.5 here). It can be misleading under class imbalance.

**Log loss** (cross-entropy) penalizes confident wrong predictions much more heavily than accuracy does — predicting $\hat{p}=0.99$ for a true negative costs far more log loss than predicting $\hat{p}=0.6$. Lower is better; a model that always predicts the base rate has a log loss you can use as a naive baseline for comparison.

---

## Resources

- [Scikit-learn `LogisticRegression` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) — implementation details, parameters, and solver notes.
- [Scikit-learn guide to linear models](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression) — mathematical formulation and regularization options.
- [Wikipedia: Logistic regression](https://en.wikipedia.org/wiki/Logistic_regression) — source of the classic hours-studied/pass-fail worked example used above, with the full derivation.
- [Penn State STAT 501](https://online.stat.psu.edu/stat501/) — course notes covering logistic regression alongside linear regression, assumptions, and diagnostics.
- [*The Elements of Statistical Learning*, Ch. 4](https://link.springer.com/book/10.1007/978-0-387-84858-7) — advanced reference on logistic regression within the broader classification framework.

### Core fact to retain

> Logistic regression predicts the probability of a binary outcome by fitting a linear model to the log-odds, then mapping it through the sigmoid function — fit by maximum likelihood, not by minimizing squared error.
