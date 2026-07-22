# Linear Regression

## Overview

Linear regression is a **supervised learning algorithm** used to predict a **continuous numerical outcome**.

Common applications include predicting:

- Salary from years of experience
- House prices from size and location
- Monthly sales from advertising spending
- Delivery times from distance and order volume
- Energy consumption from temperature and building size

The model represents the predicted target as a weighted sum of the input features:

$$
\hat{y}
=
\beta_0
+
\beta_1 x_1
+
\beta_2 x_2
+
\cdots
+
\beta_p x_p
$$

Where:

- $\hat{y}$ is the predicted outcome.
- $x_1, \ldots, x_p$ are the input features.
- $\beta_0$ is the intercept.
- $\beta_1, \ldots, \beta_p$ are the learned coefficients.
- $p$ is the number of features.

Ordinary least squares linear regression estimates the coefficients that minimize the sum of squared prediction errors.

---

## Intuition

Imagine plotting employee salaries against years of experience.

The observations will probably not form a perfect line, but they may show an upward trend. Linear regression attempts to find the straight line that best summarizes this relationship.

For a model with one input feature:

$$
\hat{y}
=======

\beta_0
+
\beta_1x
$$

Suppose the fitted salary model is:

$$
\widehat{\text{Salary}}
=======================

45{,}000
+
4{,}000
\times
\text{Years of Experience}
$$

The coefficients can be interpreted as follows:

* **Intercept:** $\beta_0 = 45{,}000$
* **Slope:** $\beta_1 = 4{,}000$

The model predicts a salary of **$45,000** for someone with zero years of experience.

Each additional year of experience is associated with a predicted **$4,000 increase in salary**.

The word **associated** is important. A regression coefficient describes a relationship in the data, but it does not automatically establish causation.

### Residuals

A residual is the difference between an observed value and the model's prediction.

$$
e_i
===

## y_i

\hat{y}_i
$$

Where:

* $y_i$ is the actual value for observation $i$.
* $\hat{y}_i$ is the predicted value.
* $e_i$ is the residual.

A positive residual means:

$$
y_i > \hat{y}_i
$$

The model predicted too low.

A negative residual means:

$$
y_i < \hat{y}_i
$$

The model predicted too high.

A residual of zero means the prediction exactly matches the observed value.

---

## Mathematical Formulation

### Model for One Observation

For observation $i$, a multiple linear regression model is:

$$
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
$$

Where:

* $y_i$ is the observed target value.
* $x_{ij}$ is the value of feature $j$ for observation $i$.
* $\beta_j$ is the coefficient for feature $j$.
* $\epsilon_i$ is the unexplained error.

The corresponding predicted value is:

$$
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
$$

The hats indicate estimated values.

For example:

$$
\hat{\beta}_j
=============

\text{estimated value of }
\beta_j
$$

The prediction excludes the unknown error term because the model cannot directly observe $\epsilon_i$.

### Matrix Form

The complete regression model can be written as:

$$
\mathbf{y}
==========

\mathbf{X}\boldsymbol{\beta}
+
\boldsymbol{\epsilon}
$$

Where:

* $\mathbf{y}$ is the vector of observed target values.
* $\mathbf{X}$ is the feature matrix.
* $\boldsymbol{\beta}$ is the vector of coefficients.
* $\boldsymbol{\epsilon}$ is the vector of errors.

The predicted target vector is:

$$
\hat{\mathbf{y}}
================

\mathbf{X}\hat{\boldsymbol{\beta}}
$$

The residual vector is:

$$
\mathbf{e}
==========

## \mathbf{y}

\hat{\mathbf{y}}
$$

### Ordinary Least Squares Objective

Ordinary least squares, or OLS, chooses the coefficients that minimize the **residual sum of squares**.

$$
RSS
===

\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}_i
\right)^2
$$

Because:

$$
e_i
===

## y_i

\hat{y}_i
$$

RSS can also be written as:

$$
RSS
===

\sum_{i=1}^{n}
e_i^2
$$

The optimization problem is:

$$
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\sum_{i=1}^{n}
\left(
y_i
---

\mathbf{x}_i^T\boldsymbol{\beta}
\right)^2
$$

