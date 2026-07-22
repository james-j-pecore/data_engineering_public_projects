# Linear Regression

## Overview

Linear regression is a **supervised learning algorithm** used to predict a **continuous numerical outcome**.

Examples include predicting:

* Salary from years of experience
* House price from size and location
* Monthly sales from advertising expenditure
* Delivery time from distance and order volume

The model represents the target as a weighted sum of the input features:

[
\hat{y}=\beta_0+\beta_1x_1+\beta_2x_2+\cdots+\beta_px_p
]

Markdown:

```markdown
\[
\hat{y}=\beta_0+\beta_1x_1+\beta_2x_2+\cdots+\beta_px_p
\]
```

Here:

* (\hat{y}) is the predicted outcome.
* (x_1,\ldots,x_p) are the input features.
* (\beta_0) is the intercept.
* (\beta_1,\ldots,\beta_p) are the learned coefficients.
* (p) is the number of features.

Inline Markdown:

```markdown
- \(\hat{y}\) is the predicted outcome.
- \(x_1,\ldots,x_p\) are the input features.
- \(\beta_0\) is the intercept.
- \(\beta_1,\ldots,\beta_p\) are the learned coefficients.
- \(p\) is the number of features.
```

Standard ordinary least squares linear regression chooses the coefficients that minimize the sum of squared prediction errors.

---

## Intuition

Imagine plotting employee salaries against years of experience.

The points will probably not form a perfect line, but they may show an upward pattern. Linear regression attempts to draw the straight line that best summarizes that relationship.

For one feature, the model is:

[
\hat{y}=\beta_0+\beta_1x
]

Markdown:

```markdown
\[
\hat{y}=\beta_0+\beta_1x
\]
```

Suppose the fitted model is:

[
\widehat{\text{Salary}}
=======================

45{,}000
+
4{,}000(\text{Years of Experience})
]

Markdown:

```markdown
\[
\widehat{\text{Salary}}
=
45{,}000
+
4{,}000(\text{Years of Experience})
\]
```

Interpretation:

* **Intercept:** (\beta_0=45{,}000)
* **Slope:** (\beta_1=4{,}000)

Inline Markdown:

```markdown
- **Intercept:** \(\beta_0=45{,}000\)
- **Slope:** \(\beta_1=4{,}000\)
```

The model predicts a salary of $45,000 for someone with zero years of experience.

Each additional year of experience is associated with a predicted $4,000 increase in salary.

The word **associated** matters. A regression coefficient does not automatically establish causation.

### Residuals

For each observation, the residual is:

[
e_i=y_i-\hat{y}_i
]

Markdown:

```markdown
\[
e_i=y_i-\hat{y}_i
\]
```

Here:

* (y_i) is the actual observed value.
* (\hat{y}_i) is the predicted value.
* (e_i) is the residual.
* (i) identifies the observation.

Inline Markdown:

```markdown
- \(y_i\) is the actual observed value.
- \(\hat{y}_i\) is the predicted value.
- \(e_i\) is the residual.
- \(i\) identifies the observation.
```

A positive residual means the model predicted too low:

[
y_i>\hat{y}_i
]

Markdown:

```markdown
\[
y_i>\hat{y}_i
\]
```

A negative residual means the model predicted too high:

[
y_i<\hat{y}_i
]

Markdown:

```markdown
\[
y_i<\hat{y}_i
\]
```

---

## Mathematical formulation

### Model for one observation

For observation (i), a multiple linear regression model is:

[
y_i
===

\beta_0
+
\beta_1x_{i1}
+
\beta_2x_{i2}
+
\cdots
+
\beta_px_{ip}
+
\epsilon_i
]

Markdown:

```markdown
\[
y_i
=
\beta_0
+
\beta_1x_{i1}
+
\beta_2x_{i2}
+
\cdots
+
\beta_px_{ip}
+
\epsilon_i
\]
```

The error term (\epsilon_i) represents variation that the included features do not explain.

Inline Markdown:

```markdown
The error term \(\epsilon_i\) represents variation that the included features do not explain.
```

The corresponding predicted value excludes the unknown error term:

[
\hat{y}_i
=========

\hat{\beta}_0
+
\hat{\beta}*1x*{i1}
+
\hat{\beta}*2x*{i2}
+
\cdots
+
\hat{\beta}*px*{ip}
]

