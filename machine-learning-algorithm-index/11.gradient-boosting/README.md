# Gradient Boosting

## Overview

Gradient boosting is a **supervised learning algorithm**, for classification or regression, that builds an ensemble of decision trees like [Random Forest](../4.random-forest/README.md) — but where random forest trains many trees **independently in parallel** and averages them, gradient boosting trains trees **sequentially**, each one specifically correcting the errors the ensemble so far has made.

Where random forest's core idea is *reduce variance by averaging decorrelated trees*, gradient boosting's core idea is *reduce bias by iteratively fitting what's still wrong*. In practice, well-tuned gradient boosting frequently outperforms random forest on structured/tabular data, at the cost of being more sensitive to its hyperparameters and slower to train (see [XGBoost](../12.xgboost/README.md) for the optimized, more scalable implementation of the same idea).

---

## Intuition

Start with a simple baseline prediction — for regression with squared error loss, just the mean of the target. Look at the errors (residuals) that baseline makes. Fit a small tree specifically to *predict those residuals*. Add a scaled-down version of that tree's predictions to the baseline. Look at the new, smaller residuals. Fit another small tree to those. Repeat.

Each new tree is trained on "what's still unexplained," not on the original target — a very different training signal from random forest, where every tree independently tries to predict the whole target from a bootstrap resample. This is also why gradient boosting trees are typically kept shallow (`max_depth` of 2–6, sometimes even depth-1 stumps): each tree only needs to capture a small correction, not model the whole relationship on its own.

---

## Mathematical formulation

### Additive model

Gradient boosting builds up a prediction as a sum of many small models (here, small trees), added one at a time:

$$F_m(x) = F_{m-1}(x) + \nu \cdot h_m(x)$$

where $F_{m-1}$ is the ensemble so far, $h_m$ is the newly fit tree, and $\nu$ is the **learning rate** (`learning_rate`) — how much of the new tree's correction to actually apply.

### Fitting each tree to the negative gradient

The name "gradient" boosting comes from what each $h_m$ is actually fit to: the **negative gradient of the loss function** with respect to the current predictions, evaluated at each training point:

$$h_m \approx \arg\min_h \sum_{i=1}^n \left(-\frac{\partial L(y_i, F_{m-1}(x_i))}{\partial F_{m-1}(x_i)} - h(x_i)\right)^2$$

