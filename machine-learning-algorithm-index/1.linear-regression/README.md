# Linear Regression

## Overview

Linear regression is a **supervised learning algorithm** used to predict a **continuous numerical outcome**.

Examples include predicting:

- Salary from years of experience
- House price from size and location
- Monthly sales from advertising expenditure
- Delivery time from distance and order volume

The model represents the target as a weighted sum of the input features:

\[
y^​=β0​+β1​x1​+β2​x2​+⋯+βp​xp​
\]

Here:

- \(\hat{y}\) is the predicted outcome.
- \(x_1,\ldots,x_p\) are the input features.
- \(\beta_0\) is the intercept.
- \(\beta_1,\ldots,\beta_p\) are learned coefficients.

Standard ordinary least squares linear regression chooses the coefficients that minimize the sum of squared prediction errors. 

---

## Intuition

Imagine plotting employee salaries against years of experience.

The points will probably not form a perfect line, but they may show an upward pattern. Linear regression attempts to draw the line that best summarizes that relationship.

For one feature:

\[
\hat{y} = \beta_0+\beta_1x
\]

Suppose the fitted model is:

\[
\widehat{\text{Salary}} = 45{,}000 + 4{,}000(\text{Years of Experience})
\]

Interpretation:

- **Intercept \(\beta_0=45{,}000\):** predicted salary at zero years of experience.
- **Slope \(\beta_1=4{,}000\):** each additional year of experience is associated with a predicted \$4,000 increase in salary.

The word **associated** matters. A regression coefficient does not automatically establish causation.

### Residuals

For every observation:

\[
e_i=y_i-\hat{y}_i
\]

where:

- \(y_i\) is the actual value.
- \(\hat{y}_i\) is the predicted value.
- \(e_i\) is the residual, or prediction error.

A positive residual means the model predicted too low. A negative residual means it predicted too high.

---

## Mathematical formulation

### Model

For observation \(i\):

\[
y_i=\beta_0+\beta_1x_{i1}+\cdots+\beta_px_{ip}+\epsilon_i
\]

The error term \(\epsilon_i\) represents variation that the included features do not explain.

In matrix form:

\[
\mathbf{y}=\mathbf{X}\boldsymbol{\beta}+\boldsymbol{\epsilon}
\]

### Objective function

Ordinary least squares minimizes the **residual sum of squares**:

\[
RSS=\sum_{i=1}^{n}(y_i-\hat{y}_i)^2
\]

Equivalently:

\[
\hat{\boldsymbol{\beta}}
=
\arg\min_{\boldsymbol{\beta}}
\|\mathbf{y}-\mathbf{X}\boldsymbol{\beta}\|_2^2
\]

Squaring the errors:

1. Prevents positive and negative errors from canceling out.
2. Penalizes large errors more heavily.
3. Produces a mathematically convenient optimization problem.

Under suitable conditions, the closed-form ordinary least squares estimate is:

\[
\hat{\boldsymbol{\beta}}
=
(\mathbf{X}^{T}\mathbf{X})^{-1}\mathbf{X}^{T}\mathbf{y}
\]

In practice, numerical libraries generally use more stable computational methods rather than directly calculating this inverse.

### Common assumptions for statistical inference

When linear regression is used to estimate confidence intervals, hypothesis tests, and coefficient significance, the classical assumptions become important:

- **Linearity:** the expected target is linear in the coefficients.
- **Independence:** observations or errors are independent.
- **Homoscedasticity:** residual variance is approximately constant.
- **No perfect multicollinearity:** one feature is not an exact linear combination of others.
- **Normally distributed errors:** mainly needed for traditional small-sample inference, not simply to fit the model.

These assumptions are stricter than what is required to use the model for prediction.

---

## Typical hyperparameters

Ordinary least squares has relatively few true hyperparameters. Most of its behavior comes from the data and feature design.

### `fit_intercept`

Determines whether the model learns an intercept.

```python
LinearRegression(fit_intercept=True)
```

Usually leave this as `True`.

Set it to `False` only when:

- The data has already been centered appropriately, or
- Theory requires the regression line to pass through zero.

### `positive`

Restricts coefficients to nonnegative values.

```python
LinearRegression(positive=True)
```

This can be useful when negative effects would be impossible or undesirable according to the problem definition.

### `n_jobs`

Controls parallel computation for certain supported fitting cases.

```python
LinearRegression(n_jobs=-1)
```

It usually does not meaningfully change the model itself.

### `tol`

A numerical convergence tolerance used for certain sparse-data calculations. It is primarily a computational setting rather than a modeling decision.

### Important modeling choices that act like hyperparameters

Although they are not constructor parameters, these decisions often matter more:

- Which features to include
- Whether to include interaction terms
- Whether to use polynomial features
- How to treat outliers
- Whether to transform skewed variables
- Whether to use Ridge, Lasso, or Elastic Net regularization

---

## Advantages

### Easy to interpret

Each coefficient describes the expected change in the prediction associated with a one-unit change in that feature, holding the other included features constant.

### Fast to train