Markdown:

```markdown
\[
\hat{y}_i
=
\hat{\beta}_0
+
\hat{\beta}_1x_{i1}
+
\hat{\beta}_2x_{i2}
+
\cdots
+
\hat{\beta}_px_{ip}
\]
```

The hats indicate estimated quantities:

[
\hat{\beta}_j=\text{estimated value of }\beta_j
]

Markdown:

```markdown
\[
\hat{\beta}_j=\text{estimated value of }\beta_j
\]
```

### Matrix formulation

The complete model can be written in matrix form:

[
\mathbf{y}
==========

\mathbf{X}\boldsymbol{\beta}
+
\boldsymbol{\epsilon}
]

Markdown:

```markdown
\[
\mathbf{y}
=
\mathbf{X}\boldsymbol{\beta}
+
\boldsymbol{\epsilon}
\]
```

Here:

* (\mathbf{y}) is the vector of observed target values.
* (\mathbf{X}) is the feature matrix.
* (\boldsymbol{\beta}) is the vector of model coefficients.
* (\boldsymbol{\epsilon}) is the vector of error terms.

Inline Markdown:

```markdown
- \(\mathbf{y}\) is the vector of observed target values.
- \(\mathbf{X}\) is the feature matrix.
- \(\boldsymbol{\beta}\) is the vector of model coefficients.
- \(\boldsymbol{\epsilon}\) is the vector of error terms.
```

The predicted target vector is:

[
\hat{\mathbf{y}}
================

\mathbf{X}\hat{\boldsymbol{\beta}}
]

Markdown:

```markdown
\[
\hat{\mathbf{y}}
=
\mathbf{X}\hat{\boldsymbol{\beta}}
\]
```

The residual vector is:

[
\mathbf{e}
==========

## \mathbf{y}

\hat{\mathbf{y}}
]

Markdown:

```markdown
\[
\mathbf{e}
=
\mathbf{y}
-
\hat{\mathbf{y}}
\]
```

### Objective function

Ordinary least squares minimizes the **residual sum of squares**, or RSS:

[
RSS
===

\sum_{i=1}^{n}
\left(y_i-\hat{y}_i\right)^2
]

Markdown:

```markdown
\[
RSS
=
\sum_{i=1}^{n}
\left(y_i-\hat{y}_i\right)^2
\]
```

Because the residual is (e_i=y_i-\hat{y}_i), RSS can also be written as:

[
RSS
===

\sum_{i=1}^{n}e_i^2
]

Markdown:

```markdown
\[
RSS
=
\sum_{i=1}^{n}e_i^2
\]
```

The coefficient-estimation problem is:

[
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\sum_{i=1}^{n}
\left(
y_i-\mathbf{x}_i^{T}\boldsymbol{\beta}
\right)^2
]

Markdown:

```markdown
\[
\hat{\boldsymbol{\beta}}
=
\arg\min_{\boldsymbol{\beta}}
\sum_{i=1}^{n}
\left(
y_i-\mathbf{x}_i^{T}\boldsymbol{\beta}
\right)^2
\]
```

It can also be written using vector notation:

[
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\left|
\mathbf{y}-\mathbf{X}\boldsymbol{\beta}
\right|_2^2
]

Markdown:

```markdown
\[
\hat{\boldsymbol{\beta}}
=
\arg\min_{\boldsymbol{\beta}}
\left\|
\mathbf{y}-\mathbf{X}\boldsymbol{\beta}
\right\|_2^2
\]
```

Here, (\arg\min) means “the argument or parameter values that produce the minimum.”

Inline Markdown:

```markdown
Here, \(\arg\min\) means “the argument or parameter values that produce the minimum.”
```

The notation (|\cdot|_2^2) represents the squared Euclidean norm.

Inline Markdown:

```markdown
The notation \(\|\cdot\|_2^2\) represents the squared Euclidean norm.
```

### Why square the errors?

Squaring the errors:

1. Prevents positive and negative residuals from canceling.
2. Penalizes large residuals more heavily than small residuals.
3. Produces a differentiable and computationally convenient objective function.

For example:

[
(-5)^2=25
]

Markdown:

```markdown
\[
(-5)^2=25
\]
```

and:

[
(2)^2=4
]

Markdown:

```markdown
\[
(2)^2=4
\]
```

Thus, an error with magnitude five receives much more weight than an error with magnitude two.

### Closed-form solution

Under appropriate mathematical conditions, the ordinary least squares estimate is:

[
\hat{\boldsymbol{\beta}}
========================

\left(
\mathbf{X}^{T}\mathbf{X}
\right)^{-1}
\mathbf{X}^{T}\mathbf{y}
]

Markdown:

```markdown
\[
\hat{\boldsymbol{\beta}}
=
\left(
\mathbf{X}^{T}\mathbf{X}
\right)^{-1}
\mathbf{X}^{T}\mathbf{y}
\]
```

Here:

* (\mathbf{X}^{T}) is the transpose of (\mathbf{X}).
* ((\mathbf{X}^{T}\mathbf{X})^{-1}) is the inverse of the matrix (\mathbf{X}^{T}\mathbf{X}).

Inline Markdown:

```markdown
- \(\mathbf{X}^{T}\) is the transpose of \(\mathbf{X}\).
- \((\mathbf{X}^{T}\mathbf{X})^{-1}\) is the inverse of the matrix \(\mathbf{X}^{T}\mathbf{X}\).
```

This formula requires (\mathbf{X}^{T}\mathbf{X}) to be invertible.

Inline Markdown:

```markdown
This formula requires \(\mathbf{X}^{T}\mathbf{X}\) to be invertible.
```

In practice, numerical libraries generally use more stable methods such as QR decomposition or singular value decomposition rather than directly calculating the inverse.

### Expected value interpretation

A linear regression model describes the conditional expected value of the target:

[
\mathbb{E}[Y\mid X]
===================

\beta_0
+
\beta_1X_1
+
\cdots
+
\beta_pX_p
]

Markdown:

```markdown
\[
\mathbb{E}[Y\mid X]
=
\beta_0
+
\beta_1X_1
+
\cdots
+
\beta_pX_p
\]
```

The expression (\mathbb{E}[Y\mid X]) means the expected value of (Y), conditional on the observed features (X).

Inline Markdown:

```markdown
The expression \(\mathbb{E}[Y\mid X]\) means the expected value of \(Y\), conditional on the observed features \(X\).
```

### Coefficient interpretation

For feature (x_j), its coefficient is (\beta_j).

Inline Markdown:

```markdown
For feature \(x_j\), its coefficient is \(\beta_j\).
```

Holding all other included features constant, a one-unit increase in (x_j) changes the predicted target by (\beta_j):

[
\Delta\hat{y}
=============

\beta_j\Delta x_j
]

Markdown:

```markdown
\[
\Delta\hat{y}
=
\beta_j\Delta x_j
\]
```

When the feature increases by one unit:

[
\Delta x_j=1
]

Markdown:

```markdown
\[
\Delta x_j=1
\]
```

Therefore:

[
\Delta\hat{y}=\beta_j
]

Markdown:

```markdown
\[
\Delta\hat{y}=\beta_j
\]
```

### Common assumptions for statistical inference

#### Linearity

The expected outcome is linear in the model coefficients:

[
\mathbb{E}[Y\mid X]
===================

\mathbf{X}\boldsymbol{\beta}
]

Markdown:

```markdown
\[
\mathbb{E}[Y\mid X]
=
\mathbf{X}\boldsymbol{\beta}
\]
```

#### Zero conditional mean

The errors should have an expected value of zero after conditioning on the features:

[
\mathbb{E}[\epsilon\mid X]=0
]

Markdown:

```markdown
\[
\mathbb{E}[\epsilon\mid X]=0
\]
```

This means the model should not systematically overpredict or underpredict for particular feature values.

#### Independence

Errors should not be correlated across observations:

[
\operatorname{Cov}(\epsilon_i,\epsilon_j)=0
\qquad
\text{for }i\neq j
]

Markdown:

```markdown
\[
\operatorname{Cov}(\epsilon_i,\epsilon_j)=0
\qquad
\text{for }i\neq j
\]
```

#### Homoscedasticity

The residual variance should be approximately constant across feature values:

[
\operatorname{Var}(\epsilon_i\mid X)
====================================

\sigma^2
]

