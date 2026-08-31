# XGBoost

## Overview

XGBoost ("Extreme Gradient Boosting") is an optimized, regularized implementation of the same [Gradient Boosting](../11.gradient-boosting/README.md) idea — trees fit sequentially, each correcting the previous ensemble's errors — engineered specifically for speed, scalability, and resistance to overfitting. It's a separate library (not part of scikit-learn, though it ships a scikit-learn-compatible API) and was, for years, the dominant algorithm among winning solutions on tabular-data machine learning competitions.

The core sequential-correction idea is identical to plain gradient boosting; what XGBoost changes is *how* each tree's structure and leaf values are chosen — with an explicit regularization term baked into the optimization itself, rather than relying only on shrinkage and shallow trees to control overfitting.

---

## Intuition

Plain gradient boosting fits each new tree directly to the residuals (the negative gradient of the loss) using an ordinary regression tree, then hopes shrinkage (`learning_rate`) and shallow depth keep it from overfitting. XGBoost instead folds regularization directly into the criterion used to *choose* each tree's structure: both the split-selection gain and the optimal value predicted at each leaf come from minimizing loss **plus a penalty on the tree's complexity** — number of leaves and the size of their predicted values — in one closed-form step per candidate split (see [Mathematical formulation](#mathematical-formulation)).

This has a concrete, visible effect: leaf values in XGBoost are systematically **shrunk toward zero** relative to the plain average residual a standard gradient boosting tree would predict at that leaf — an explicit, tunable regularization on top of the shrinkage learning rate already provides (see [Simple example](#simple-example) for exactly how much).

---

## Mathematical formulation

### Regularized objective

For each new tree $f_t$, XGBoost minimizes a second-order Taylor approximation of the loss plus an explicit complexity penalty:

$$\mathcal{L}^{(t)} \approx \sum_{i=1}^{n}\left[g_i f_t(x_i) + \frac{1}{2}h_i f_t(x_i)^2\right] + \Omega(f_t), \qquad \Omega(f_t) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^{T} w_j^2$$

where $g_i = \partial L(y_i, \hat{y}_i^{(t-1)}) / \partial \hat{y}_i^{(t-1)}$ and $h_i = \partial^2 L / \partial (\hat{y}_i^{(t-1)})^2$ are the **first and second derivatives** (gradient and Hessian) of the loss at the current prediction, $T$ is the number of leaves, and $w_j$ is leaf $j$'s predicted value. Using both the gradient *and* the Hessian (a Newton's-method-style step, not just gradient descent) is what lets the same framework support any twice-differentiable loss with the closed-form solution below — including plain squared error, where $h_i = 1$ for every point, making the formulas collapse to something directly comparable to plain gradient boosting (see [Simple example](#simple-example)).

### Optimal leaf weight and split gain

For a fixed tree structure, the optimal weight for leaf $j$ (with gradient/Hessian sums $G_j=\sum_{i \in j} g_i$, $H_j=\sum_{i \in j} h_i$ over the points landing in it) is:

$$w_j^* = -\frac{G_j}{H_j + \lambda}$$

— note the $\lambda$ in the denominator: larger `reg_lambda` shrinks every leaf's value toward zero, on top of whatever `learning_rate` already does. The gain from splitting a node into left/right children is:

$$\text{Gain} = \frac{1}{2}\left[\frac{G_L^2}{H_L+\lambda} + \frac{G_R^2}{H_R+\lambda} - \frac{G^2}{H+\lambda}\right] - \gamma$$

The $-\gamma$ term means a split is only made **if it improves the regularized objective by more than $\gamma$** — unlike a plain decision tree or gradient boosting tree, which will take any split that reduces impurity/SSE at all (down to `min_samples_split`/`min_samples_leaf` limits), XGBoost can refuse to split a node outright if the split isn't worth its complexity cost. This is `gamma`, effectively pruning during tree construction rather than only after.

### Practical engineering (why it's fast)

Beyond the math above, XGBoost's speed comes from engineering: **histogram-based split finding** (bucketing continuous features into a fixed number of bins so candidate thresholds are cheap to evaluate), **parallelizing the search for the best split across features** within a single tree (the sequential dependency is only *across* trees, same as any gradient boosting method — not within one), and a **learned default direction for missing values** at each split, so missing data doesn't need to be imputed beforehand.

---

## Typical hyperparameters

### `n_estimators` / `learning_rate`

Same meaning and same tuning relationship as in plain [Gradient Boosting](../11.gradient-boosting/README.md#typical-hyperparameters) — tuned jointly, usually with early stopping.

```python
XGBRegressor(n_estimators=100, learning_rate=0.1)
```

### `max_depth`

Same meaning as before, but XGBoost's regularization (`reg_lambda`, `gamma`) does some of the overfitting-control work that depth limits alone have to do in plain gradient boosting, so effective defaults can differ between the two.

### `reg_lambda` (L2) and `reg_alpha` (L1)

Direct penalties on leaf weight magnitude, per [Mathematical formulation](#mathematical-formulation) — `reg_lambda` (default `1`) shrinks all leaf weights smoothly toward zero; `reg_alpha` (default `0`) can shrink some leaf weights exactly to zero, similar in spirit to Lasso vs. Ridge in [Logistic Regression](../2.logistic-regression/README.md#typical-hyperparameters).

```python
XGBRegressor(reg_lambda=1.0, reg_alpha=0.0)
```

### `gamma`

Minimum gain required to make a split (default `0`, meaning no extra pruning threshold beyond the gain formula itself). Larger values make the tree more conservative about adding leaves.

### `subsample` / `colsample_bytree`

Fraction of rows, and fraction of features, sampled for each tree — the same stochastic-boosting idea as scikit-learn's `subsample`, plus a random-forest-style random feature subset per tree on top.

### `min_child_weight`

Minimum sum of Hessian ($H_j$ above) required in a leaf — for squared error loss where every point's Hessian is 1, this is equivalent to a minimum sample count per leaf; for other losses it weights points by how much curvature/confidence they contribute.

### Modeling choices that matter more than any single constructor argument

- `n_estimators` + `learning_rate` tuned together with early stopping (`eval_set`, `early_stopping_rounds`), same as plain gradient boosting.
- Whether `reg_lambda`/`reg_alpha`/`gamma` are left at defaults or actively tuned — this is XGBoost's main practical advantage over plain gradient boosting, and leaving it entirely at defaults gives up much of that advantage.
- Being aware that **`base_score` has historically defaulted to `0.5`** regardless of the target's actual scale (rather than the target mean, which is what plain gradient boosting starts from) — a well-known gotcha that can slow early convergence on regression targets far from 0.5; explicitly setting `base_score` to the target mean, or relying on enough boosting rounds to correct for it, avoids the surprise.

---

## Advantages

**Regularization is part of tree construction itself**, not just an after-the-fact shrinkage factor — often measurably better generalization than plain gradient boosting for the same amount of tuning effort.

**Fast**, via histogram-based split finding and within-tree parallelism across features, especially relative to scikit-learn's exact-split-search `GradientBoostingRegressor`.

**Handles missing values natively** — no imputation step required, since each split learns which direction (left or right) a missing value should default to.

**Extremely well-established for tabular data**, with correspondingly extensive tooling, documentation, and community tuning wisdom.

**Flexible objective/evaluation support** — built-in objectives cover regression, classification, and ranking, and custom objectives/eval metrics are supported for less standard problems.

---

## Limitations

**More hyperparameters than plain gradient boosting** — `reg_lambda`, `reg_alpha`, `gamma`, and `min_child_weight` add real tuning surface area on top of `n_estimators`, `learning_rate`, and `max_depth`, and they interact with each other.

**An external dependency, not part of scikit-learn** — a separate library to install, version, and keep compatible with the rest of a scikit-learn-based pipeline (though its estimator API is designed to slot in interchangeably).

**Still inherits gradient boosting's general risks** — sequential training that doesn't parallelize across trees, sensitivity to too many estimators/too high a learning rate, poor extrapolation, and limited interpretability without an add-on like SHAP.

**The `base_score` default is a real, easy-to-hit gotcha** — see [Typical hyperparameters](#typical-hyperparameters); it's not a bug, but it surprises people who assume it behaves like scikit-learn's mean-based initialization.

**Can still overfit** despite the added regularization — `reg_lambda`/`reg_alpha`/`gamma` reduce the risk relative to plain gradient boosting, they don't eliminate the need for validation-based tuning and/or early stopping.

---

## Simple example

Reusing the same tiny regression dataset from [Gradient Boosting](../11.gradient-boosting/README.md#simple-example):

| $x$ | $y$ |
|---:|---:|
| 1 | 1 |
| 2 | 2 |
| 3 | 6 |
| 4 | 8 |
| 5 | 4 |
| 6 | 5 |

With `base_score` set explicitly to $\bar{y}=4.333$ (see the gotcha above), `learning_rate=1.0`, `max_depth=1`, and `reg_lambda=1` (default), squared error loss gives every point a Hessian $h_i=1$ and gradient $g_i = F_0 - y_i$ — for example, $g_1 = 4.333 - 1 = 3.333$.

**Stage 1:** the split $x \leq 2.5$ vs. $x > 2.5$ maximizes the regularized gain (same threshold plain gradient boosting found, since the two classes here are cleanly separated). With $G_L=-5.667, H_L=2$ on the left and $G_R=5.667, H_R=4$ on the right:

$$w_L^* = -\frac{-5.667}{2+1} = -1.889, \qquad w_R^* = -\frac{5.667}{4+1} = 1.133$$

Compare this to plain gradient boosting's unregularized leaf values for the same split, $-2.833$ and $1.417$ — XGBoost's $\lambda=1$ visibly shrinks both leaf values toward zero. Adding these to $F_0$:

$$F_1(x) = [2.444,\ 2.444,\ 5.467,\ 5.467,\ 5.467,\ 5.467]$$

**Stage 2:** recomputing gradients against $F_1$ and repeating gives the best split at $x \leq 4.5$, with leaf weights $w_L^*=0.236$, $w_R^*=-0.644$, producing:

$$F_2(x) = [2.68,\ 2.68,\ 5.702,\ 5.702,\ 4.822,\ 4.822]$$

### Python example

See [`xgboost_example.py`](xgboost_example.py) for the runnable version (requires `pip install xgboost`):

```python
import numpy as np
from xgboost import XGBRegressor

X = np.array([[1], [2], [3], [4], [5], [6]])
y = np.array([1, 2, 6, 8, 4, 5])

# base_score set explicitly to the target mean (see README's base_score
# gotcha); reg_lambda=1 is XGBoost's default, shown explicitly here since
# it's exactly what produces the shrunk leaf values in the hand-derivation.
model = XGBRegressor(
    n_estimators=2, learning_rate=1.0, max_depth=1,
    reg_lambda=1.0, base_score=float(np.mean(y)),
)
model.fit(X, y)

# predict() with iteration_range gives the ensemble's output after each stage.
for stage in range(1, 3):
    preds = model.predict(X, iteration_range=(0, stage))
    print(f"After stage {stage}:", preds)
```

Expected output (matches the hand-derived stage-by-stage predictions above):

```text
After stage 1: [2.4444444 2.4444444 5.4666667 5.4666667 5.4666667 5.4666667]
After stage 2: [2.68      2.68      5.7022223 5.7022223 4.8222222 4.8222222]
```

---

## Resources

- [XGBoost Python API documentation](https://xgboost.readthedocs.io/en/stable/python/python_api.html) — `XGBRegressor`/`XGBClassifier` parameters and methods.
- [XGBoost introduction to boosted trees](https://xgboost.readthedocs.io/en/stable/tutorials/model.html) — the official derivation of the regularized objective, gain formula, and optimal leaf weight, matching the notation used above.
- [Chen & Guestrin, "XGBoost: A Scalable Tree Boosting System" (2016)](https://arxiv.org/abs/1603.02754) — the original paper, including the systems-level optimizations (histogram binning, sparsity-aware split finding).
- [Gradient Boosting](../11.gradient-boosting/README.md) in this index — the unregularized version of the same core algorithm, useful for seeing exactly what XGBoost adds.

### Core fact to retain

> XGBoost is gradient boosting with an explicit complexity penalty built into both the split-gain formula and the optimal leaf value — the same sequential residual-correction idea, but regularized and engineered for speed from the ground up.