Using matrix notation:

$$
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\left|
\mathbf{y}
----------

\mathbf{X}\boldsymbol{\beta}
\right|_2^2
$$

The notation $\arg\min$ means the parameter values that produce the minimum value of the objective function.

The notation $|\cdot|_2^2$ represents the squared Euclidean norm.

### Why Square the Errors?

Squaring the errors has several useful effects:

* Positive and negative residuals cannot cancel each other out.
* Large residuals receive greater penalties than small residuals.
* The objective function is smooth and mathematically convenient to optimize.

For example:

$$
(-5)^2
======

25
$$

While:

$$
2^2
===

4
$$

An error with magnitude $5$ therefore contributes much more to the loss than an error with magnitude $2$.

### Closed-Form Solution

Under suitable mathematical conditions, the OLS coefficient estimate can be written as:

$$
\hat{\boldsymbol{\beta}}
========================

\left(
\mathbf{X}^T\mathbf{X}
\right)^{-1}
\mathbf{X}^T\mathbf{y}
$$

Where:

* $\mathbf{X}^T$ is the transpose of $\mathbf{X}$.
* $(\mathbf{X}^T\mathbf{X})^{-1}$ is the inverse of $\mathbf{X}^T\mathbf{X}$.

This formula requires $\mathbf{X}^T\mathbf{X}$ to be invertible.

In practice, machine-learning libraries typically use more numerically stable methods, such as QR decomposition or singular value decomposition, rather than directly calculating the inverse.

### Expected Value Interpretation

Linear regression models the conditional expected value of the target:

$$
\mathbb{E}[Y \mid X]
====================

\beta_0
+
\beta_1X_1
+
\cdots
+
\beta_pX_p
$$

The expression $\mathbb{E}[Y \mid X]$ means the expected value of $Y$ given the observed features $X$.

### Coefficient Interpretation

For feature $x_j$, the corresponding coefficient is $\beta_j$.

Holding the other included features constant:

$$
\Delta\hat{y}
=============

\beta_j\Delta x_j
$$

For a one-unit increase in the feature:

$$
\Delta x_j
==========

1
$$

Therefore:

$$
\Delta\hat{y}
=============

\beta_j
$$

This means that a one-unit increase in $x_j$ is associated with a predicted change of $\beta_j$ units in the target, assuming the other included features remain constant.

---

## Assumptions

The assumptions of linear regression are especially important when using the model for statistical inference, confidence intervals, or hypothesis tests.

### Linearity

The expected target should be representable as a linear combination of the model coefficients.

$$
\mathbb{E}[Y \mid X]
====================

\mathbf{X}\boldsymbol{\beta}
$$

Linear regression is linear in its coefficients, though the input features may include transformations such as $x^2$ or $\log(x)$.

### Zero Conditional Mean

The errors should have an expected value of zero after conditioning on the features.

$$
\mathbb{E}[\epsilon \mid X]
===========================

0
$$

This means the model should not systematically overpredict or underpredict for particular feature values.

Violations often indicate:

* Missing important variables
* Incorrect functional form
* Selection bias
* Endogeneity
* Measurement problems

### Independence

Errors should not be correlated across observations.

$$
\operatorname{Cov}(\epsilon_i, \epsilon_j)
==========================================

0
\qquad
\text{for }
i \neq j
$$

This assumption may be violated in:

* Time-series data
* Repeated measurements
* Geographic data
* Clustered observations
* Panel data

### Homoscedasticity

The conditional variance of the errors should be approximately constant.

$$
\operatorname{Var}(\epsilon_i \mid X)
=====================================

\sigma^2
$$

Where $\sigma^2$ is the error variance.

If the residual variance changes across feature values, the errors are heteroscedastic.

$$
\operatorname{Var}(\epsilon_i \mid X)
\neq
\sigma^2
$$

Heteroscedasticity may make standard errors and statistical tests unreliable, even when the coefficient estimates remain useful.

### No Perfect Multicollinearity

No predictor should be an exact linear combination of the other predictors.

For example, perfect multicollinearity exists if:

$$
x_3
===