For **squared error loss** ($L = \frac{1}{2}(y-F)^2$), the negative gradient works out to exactly the residual, $y_i - F_{m-1}(x_i)$ — which is why the residual-fitting description in [Intuition](#intuition) is not just an analogy for squared error loss, it's exactly what's happening. For **log loss** (classification, same loss as [Logistic Regression](../2.logistic-regression/README.md#mathematical-formulation)), the negative gradient is $y_i - \hat{p}_i$ — the same residual idea, just on the probability scale. This is what makes gradient boosting a general framework: swapping the loss function changes what each tree is fit to, without changing the overall algorithm.

### Shrinkage

Using $\nu < 1$ (`learning_rate`) deliberately makes each step an under-correction rather than a full one, requiring more trees (`n_estimators`) to reach the same fit — but empirically produces better-generalizing models than taking full-sized steps, for the same reason a smaller step size in gradient descent is often preferable to a larger one.

---

## Typical hyperparameters

### `n_estimators`

Number of boosting stages (trees). Unlike random forest, **more is not always better** here — because each tree keeps correcting residuals, too many stages will eventually start fitting noise in the training data (overfitting), so this is tuned jointly with `learning_rate`, usually via early stopping on a validation set.

```python
GradientBoostingRegressor(n_estimators=100)
```

### `learning_rate`

The shrinkage factor $\nu$ above. Smaller values need more `n_estimators` to reach the same training fit but generalize better; a common practical trade-off is "as small a learning rate as compute budget allows, with enough estimators (or early stopping) to compensate."

```python
GradientBoostingRegressor(learning_rate=0.1)
```

### `max_depth`

Depth of each individual tree. Much shallower than a standalone decision tree or a random forest tree would typically use — depth 3–6 is common, since each tree is only meant to model a small correction, not the whole target.

### `subsample`

Fraction of training rows used to fit each tree (< 1.0 gives "stochastic gradient boosting"). Introduces some of random forest's bagging-style randomness into an otherwise fully sequential/deterministic process, which can reduce overfitting.

### `loss`

The loss function being minimized (`"squared_error"` for regression by default; `"log_loss"` for classification) — this is what determines what the negative gradient (and therefore what each tree is fit to) actually is.

### Modeling choices that matter more than any single constructor argument

- `n_estimators` and `learning_rate` tuned **together**, typically with early stopping (`n_iter_no_change`, `validation_fraction`) rather than a fixed grid search over both independently.
- Tree depth kept shallow relative to what a standalone tree or random forest would use.
- Whether the added training time and tuning sensitivity are worth it relative to a random forest baseline for the specific dataset at hand.

---

## Advantages

**Often the strongest tabular-data performer among classical ML methods** when properly tuned — a large share of tabular data science competition winners use gradient-boosted trees (usually [XGBoost](../12.xgboost/README.md) or a close relative).

**Optimizes an explicit, flexible loss function** — the same framework covers regression, classification, ranking, and quantile prediction just by swapping the loss, unlike random forest's fixed averaging/voting mechanism.

**Naturally captures nonlinearities and interactions**, inheriting this from its tree base learners.

**Handles mixed feature types** without scaling, same as any tree-based method.

---

## Limitations

**Sequential training — doesn't parallelize the way random forest does** — each tree depends on the previous ensemble's residuals, so trees can't be fit independently across cores the way random forest's trees can (this is one of the specific things [XGBoost](../12.xgboost/README.md) and other modern implementations optimize around).

**More hyperparameter-sensitive than random forest** — `n_estimators`, `learning_rate`, and `max_depth` all interact, and a poor combination (especially too many estimators with too high a learning rate) overfits noticeably more easily than random forest tends to.

**Slower to train** than a random forest with a comparable number of trees, precisely because of the sequential dependency.

**More sensitive to outliers** than random forest — because each tree is fit directly to residuals, an outlier's unusually large residual gets specifically targeted by the next tree, rather than merely being one vote among many bootstrap samples.

**Extrapolates poorly**, inheriting this from its tree base learners, same as random forest.

**Requires care to avoid overfitting** — without early stopping or a validation-tuned `n_estimators`, training accuracy can be driven arbitrarily high while generalization gets worse, a failure mode that isn't self-limiting the way adding more random forest trees is.

---

## Simple example

A small regression dataset with visible structure:

| $x$ | $y$ |
|---:|---:|
| 1 | 1 |
| 2 | 2 |
| 3 | 6 |
| 4 | 8 |
| 5 | 4 |
| 6 | 5 |

Running 2 boosting stages by hand, with `learning_rate=1.0` and depth-1 stumps (finding, at each stage, the single threshold that minimizes total squared error of the *residuals*):

**Stage 0 (initialization):** $F_0(x) = \bar{y} = 4.333$ for every point.

**Stage 1:** residuals are $y - F_0 = [-3.33, -2.33, 1.67, 3.67, -0.33, 0.67]$. The best stump splits at $x \leq 2.5$ (mean residual $-2.83$) vs. $x > 2.5$ (mean residual $1.42$). Adding this to $F_0$:

$$F_1(x) = [1.5,\ 1.5,\ 5.75,\ 5.75,\ 5.75,\ 5.75]$$

**Stage 2:** new residuals are $y - F_1 = [-0.5, 0.5, 0.25, 2.25, -1.75, -0.75]$. The best stump now splits at $x \leq 4.5$ (mean residual $0.625$) vs. $x > 4.5$ (mean residual $-1.25$). Adding this to $F_1$:

$$F_2(x) = [2.125,\ 2.125,\ 6.375,\ 6.375,\ 4.5,\ 4.5]$$

Mean squared error has dropped from $\text{Var}(y) \approx 5.56$ at initialization to $\approx 0.76$ after just 2 stages.

### Python example

See [`gradient_boosting.py`](gradient_boosting.py) for the runnable version:

```python
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

X = np.array([[1], [2], [3], [4], [5], [6]])
y = np.array([1, 2, 6, 8, 4, 5])

# criterion="squared_error" (rather than scikit-learn's default "friedman_mse")
# so each tree's split matches the plain weighted-SSE-minimizing split used
# in the hand computation above.
model = GradientBoostingRegressor(
    n_estimators=2, learning_rate=1.0, max_depth=1, criterion="squared_error"
)
model.fit(X, y)

for i, pred in enumerate(model.staged_predict(X), start=1):
    print(f"After stage {i}:", pred)
```

Expected output (matches the hand-computed stage-by-stage predictions above):

```text
After stage 1: [1.5   1.5   5.75  5.75  5.75  5.75]
After stage 2: [2.125 2.125 6.375 6.375 4.5   4.5  ]
```

---

## Resources

- [Scikit-learn `GradientBoostingRegressor` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html) — parameters, `staged_predict`, early stopping options.
- [Scikit-learn ensemble methods guide](https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting) — the algorithm, loss functions, and comparison to random forest.
- [Friedman, "Greedy Function Approximation: A Gradient Boosting Machine" (2001)](https://projecteuclid.org/euclid.aos/1013203451) — the original gradient boosting paper.
- [*The Elements of Statistical Learning*, Ch. 10](https://link.springer.com/book/10.1007/978-0-387-84858-7) — boosting, the gradient boosting framework, and its relationship to other additive models.

### Core fact to retain

> Gradient boosting builds an ensemble sequentially, with each new (typically shallow) tree fit to the negative gradient of the loss — for squared error, literally the residuals — of the ensemble so far, trading random forest's easy parallelism and robustness for a usually stronger, but more tuning-sensitive, fit.
