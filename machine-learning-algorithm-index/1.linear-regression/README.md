# Linear Regression

## Overview

Linear regression is a **supervised learning algorithm** used to predict a **continuous numerical outcome**.

Examples include predicting:

- Salary from years of experience
- House price from size and location
- Monthly sales from advertising expenditure
- Delivery time from distance and order volume

The model represents the target as a weighted sum of the input features:

$$\hat{y} = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \cdots + \beta_p x_p$$

Here:

- $\hat{y}$ is the predicted outcome.
- $x_1, \ldots, x_p$ are the input features.
- $\beta_0$ is the intercept.
- $\beta_1, \ldots, \beta_p$ are learned coefficients.

Standard ordinary least squares (OLS) linear regression chooses the coefficients that minimize the sum of squared prediction errors.

---

## Intuition

Imagine plotting employee salaries against years of experience.

The points will probably not form a perfect line, but they may show an upward pattern. Linear regression attempts to draw the line that best summarizes that relationship.

For one feature:

$$\hat{y} = \beta_0 + \beta_1 x$$

Suppose the fitted model is:

$$\widehat{\text{Salary}} = 45{,}000 + 4{,}000 \cdot (\text{Years of Experience})$$

Interpretation:

- **Intercept $\beta_0 = 45{,}000$:** predicted salary at zero years of experience.
- **Slope $\beta_1 = 4{,}000$:** each additional year of experience is associated with a predicted \$4,000 increase in salary.

The word **associated** matters. A regression coefficient does not automatically establish causation.

### Residuals

For every observation:

$$e_i = y_i - \hat{y}_i$$

where:

- $y_i$ is the actual value.
- $\hat{y}_i$ is the predicted value.
- $e_i$ is the residual, or prediction error.

A positive residual means the model predicted too low. A negative residual means it predicted too high.

---

## Mathematical formulation

### Model

For observation $i$:

$$y_i = \beta_0 + \beta_1 x_{i1} + \cdots + \beta_p x_{ip} + \epsilon_i$$

The error term $\epsilon_i$ represents variation that the included features do not explain.

In matrix form:

$$\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}$$

### Objective function

Ordinary least squares minimizes the **residual sum of squares**:

$$RSS = \sum_{i=1}^{n} (y_i - \hat{y}_i)^2$$

Equivalently:

$$\hat{\boldsymbol{\beta}} = \arg\min_{\boldsymbol{\beta}} \lVert \mathbf{y} - \mathbf{X}\boldsymbol{\beta} \rVert_2^2$$

Squaring the errors:

1. Prevents positive and negative errors from canceling out.
2. Penalizes large errors more heavily.
3. Produces a mathematically convenient (differentiable, convex) optimization problem.

Under suitable conditions (full column rank $\mathbf{X}$), the closed-form OLS estimate is:

$$\hat{\boldsymbol{\beta}} = (\mathbf{X}^{T}\mathbf{X})^{-1}\mathbf{X}^{T}\mathbf{y}$$

In practice, numerical libraries (including scikit-learn) generally use more numerically stable methods, such as QR or SVD decomposition, rather than directly computing this inverse.

### Common assumptions for statistical inference

When linear regression is used to estimate confidence intervals, hypothesis tests, and coefficient significance, the classical assumptions become important:

- **Linearity:** the expected target is linear in the coefficients.
- **Independence:** observations or errors are independent.
- **Homoscedasticity:** residual variance is approximately constant across fitted values.
- **No perfect multicollinearity:** no feature is an exact linear combination of the others.
- **Normally distributed errors:** mainly needed for classical small-sample inference, not simply to fit the model.

These assumptions are stricter than what is required to use the model purely for prediction.

---

## Typical hyperparameters

Ordinary least squares has relatively few true hyperparameters. Most of its behavior comes from the data and feature design, not from tuning.

### `fit_intercept`

Determines whether the model learns an intercept term.

```python
LinearRegression(fit_intercept=True)
```

Usually leave this as `True`. Set it to `False` only when the data has already been centered appropriately, or theory requires the regression line to pass through the origin.

### `positive`

Restricts coefficients to nonnegative values.

```python
LinearRegression(positive=True)
```

Useful when negative effects would be impossible or nonsensical given the problem definition (e.g., a physical quantity that can only add to the outcome).

### `n_jobs`

Controls parallel computation for certain supported fitting paths (e.g., multiple targets). It does not change the fitted model itself.

### `copy_X`

Whether to copy the input data before fitting rather than overwrite it in place. A computational/memory setting, not a modeling choice.

### Modeling choices that matter more than any constructor argument

Although they aren't parameters on `LinearRegression` itself, these decisions typically have a much larger effect on model quality:

- Which features to include
- Whether to add interaction terms
- Whether to add polynomial features
- How to handle outliers
- Whether to transform skewed variables (e.g., log transform)
- Whether to use Ridge, Lasso, or Elastic Net regularization instead of plain OLS

---

## Advantages

**Easy to interpret** — each coefficient describes the expected change in the prediction associated with a one-unit change in that feature, holding the other included features constant.