2x_1
+
5x_2
$$

Strong but imperfect multicollinearity can also make coefficient estimates unstable.

### Normality of Errors

For classical small-sample confidence intervals and hypothesis tests, errors are often assumed to follow a normal distribution.

$$
\epsilon_i
\sim
\mathcal{N}(0,\sigma^2)
$$

Normality is not strictly required simply to fit an OLS model.

It matters more for:

* Small-sample statistical inference
* Confidence intervals
* Hypothesis tests
* Prediction intervals

---

## Typical Hyperparameters

Ordinary least squares has relatively few true hyperparameters. Most performance differences come from feature selection, preprocessing, and model design.

### `fit_intercept`

Controls whether the model estimates an intercept.

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression(fit_intercept=True)
```

The default is usually appropriate.

Set `fit_intercept=False` only when:

* The features and target have already been centered.
* Domain knowledge requires the model to pass through the origin.
* An intercept has already been included manually.

Without an intercept, the model becomes:

$$
\hat{y}
=======

\beta_1x_1
+
\cdots
+
\beta_px_p
$$

### `positive`

Restricts all coefficients to nonnegative values.

$$
\beta_j
\geq
0
\qquad
\text{for every }
j
$$

```python
model = LinearRegression(positive=True)
```

This may be useful when negative coefficients would contradict known constraints.

For example, a production model might require all resource inputs to have nonnegative estimated effects.

### `n_jobs`

Controls parallel computation for supported fitting cases.

```python
model = LinearRegression(n_jobs=-1)
```

A value of `-1` generally means to use all available processors.

This parameter affects computational performance rather than the statistical form of the model.

### `tol`

Controls numerical convergence tolerance for certain sparse-data calculations.

```python
model = LinearRegression(tol=1e-6)
```

This is mainly a computational parameter.

### Important Modeling Choices

These choices often matter more than the model's explicit hyperparameters:

* Which predictors to include
* How to encode categorical features
* Whether to transform skewed variables
* Whether to include polynomial terms
* Whether to include interaction terms
* How to handle missing values
* How to handle outliers
* Whether to standardize features
* Whether to use regularization
* How to divide training and test data

---

## Feature Engineering

### Interaction Terms

An interaction allows the effect of one feature to depend on another feature.

$$
\hat{y}
=======

\beta_0
+
\beta_1x_1
+
\beta_2x_2
+
\beta_3x_1x_2
$$

The interaction coefficient $\beta_3$ changes how $x_1$ and $x_2$ work together.

For example, the effect of advertising spending may depend on the size of the target market.

### Polynomial Terms

A quadratic model can be written as:

$$
\hat{y}
=======

\beta_0
+
\beta_1x
+
\beta_2x^2
$$

Although the relationship is curved with respect to $x$, it is still a linear model because it is linear in the coefficients $\beta_0$, $\beta_1$, and $\beta_2$.

A cubic model might be:

$$
\hat{y}
=======

\beta_0
+
\beta_1x
+
\beta_2x^2
+
\beta_3x^3
$$

Polynomial features can model nonlinear patterns, but high-degree polynomials can overfit and behave unpredictably outside the training range.

### Log Transformations

A feature can be log-transformed:

$$
\hat{y}
=======

\beta_0
+
\beta_1\log(x)
$$

A target can also be log-transformed:

$$
\log(\hat{y})
=============

\beta_0
+
\beta_1x
$$

Log transformations may help with:

* Right-skewed variables
* Multiplicative relationships
* Percentage-based interpretation
* Nonconstant residual variance

---

## Regularized Alternatives

Regularization adds a penalty to the regression objective to reduce model complexity and coefficient instability.

### Ridge Regression

Ridge regression adds an $L_2$ penalty.

$$
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\left[
\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}*i
\right)^2
+
\lambda
\sum*{j=1}^{p}
\beta_j^2
\right]
$$

The parameter $\lambda$ controls the strength of regularization.

A larger $\lambda$ shrinks the coefficients more strongly toward zero.

Ridge regression is useful when:

* Predictors are highly correlated
* There are many features
* Coefficient stability matters
* Some bias is acceptable in exchange for lower variance

### Lasso Regression

Lasso regression adds an $L_1$ penalty.

$$
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\left[
\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}*i
\right)^2
+
\lambda
\sum*{j=1}^{p}
|\beta_j|
\right]
$$

Lasso can reduce some coefficients exactly to zero.

This makes it useful for:

* Feature selection
* Sparse models
* High-dimensional datasets
* Improving interpretability

### Elastic Net

Elastic Net combines $L_1$ and $L_2$ penalties.

$$
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\left[
\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}*i
\right)^2
+
\lambda_1
\sum*{j=1}^{p}
|\beta_j|
+
\lambda_2
\sum_{j=1}^{p}
\beta_j^2
\right]
$$

Elastic Net can be useful when predictors are numerous and strongly correlated.

---

## Advantages

### Interpretability

Linear regression coefficients have relatively direct interpretations.

Each coefficient estimates the predicted change in the target associated with a one-unit increase in the corresponding feature, holding other included features constant.

### Fast Training

Linear regression is computationally efficient compared with many nonlinear algorithms.

It works well as an initial baseline.

### Strong Benchmark

A linear model gives a useful performance reference before trying more complex algorithms.

If a complex model only slightly outperforms linear regression, the additional complexity may not be justified.

### Effective for Linear Relationships

When the underlying relationship is approximately linear, linear regression can perform very well.

### Supports Statistical Inference

Traditional regression analysis can provide:

* Standard errors
* Confidence intervals
* Hypothesis tests
* Prediction intervals
* Measures of coefficient uncertainty

A common hypothesis test for coefficient $\beta_j$ is:

$$
H_0
:
\beta_j
=======

0
$$

$$
H_1
:
\beta_j
\neq
0
$$

The null hypothesis states that the feature has no linear association with the target after controlling for the other included predictors.

### Can Extrapolate

Linear regression can produce predictions outside the range observed in the training data.

This is different from many tree-based models, which generally predict combinations of observed target values.

Extrapolation can be useful, but it can also be dangerous when the relationship does not continue beyond the observed range.

### Works with Large Datasets

Linear regression can scale efficiently to large datasets, particularly when the number of features is moderate.

---

## Limitations

### Restrictive Functional Form

Basic linear regression assumes a constant linear relationship.

$$
\hat{y}
=======

\beta_0
+
\beta_1x
$$

This assumes that every one-unit increase in $x$ has the same predicted effect, regardless of the original value of $x$.

Real relationships may instead contain:

* Curves
* Thresholds
* Saturation
* Interactions
* Discontinuities
* Seasonal patterns

### Sensitivity to Outliers

Because OLS squares each residual, observations with large errors receive substantial weight.

For example:

$$
10^2
====

100
$$

While:

$$
2^2
===

4
$$

The error of $10$ contributes 25 times as much to the loss:

$$
\frac{10^2}{2^2}
================

# \frac{100}{4}

25
$$

A small number of extreme observations can significantly shift the fitted line.

### Multicollinearity

When predictors are strongly correlated, the model may struggle to separate their individual effects.

Possible consequences include:

* Unstable coefficients
* Large standard errors
* Unexpected coefficient signs
* Difficult interpretation
* Large changes after small data updates

Prediction quality can remain acceptable even when coefficient interpretation becomes unreliable.

### Unrealistic Extrapolation

A fitted relationship may not remain valid outside the observed feature range.

A salary model trained on employees with 0 to 20 years of experience should not automatically be trusted for someone with 100 years of experience.

### Association Is Not Causation

Regression coefficients do not automatically identify causal effects.

Observed relationships may reflect:

* Confounding variables
* Reverse causality
* Selection bias
* Measurement error
* Omitted variables
* Coincidental correlation

### Limited Feature Selection

Ordinary least squares usually estimates a coefficient for every supplied feature.

When the number of predictors is close to or greater than the number of observations:

$$
p
\geq
n
$$

The model may become unstable or may not have a unique OLS solution.

Where:

* $p$ is the number of predictors.
* $n$ is the number of observations.

Regularization may be more appropriate in this setting.

### Poor Fit for Some Target Types

Basic linear regression is not generally appropriate for:

* Binary outcomes
* Multiclass outcomes
* Strongly skewed count data
* Probabilities restricted between 0 and 1
* Time-to-event outcomes
* Ordinal categories

Alternative models include:

* Logistic regression
* Poisson regression
* Negative binomial regression
* Survival models
* Tree-based algorithms

### Sensitive to Data Leakage

Linear regression can appear highly accurate when training data contains information that would not be available at prediction time.

Examples include:

* Future information
* Post-outcome variables
* Target-derived features
* Preprocessing performed before the train-test split

---

## Simple Example

Suppose advertising expenditure and weekly sales follow this pattern:

| Advertising, $x$ | Sales, $y$ |
| ---------------: | ---------: |
|                1 |          3 |
|                2 |          5 |
|                3 |          7 |
|                4 |          9 |

These observations lie exactly on the line:

$$
\hat{y}
=======

1
+
2x
$$

Therefore:

$$
\beta_0
=======

1
$$

And:

$$
\beta_1
=======

2
$$

The intercept means that when advertising equals zero, predicted sales equal one unit.

The slope means that each one-unit increase in advertising is associated with a two-unit increase in predicted sales.

For an advertising value of five:

$$
x
=

5
$$

The prediction is:

$$
\hat{y}
=======

1
+
2(5)
$$

Therefore:

$$
\hat{y}
=======

11
$$

The model predicts sales of 11 units.

### Residual Calculation

For the first observation:

$$
y_1
===

3
$$

The model predicts:

$$
\hat{y}_1
=========

1
+
2(1)
====

3
$$

The residual is:

$$
e_1
===

## y_1

# \hat{y}_1

## 3

# 3

0
$$

Because all observations lie exactly on the line:

$$
e_i
===

0
\qquad
\text{for every }
i
$$

Therefore:

$$
RSS
===

0
$$

---

## Python Example

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# Four observations and one feature
X = np.array([[1], [2], [3], [4]])
y = np.array([3, 5, 7, 9])

model = LinearRegression()
model.fit(X, y)

training_predictions = model.predict(X)
new_prediction = model.predict([[5]])

mse = mean_squared_error(y, training_predictions)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y, training_predictions)
r_squared = r2_score(y, training_predictions)

print(f"Intercept: {model.intercept_:.2f}")
print(f"Coefficient: {model.coef_[0]:.2f}")
print(f"Prediction for x=5: {new_prediction[0]:.2f}")
print(f"MSE: {mse:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"R²: {r_squared:.2f}")
```