Markdown:

```markdown
\[
\operatorname{Var}(\epsilon_i\mid X)
=
\sigma^2
\]
```

Here, (\sigma^2) is the error variance.

Inline Markdown:

```markdown
Here, \(\sigma^2\) is the error variance.
```

If the residual variance changes systematically, the data exhibits **heteroscedasticity**:

[
\operatorname{Var}(\epsilon_i\mid X)
\neq
\sigma^2
]

Markdown:

```markdown
\[
\operatorname{Var}(\epsilon_i\mid X)
\neq
\sigma^2
\]
```

#### No perfect multicollinearity

No feature should be an exact linear combination of the other features.

For example, perfect multicollinearity would exist if:

[
x_3=2x_1+5x_2
]

Markdown:

```markdown
\[
x_3=2x_1+5x_2
\]
```

#### Normally distributed errors

For classical small-sample hypothesis tests and confidence intervals, errors are often assumed to follow a normal distribution:

[
\epsilon_i
\sim
\mathcal{N}(0,\sigma^2)
]

Markdown:

```markdown
\[
\epsilon_i
\sim
\mathcal{N}(0,\sigma^2)
\]
```

Normality is not strictly required merely to fit an ordinary least squares model.

---

## Typical hyperparameters

Ordinary least squares has relatively few true hyperparameters. Most of its behavior comes from the data, feature engineering, and preprocessing choices.

### `fit_intercept`

Determines whether the model learns an intercept.

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression(fit_intercept=True)
```

Usually leave this as `True`.

Set it to `False` only when:

* The data has already been centered appropriately.
* Theoretical knowledge requires the regression line to pass through zero.

When the intercept is disabled, the model becomes:

[
\hat{y}
=======

\beta_1x_1+\cdots+\beta_px_p
]

Markdown:

```markdown
\[
\hat{y}
=
\beta_1x_1+\cdots+\beta_px_p
\]
```

### `positive`

Restricts the learned coefficients to nonnegative values:

[
\beta_j\geq 0
\qquad
\text{for every }j
]

Markdown:

```markdown
\[
\beta_j\geq 0
\qquad
\text{for every }j
\]
```

Python:

```python
model = LinearRegression(positive=True)
```

This can be useful when negative effects would be impossible according to the problem definition.

### `n_jobs`

Controls parallel computation for certain supported fitting cases.

```python
model = LinearRegression(n_jobs=-1)
```

A value of `-1` generally means to use all available processors.

This affects computation rather than the statistical form of the fitted model.

### `tol`

Controls numerical convergence tolerance for certain sparse-data calculations.

```python
model = LinearRegression(tol=1e-6)
```

This is primarily a computational setting rather than a modeling decision.

### Important modeling choices

Although they are not constructor hyperparameters, these choices often affect performance more strongly:

* Which features to include
* Whether to remove irrelevant features
* How to encode categorical variables
* Whether to include interaction terms
* Whether to include polynomial terms
* How to handle missing values
* How to treat outliers
* Whether to transform skewed variables
* Whether to use regularization

### Interaction terms

An interaction model might include:

[
\hat{y}
=======

\beta_0
+
\beta_1x_1
+
\beta_2x_2
+
\beta_3x_1x_2
]

Markdown:

```markdown
\[
\hat{y}
=
\beta_0
+
\beta_1x_1
+
\beta_2x_2
+
\beta_3x_1x_2
\]
```

The interaction coefficient (\beta_3) allows the effect of (x_1) to depend on the value of (x_2).

Inline Markdown:

```markdown
The interaction coefficient \(\beta_3\) allows the effect of \(x_1\) to depend on the value of \(x_2\).
```

### Polynomial terms

A quadratic regression model might be:

[
\hat{y}
=======

\beta_0
+
\beta_1x
+
\beta_2x^2
]

Markdown:

```markdown
\[
\hat{y}
=
\beta_0
+
\beta_1x
+
\beta_2x^2
\]
```

Although this relationship is curved with respect to (x), it is still considered a linear model because it is linear in the coefficients (\beta_0,\beta_1,\beta_2).

Inline Markdown:

```markdown
Although this relationship is curved with respect to \(x\), it is still considered a linear model because it is linear in the coefficients \(\beta_0,\beta_1,\beta_2\).
```

### Regularized alternatives

#### Ridge regression

Ridge regression adds an (L_2) penalty:

[
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\left[
\sum_{i=1}^{n}
\left(y_i-\hat{y}*i\right)^2
+
\lambda
\sum*{j=1}^{p}\beta_j^2
\right]
]

Markdown:

```markdown
\[
\hat{\boldsymbol{\beta}}
=
\arg\min_{\boldsymbol{\beta}}
\left[
\sum_{i=1}^{n}
\left(y_i-\hat{y}_i\right)^2
+
\lambda
\sum_{j=1}^{p}\beta_j^2
\right]
\]
```

#### Lasso regression

Lasso regression adds an (L_1) penalty:

[
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\left[
\sum_{i=1}^{n}
\left(y_i-\hat{y}*i\right)^2
+
\lambda
\sum*{j=1}^{p}
|\beta_j|
\right]
]

Markdown:

```markdown
\[
\hat{\boldsymbol{\beta}}
=
\arg\min_{\boldsymbol{\beta}}
\left[
\sum_{i=1}^{n}
\left(y_i-\hat{y}_i\right)^2
+
\lambda
\sum_{j=1}^{p}
|\beta_j|
\right]
\]
```

Here, (\lambda) controls the strength of regularization.

Inline Markdown:

```markdown
Here, \(\lambda\) controls the strength of regularization.
```

---

## Advantages

### Easy to interpret

Each coefficient describes the expected change in the prediction associated with a one-unit change in that feature, holding the other included features constant.

### Fast to train

Linear regression is computationally inexpensive compared with many nonlinear machine-learning algorithms.

### Strong baseline

It provides a useful benchmark before trying more complicated models.

If a complex model barely outperforms linear regression, the extra complexity may not be justified.

### Works well for linear relationships

When the relationship is approximately linear and the data is reasonably clean, linear regression can perform well.

### Supports statistical inference

Traditional regression analysis can provide:

* Confidence intervals
* Hypothesis tests
* Standard errors
* Measures of coefficient uncertainty

A typical coefficient hypothesis test is:

[
H_0:\beta_j=0
]

[
H_1:\beta_j\neq 0
]

Markdown:

```markdown
\[
H_0:\beta_j=0
\]