**Fast to train** — linear regression is computationally inexpensive compared with most nonlinear machine learning models, even on large datasets.

**Strong baseline** — it's a useful benchmark before trying more complex algorithms. If a complex model barely outperforms linear regression, the added complexity may not be worth it.

**Works well for genuinely linear relationships** — when the underlying relationship is approximately linear and the data is reasonably clean, linear regression can perform extremely well with very little machinery.

**Supports statistical inference** — classical regression analysis can provide confidence intervals, hypothesis tests, standard errors, and other measures of coefficient uncertainty.

**Extrapolates** — unlike most tree-based models, linear regression can produce predictions outside the range of the observed target values. This can be useful, but it can also be dangerous (see Limitations).

---

## Limitations

**Assumes a restrictive functional form** — a basic model assumes each feature has a constant linear effect:

$$\hat{y} = \beta_0 + \beta_1 x$$

This assumes increasing $x$ by one unit has the same predicted effect at every value of $x$. Real relationships may instead have curves, thresholds, saturation points, interactions, or discontinuities.

**Sensitive to outliers** — because errors are squared, observations with large residuals can have an outsized influence on the fitted coefficients.

**Multicollinearity destabilizes coefficients** — when features are strongly correlated with one another, the model can struggle to separate their individual effects. Consequences include large coefficient swings between samples, unexpected coefficient signs, inflated standard errors, and difficult interpretation. Prediction accuracy can still be fine even when coefficient interpretation becomes unstable.

**Extrapolation can be unrealistic** — a fitted relationship may not continue to hold outside the observed feature range. A salary model trained on employees with 0–20 years of experience shouldn't be trusted at 100 years of experience.

**Coefficients do not prove causation** — a coefficient may capture confounding variables, selection effects, reverse causality, measurement bias, or coincidental correlation rather than a true causal effect.

**Basic OLS does not perform feature selection** — it typically assigns a nonzero coefficient to every supplied feature. With many noisy or correlated variables, regularized alternatives (Lasso, Elastic Net) may generalize better.

**Poor fit for some target types** — basic linear regression is generally a poor choice for binary outcomes, categories, counts with strongly non-normal structure, or tightly bounded outcomes. Logistic, Poisson, or tree-based models are usually more appropriate there.

---

## Simple example

Suppose we observe the following relationship between advertising expenditure and weekly sales:

| Advertising, $x$ | Sales, $y$ |
|---:|---:|
| 1 | 3 |
| 2 | 5 |
| 3 | 7 |
| 4 | 9 |

These observations lie exactly on:

$$\hat{y} = 1 + 2x$$

So the intercept is $\beta_0 = 1$ and the advertising coefficient is $\beta_1 = 2$. At an advertising value of 5:

$$\hat{y} = 1 + 2(5) = 11$$

The model predicts sales of 11 units.

### Python example

See [`linear_regression.py`](linear_regression.py) for the runnable version. It fits the same data shown above:

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

X = np.array([[1], [2], [3], [4]])  # 4 observations, 1 feature
y = np.array([3, 5, 7, 9])

model = LinearRegression()
model.fit(X, y)
predictions = model.predict(X)

print("Intercept:", model.intercept_)
print("Coefficient:", model.coef_[0])
print("Prediction for x=5:", model.predict([[5]])[0])
print("Residuals:", y - predictions)
print("MSE:", mean_squared_error(y, predictions))
print("R^2:", r2_score(y, predictions))
```

Expected output:

```text
Intercept: 1.0
Coefficient: 2.0
Prediction for x=5: 11.0
Residuals: [0. 0. 0. 0.]
MSE: 0.0
R^2: 1.0
```

The residuals are all exactly zero here only because this toy dataset was constructed to lie perfectly on a line — real data will almost never fit this cleanly.

### Interpreting the metrics

**Mean squared error**

$$MSE = \frac{1}{n}\sum_{i=1}^{n} (y_i - \hat{y}_i)^2$$

Lower is better. An MSE of zero means every prediction is exactly correct.

**Coefficient of determination**

$$R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}$$

An $R^2$ of 1 means the model explains all observed variation in the target within this dataset. A high training $R^2$ does not necessarily mean the model will generalize well to new, unseen data — it should always be checked on held-out data, not just the training set.

---

## Resources

- [Scikit-learn `LinearRegression` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html) — implementation details, parameters, and API examples.
- [Scikit-learn guide to linear models](https://scikit-learn.org/stable/modules/linear_model.html) — mathematical notation and related models such as Ridge and Lasso.
- [Penn State STAT 501](https://online.stat.psu.edu/stat501/) — detailed regression course notes covering assumptions, diagnostics, and inference.
- [Stanford: Statistical Learning](https://online.stanford.edu/courses/sohs-ystatslearning-statistical-learning-r) — accessible treatment of regression and broader statistical-learning concepts.
- [*The Elements of Statistical Learning*](https://link.springer.com/book/10.1007/978-0-387-84858-7) — advanced reference covering linear methods and the broader theory of statistical learning.

### Core fact to retain

> Linear regression predicts a continuous value by estimating the linear combination of features that minimizes squared prediction errors.