Expected output:

```text
Intercept: 1.00
Coefficient: 2.00
Prediction for x=5: 11.00
MSE: 0.00
RMSE: 0.00
MAE: 0.00
R²: 1.00
```

---

## Train-Test Example

Evaluating the model on the same data used for training can produce overly optimistic results.

A better workflow uses separate training and test datasets.

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(seed=42)

X = np.arange(1, 101).reshape(-1, 1)
noise = rng.normal(loc=0, scale=10, size=100)
y = 20 + 3 * X.ravel() + noise

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)

model = LinearRegression()
model.fit(X_train, y_train)

test_predictions = model.predict(X_test)

mse = mean_squared_error(y_test, test_predictions)
r_squared = r2_score(y_test, test_predictions)

print(f"Intercept: {model.intercept_:.2f}")
print(f"Coefficient: {model.coef_[0]:.2f}")
print(f"Test MSE: {mse:.2f}")
print(f"Test R²: {r_squared:.2f}")
```

This evaluates how well the fitted relationship generalizes to unseen observations.

---

## Evaluation Metrics

### Mean Squared Error

Mean squared error is the average squared residual.

$$
MSE
===

\frac{1}{n}
\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}_i
\right)^2
$$

Equivalently:

$$
MSE
===

\frac{RSS}{n}
$$

Lower values are better.

An MSE of zero means every prediction is exactly correct.

$$
MSE
===

0
\iff
y_i
===

\hat{y}_i
\text{ for every }
i
$$

The symbol $\iff$ means “if and only if.”

Because errors are squared, MSE places greater weight on large errors.

### Root Mean Squared Error

Root mean squared error is:

$$
RMSE
====

\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}_i
\right)^2
}
$$

Equivalently:

$$
RMSE
====

\sqrt{MSE}
$$

RMSE is measured in the same units as the target variable.

For example, if the target is measured in dollars, RMSE is also measured in dollars.

### Mean Absolute Error

Mean absolute error is:

$$
MAE
===

\frac{1}{n}
\sum_{i=1}^{n}
\left|
y_i
---

\hat{y}_i
\right|
$$

MAE is less sensitive to extreme errors than MSE or RMSE.

It is often easier to explain to nontechnical audiences because it represents the average absolute prediction error.

### Coefficient of Determination

The coefficient of determination is:

$$
R^2
===

## 1

\frac{
\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}*i
\right)^2
}{
\sum*{i=1}^{n}
\left(
y_i
---

\bar{y}
\right)^2
}
$$

The numerator is the residual sum of squares:

$$
RSS
===

\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}_i
\right)^2
$$

The denominator is the total sum of squares:

$$
TSS
===

\sum_{i=1}^{n}
\left(
y_i
---

\bar{y}
\right)^2
$$

Therefore:

$$
R^2
===

## 1

\frac{RSS}{TSS}
$$

Interpretation:

* $R^2 = 1$ means the model perfectly predicts the observed values.
* $R^2 = 0$ means the model performs no better than predicting the target mean.
* $R^2 < 0$ means the model performs worse than predicting the target mean.

A high training $R^2$ does not guarantee good performance on unseen data.

### Adjusted Coefficient of Determination

Adjusted $R^2$ penalizes the inclusion of additional predictors.

$$
\bar{R}^2
=========

## 1

\left(
1
-

R^2
\right)
\frac{n-1}{n-p-1}
$$

Where:

* $n$ is the number of observations.
* $p$ is the number of predictors.

Unlike ordinary $R^2$, adjusted $R^2$ can decrease when irrelevant variables are added.

### Mean Absolute Percentage Error

Mean absolute percentage error is:

$$
MAPE
====

\frac{100}{n}
\sum_{i=1}^{n}
\left|
\frac{
y_i
---

\hat{y}_i
}{
y_i
}
\right|
$$

MAPE expresses prediction error as a percentage.

However, it can behave poorly when actual values are zero or close to zero.

---

## Diagnostic Checks

### Residual Plot

A residual plot compares residuals with predicted values.

A healthy residual plot should usually show:

* Residuals centered near zero
* No obvious curve
* Roughly constant vertical spread
* No strong clusters
* Few highly influential observations

A curved pattern may indicate a nonlinear relationship.

A funnel shape may indicate heteroscedasticity.

### Q-Q Plot

A quantile-quantile plot compares residuals with a theoretical normal distribution.

Large deviations from the diagonal may indicate:

* Heavy tails
* Skewness
* Outliers
* Non-normal errors

### Multicollinearity Check

The variance inflation factor for feature $j$ is:

$$
VIF_j
=====

\frac{1}{
1
-

R_j^2
}
$$

Where $R_j^2$ is obtained by regressing feature $j$ on the remaining predictors.

Higher VIF values indicate stronger multicollinearity.

Common rough guidelines are:

* VIF near 1: little multicollinearity
* VIF above 5: potentially concerning
* VIF above 10: often considered severe

These thresholds are guidelines rather than strict rules.

### Influence and Leverage

Some observations can have unusually large influence on the fitted model.

Important concepts include:

* Leverage
* Studentized residuals
* Cook's distance
* DFBETAs

Cook's distance measures how strongly an observation affects the fitted coefficients.

A highly influential observation is not automatically incorrect, but it should be investigated.

---

## When to Use Linear Regression

Linear regression is a strong choice when:

* The target is continuous.
* Relationships are approximately linear.
* Interpretability matters.
* Training speed matters.
* You need a baseline model.
* You need coefficient estimates.
* Statistical inference is important.
* The number of predictors is manageable.

Examples include:

* Revenue forecasting
* Salary modeling
* Demand estimation
* Cost prediction
* Housing-price analysis
* Marketing-response analysis
* Operational capacity planning

---

## When Not to Use Linear Regression

Linear regression may not be the best choice when:

* The target is categorical.
* The relationship is strongly nonlinear.
* The data contains many extreme outliers.
* Predictors interact in complex ways.
* The target is strongly bounded.
* The model must automatically capture thresholds.
* Prediction accuracy matters more than interpretability.
* The dataset has many more features than observations without regularization.

Possible alternatives include:

* Logistic regression
* Decision trees
* Random forests
* Gradient boosting
* Support vector regression
* Neural networks
* Generalized linear models
* Robust regression
* Quantile regression

---

## Practical Workflow

A typical linear regression workflow is:

1. Define the continuous target variable.
2. Select candidate predictors.
3. Inspect missing values and outliers.
4. Split the data into training and test sets.
5. Fit a baseline linear model.
6. Evaluate predictions on unseen data.
7. Inspect residual plots.
8. Check for multicollinearity.
9. Add transformations or interactions when justified.
10. Compare OLS with regularized alternatives.
11. Document assumptions and limitations.
12. Communicate coefficients carefully.

---

## Common Interview Questions

### What does a coefficient mean?

A coefficient represents the predicted change in the target associated with a one-unit increase in the feature, holding the other included features constant.

### Why does OLS square the residuals?

Squaring prevents cancellation, penalizes large errors, and creates a smooth optimization problem.

### What is the difference between a residual and an error?

An error is the theoretical difference between an observation and the true population relationship.

A residual is the observed difference between an observation and the fitted model prediction.

### What is multicollinearity?

Multicollinearity occurs when predictors are strongly linearly related.

It can make coefficient estimates unstable and difficult to interpret.

### Does a high $R^2$ mean the model is good?

Not necessarily.

A high $R^2$ can occur because of:

* Overfitting
* Data leakage
* Irrelevant predictors
* Strong trends
* Evaluation on training data

The model should also be evaluated on unseen data and checked for assumption violations.

### Why can $R^2$ be negative?

On test data, $R^2$ can be negative when the model performs worse than simply predicting the mean target value.

### Is feature scaling required?

Feature scaling is not generally required for ordinary least squares predictions.

However, scaling can be useful when:

* Comparing coefficient magnitudes
* Using Ridge or Lasso
* Improving numerical conditioning
* Combining regression with other preprocessing steps

### Can linear regression model nonlinear relationships?

Yes, if nonlinear transformations are included as features.

For example:

$$
\hat{y}
=======

\beta_0
+
\beta_1x
+
\beta_2x^2
$$

The model is nonlinear in $x$ but remains linear in the coefficients.

---

## Resources

### Documentation

* Scikit-learn: `LinearRegression`
* Scikit-learn: Linear Models User Guide
* Statsmodels: Ordinary Least Squares

### Courses and Tutorials

* Penn State STAT 501
* Stanford Statistical Learning
* StatQuest: Linear Regression
* Khan Academy: Regression

### Books

* *An Introduction to Statistical Learning*
* *The Elements of Statistical Learning*
* *Applied Linear Statistical Models*
* *Regression and Other Stories*
* *Introduction to Linear Regression Analysis*

---

## Core Facts to Retain

Linear regression predicts a continuous outcome using a weighted sum of features.

$$
\hat{y}
=======

\beta_0
+
\sum_{j=1}^{p}
\beta_jx_j
$$

Ordinary least squares chooses the coefficient estimates that minimize squared residuals.

$$
\hat{\boldsymbol{\beta}}
========================

\arg\min_{\boldsymbol{\beta}}
\sum_{i=1}^{n}
\left(
y_i
---

\hat{y}_i
\right)^2
$$

A coefficient describes the expected change in the prediction associated with a one-unit change in the corresponding feature, holding other included features constant.

Important practical checks include:

* Whether the relationship is reasonably linear
* Whether influential outliers exist
* Whether residual variance is stable
* Whether predictors are strongly collinear
* Whether performance generalizes to unseen data
* Whether the features would be available at prediction time

The most important conceptual warning is:

> Regression coefficients describe associations unless the research design supports a causal interpretation.