Linear regression is computationally inexpensive compared with most nonlinear machine-learning models.

### Strong baseline

It provides a useful benchmark before trying more complicated algorithms. If a complex model barely outperforms linear regression, the additional complexity may not be justified.

### Works well for genuinely linear relationships

When the relationship is approximately linear and the data is reasonably clean, linear regression can perform extremely well.

### Supports statistical inference

Traditional regression analysis can provide:

- Confidence intervals
- Hypothesis tests
- Standard errors
- Measures of coefficient uncertainty

### Extrapolates

Unlike many tree-based models, linear regression can produce predictions outside the range of the observed target values. This can be useful, although it can also be dangerous.

---

## Limitations

### Assumes a restrictive functional form

A basic model assumes that each feature has a constant linear effect.

For example:

\[
\hat{y}=\beta_0+\beta_1x
\]

assumes that increasing \(x\) by one unit has the same predicted effect at every value of \(x\).

Real relationships may instead have:

- Curves
- Thresholds
- Saturation points
- Interactions
- Discontinuities

### Sensitive to outliers

Because errors are squared, observations with large residuals can have substantial influence on the fitted coefficients.

### Multicollinearity destabilizes coefficients

When features are strongly correlated with one another, the model may struggle to separate their individual effects.

Consequences can include:

- Large coefficient changes between samples
- Unexpected coefficient signs
- Large standard errors
- Difficult interpretation

Prediction may still be acceptable even when coefficient interpretation becomes unstable.

### Extrapolation can be unrealistic

A fitted relationship may not continue outside the observed feature range.

A salary model trained on workers with 0–20 years of experience should not be trusted automatically at 100 years of experience.

### Coefficients do not prove causation

A coefficient may capture:

- Confounding variables
- Selection effects
- Reverse causality
- Measurement bias
- Coincidental correlation

### Basic OLS does not perform feature selection

Ordinary least squares usually assigns a coefficient to every supplied feature. With many noisy or correlated variables, regularized alternatives may generalize better.

### Poor fit for some target types

Basic linear regression is generally inappropriate for:

- Binary outcomes
- Categories
- Counts with strongly non-normal structures
- Highly bounded outcomes

Other models, such as logistic, Poisson, or tree-based models, may be more suitable.

---

## Simple example

Suppose we observe the following relationship between advertising expenditure and weekly sales:

| Advertising, \(x\) | Sales, \(y\) |
|---:|---:|
| 1 | 3 |
| 2 | 5 |
| 3 | 7 |
| 4 | 9 |

These observations lie exactly on:

\[
\hat{y}=1+2x
\]

Therefore:

- Intercept: \(\beta_0=1\)
- Advertising coefficient: \(\beta_1=2\)

At an advertising value of \(5\):

\[
\hat{y}=1+2(5)=11
\]

The model predicts sales of 11 units.

### Python example

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# X must be two-dimensional:
# 4 observations and 1 feature
X = np.array([[1], [2], [3], [4]])
y = np.array([3, 5, 7, 9])

model = LinearRegression()
model.fit(X, y)

predictions = model.predict(X)

print("Intercept:", model.intercept_)
print("Coefficient:", model.coef_[0])
print("Prediction for x=5:", model.predict([[5]])[0])
print("MSE:", mean_squared_error(y, predictions))
print("R²:", r2_score(y, predictions))
```

Expected output:

```text
Intercept: 1.0
Coefficient: 2.0
Prediction for x=5: 11.0
MSE: 0.0
R²: 1.0
```

### Interpreting the metrics

**Mean squared error**

\[
MSE=\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2
\]

Lower is better. An MSE of zero means every prediction is exactly correct.

**Coefficient of determination**

\[
R^2
=
1-\frac{\sum_i(y_i-\hat{y}_i)^2}
{\sum_i(y_i-\bar{y})^2}
\]

An \(R^2\) of 1 means the model explains all observed variation in the target within this dataset. A high training \(R^2\) does not necessarily mean the model will generalize well to new data.

---

## Resources

- **Scikit-learn `LinearRegression` documentation:** implementation details, parameters, and API examples. (https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html?utm_source=chatgpt.com)
- **Scikit-learn guide to linear models:** mathematical notation and related models such as Ridge and Lasso. (https://scikit-learn.org/stable/modules/linear_model.html?utm_source=chatgpt.com)
- **Penn State STAT 501:** detailed regression course notes with assumptions, diagnostics, inference, and examples. (https://online.stat.psu.edu/stat501/?utm_source=chatgpt.com)
- **Stanford Statistical Learning course:** accessible treatment of regression and broader statistical-learning concepts. (https://online.stanford.edu/courses/sohs-ystatslearning-statistical-learning-r?utm_source=chatgpt.com)
- **The Elements of Statistical Learning:** advanced reference covering linear methods and the broader theoretical framework of statistical learning. (https://link.springer.com/book/10.1007/978-0-387-84858-7?utm_source=chatgpt.com)

### Core fact to retain

> Linear regression predicts a continuous value by estimating the linear combination of features that minimizes squared prediction errors.