\[
H_1:\beta_j\neq 0
\]
```

The null hypothesis states that feature (j) has no linear association with the target after accounting for the other included features.

### Can extrapolate

Unlike many tree-based models, linear regression can produce predictions outside the range of the observed target values.

This may be useful, but it can also produce unrealistic results.

---

## Limitations

### Assumes a restrictive functional form

A basic model assumes that each feature has a constant linear effect.

For example:

[
\hat{y}=\beta_0+\beta_1x
]

Markdown:

```markdown
\[
\hat{y}=\beta_0+\beta_1x
\]
```

This assumes that increasing (x) by one unit has the same predicted effect at every value of (x).

Real relationships may instead have:

* Curves
* Thresholds
* Saturation points
* Interactions
* Discontinuities

### Sensitive to outliers

Because errors are squared, observations with large residuals can have substantial influence on the fitted coefficients.

For example:

[
10^2=100
]

Markdown:

```markdown
\[
10^2=100
\]
```

while:

[
2^2=4
]

Markdown:

```markdown
\[
2^2=4
\]
```

An error of 10 therefore contributes 25 times as much to the loss as an error of 2:

[
\frac{10^2}{2^2}
================

# \frac{100}{4}

25
]

Markdown:

```markdown
\[
\frac{10^2}{2^2}
=
\frac{100}{4}
=
25
\]
```

### Multicollinearity destabilizes coefficients

When features are strongly correlated with one another, the model may struggle to separate their individual effects.

Consequences can include:

* Large coefficient changes between samples
* Unexpected coefficient signs
* Large standard errors
* Difficult interpretation

Prediction may still be acceptable even when coefficient interpretation becomes unstable.

### Extrapolation can be unrealistic

A fitted relationship may not continue outside the observed feature range.

A salary model trained on people with 0–20 years of experience should not automatically be trusted at 100 years of experience.

### Coefficients do not prove causation

A coefficient may reflect:

* Confounding variables
* Selection effects
* Reverse causality
* Measurement bias
* Coincidental correlation

### Basic OLS does not perform feature selection

Ordinary least squares usually estimates a coefficient for every supplied feature.

When the number of features approaches or exceeds the number of observations, the model can become unstable.

This situation can be represented as:

[
p\geq n
]

Markdown:

```markdown
\[
p\geq n
\]
```

Here:

* (p) is the number of features.
* (n) is the number of observations.

Inline Markdown:

```markdown
- \(p\) is the number of features.
- \(n\) is the number of observations.
```

### Poor fit for some target types

Basic linear regression is generally inappropriate for:

* Binary outcomes
* Unordered categories
* Highly skewed count data
* Strongly bounded outcomes

Other models, such as logistic regression, Poisson regression, or tree-based models, may be more appropriate.

---

## Simple example

Suppose we observe the relationship between advertising expenditure and weekly sales:

| Advertising, (x) | Sales, (y) |
| ---------------: | ---------: |
|                1 |          3 |
|                2 |          5 |
|                3 |          7 |
|                4 |          9 |

Table-header Markdown:

```markdown
| Advertising, \(x\) | Sales, \(y\) |
|---:|---:|
| 1 | 3 |
| 2 | 5 |
| 3 | 7 |
| 4 | 9 |
```

These observations lie exactly on the line:

[
\hat{y}=1+2x
]

Markdown:

```markdown
\[
\hat{y}=1+2x
\]
```

Therefore:

[
\beta_0=1
]

Markdown:

```markdown
\[
\beta_0=1
\]
```

and:

[
\beta_1=2
]

Markdown:

```markdown
\[
\beta_1=2
\]
```

At an advertising value of five:

[
x=5
]

Markdown:

```markdown
\[
x=5
\]
```

The prediction is:

[
\hat{y}
=======

1+2(5)
]

Markdown:

```markdown
\[
\hat{y}
=
1+2(5)
\]
```

Therefore:

[
\hat{y}=11
]

Markdown:

```markdown
\[
\hat{y}=11
\]
```

The model predicts sales of 11 units.

### Residual calculations

For the first observation:

[
y_1=3
]

Markdown:

```markdown
\[
y_1=3
\]
```

The prediction is:

[
\hat{y}_1
=========

# 1+2(1)

3
]

Markdown:

```markdown
\[
\hat{y}_1
=
1+2(1)
=
3
\]
```

The residual is:

[
e_1
===

# y_1-\hat{y}_1

# 3-3

0
]

Markdown:

```markdown
\[
e_1
=
y_1-\hat{y}_1
=
3-3
=
0
\]
```

Because all four observations lie exactly on the regression line:

[
e_i=0
\qquad
\text{for every }i
]

Markdown:

```markdown
\[
e_i=0
\qquad
\text{for every }i
\]
```

Therefore:

[
RSS=0
]

Markdown:

```markdown
\[
RSS=0
\]
```

### Python example

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Four observations and one feature
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

---

## Evaluation metrics

### Mean squared error

Mean squared error is the average squared residual:

[
MSE
===

\frac{1}{n}
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
]

Markdown:

```markdown
\[
MSE
=
\frac{1}{n}
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
\]
```

Equivalently:

[
MSE=\frac{RSS}{n}
]

Markdown:

```markdown
\[
MSE=\frac{RSS}{n}
\]
```

Lower values are better.

An MSE of zero means every prediction is exactly correct:

[
MSE=0
\iff
y_i=\hat{y}_i
\text{ for every }i
]

Markdown:

```markdown
\[
MSE=0
\iff
y_i=\hat{y}_i
\text{ for every }i
\]
```

The symbol (\iff) means “if and only if.”

Inline Markdown:

```markdown
The symbol \(\iff\) means “if and only if.”
```

### Root mean squared error

Root mean squared error returns the error to the original units of the target:

[
RMSE
====

\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
}
]

Markdown:

```markdown
\[
RMSE
=
\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
}
\]
```

Equivalently:

[
RMSE=\sqrt{MSE}
]

Markdown:

```markdown
\[
RMSE=\sqrt{MSE}
\]
```

### Mean absolute error

Mean absolute error uses the absolute value of each residual:

[
MAE
===

\frac{1}{n}
\sum_{i=1}^{n}
\left|
y_i-\hat{y}_i
\right|
]

Markdown:

```markdown
\[
MAE
=
\frac{1}{n}
\sum_{i=1}^{n}
\left|
y_i-\hat{y}_i
\right|
\]
```

MAE is generally less sensitive to very large residuals than MSE.

### Coefficient of determination

The coefficient of determination is:

[
R^2
===

1-
\frac{
\sum_{i=1}^{n}
\left(
y_i-\hat{y}*i
\right)^2
}{
\sum*{i=1}^{n}
\left(
y_i-\bar{y}
\right)^2
}
]

Markdown:

```markdown
\[
R^2
=
1-
\frac{
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
}{
\sum_{i=1}^{n}
\left(
y_i-\bar{y}
\right)^2
}
\]
```

The numerator is the residual sum of squares:

[
RSS
===

\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
]

Markdown:

```markdown
\[
RSS
=
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
\]
```

The denominator is the total sum of squares:

[
TSS
===

\sum_{i=1}^{n}
\left(
y_i-\bar{y}
\right)^2
]

Markdown:

```markdown
\[
TSS
=
\sum_{i=1}^{n}
\left(
y_i-\bar{y}
\right)^2
\]
```

Thus:

[
R^2=1-\frac{RSS}{TSS}
]

Markdown:

```markdown
\[
R^2=1-\frac{RSS}{TSS}
\]
```

An (R^2) of one means the predictions perfectly match the observed values:

[
R^2=1
]

Markdown:

```markdown
\[
R^2=1
\]
```

An (R^2) of zero means the model performs no better on the evaluated data than predicting the mean target value:

[
R^2=0
]

Markdown:

```markdown
\[
R^2=0
\]
```

An (R^2) value can be negative on test data when the model performs worse than predicting the target mean:

[
R^2<0
]

Markdown:

```markdown
\[
R^2<0
\]
```

A high training (R^2) does not necessarily mean the model will generalize well to new data.

### Adjusted coefficient of determination

Adjusted (R^2) penalizes the inclusion of additional predictors:

[
\bar{R}^2
=========

1-
\left(
1-R^2
\right)
\frac{n-1}{n-p-1}
]

Markdown:

```markdown
\[
\bar{R}^2
=
1-
\left(
1-R^2
\right)
\frac{n-1}{n-p-1}
\]
```

Here:

* (n) is the number of observations.
* (p) is the number of predictor variables.

Inline Markdown:

```markdown
- \(n\) is the number of observations.
- \(p\) is the number of predictor variables.
```

---

## Resources

* **Scikit-learn: `LinearRegression` documentation**
  Implementation details, parameters, attributes, and API examples.

* **Scikit-learn: Linear Models user guide**
  Mathematical notation and related methods such as Ridge, Lasso, and Elastic Net.

* **Penn State STAT 501**
  Regression assumptions, diagnostics, inference, transformations, and worked examples.

* **An Introduction to Statistical Learning**
  Accessible treatment of linear regression and broader statistical-learning concepts.

* **The Elements of Statistical Learning**
  More advanced treatment of linear methods, regularization, model complexity, and statistical learning theory.

* **StatQuest: Linear Regression**
  Visual explanations of fitting a regression line, residuals, (R^2), and statistical significance.

---

## Core facts to retain

> Linear regression predicts a continuous value by estimating a linear combination of features.

The prediction equation is:

[
\hat{y}
=======

\beta_0
+
\sum_{j=1}^{p}\beta_jx_j
]

Markdown:

```markdown
\[
\hat{y}
=
\beta_0
+
\sum_{j=1}^{p}\beta_jx_j
\]
```

Ordinary least squares chooses the coefficients that minimize squared residuals:

[
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
]

Markdown:

```markdown
\[
\hat{\boldsymbol{\beta}}
=
\arg\min_{\boldsymbol{\beta}}
\sum_{i=1}^{n}
\left(
y_i-\hat{y}_i
\right)^2
\]
```

A coefficient describes an association, not necessarily a causal effect.

The most important practical checks are:

* Whether the relationship is reasonably linear
* Whether influential outliers exist
* Whether residual variance is stable
* Whether predictors are strongly collinear
* Whether performance holds on unseen data
