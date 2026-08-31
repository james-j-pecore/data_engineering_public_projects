# Random Forest

## Overview

A random forest is a **supervised learning algorithm** — for classification or regression — that fits **many decision trees** on randomized variants of the training data and **averages their predictions** (majority vote for classification, mean for regression). It's an **ensemble method** built directly on top of [Decision Tree](../3.decision-tree/README.md): same base learner, different training recipe.

The motivation is the single biggest weakness of an individual decision tree — high variance (see [Decision Tree: Limitations](../3.decision-tree/README.md#limitations)) — a single tree changes a lot if the training data changes slightly. Random forest cancels out that instability by averaging over many trees that are each a little different from one another, without meaningfully increasing bias.

---

## Intuition

Two sources of randomness turn "a bunch of decision trees" into "a random forest":

**1. Bagging (bootstrap aggregating).** Each tree is trained on a *bootstrap sample* — a sample of the same size as the training set, drawn **with replacement**. Roughly 63% of the original rows appear (some more than once) in any given bootstrap sample, and the remaining ~37% are left out — those left-out rows are used for a free internal validation estimate (see [out-of-bag error](#out-of-bag-oob-error) below).

**2. Random feature subsets.** At each split, instead of considering every feature (as a single decision tree does), each tree only considers a random subset of features (`max_features`). This decorrelates the trees — if one feature is very strong, bagging alone would still make most trees split on it first, keeping the trees highly correlated with each other and limiting the variance reduction from averaging.

Why averaging helps: if $B$ trees each have prediction variance $\sigma^2$ and were fully independent, the variance of their average would be $\sigma^2/B$ — averaging many noisy-but-unbiased estimators produces a much less noisy one. Real trees in a forest aren't fully independent (they're trained on overlapping, correlated data), so the variance reduction is smaller than a naive $1/B$ but still substantial — which is exactly why random feature subsets matter: less correlation between trees means the averaging benefit is closer to that ideal.

### Out-of-bag (OOB) error

Because each tree only trains on ~63% of the rows, the other ~37% can be used to evaluate that tree without a separate holdout set. Averaging each row's predictions from only the trees that didn't see it during training gives the **out-of-bag error** — a built-in, no-extra-cost approximation of cross-validated performance (`oob_score=True` in scikit-learn).

---

## Mathematical formulation

### Prediction

For classification, with $B$ trees $T_1, \ldots, T_B$:

$$\hat{y} = \text{mode}\{T_1(x), \ldots, T_B(x)\}$$

(scikit-learn actually averages each tree's predicted class *probabilities* and takes the argmax, which is a softer version of a majority vote.) For regression:

$$\hat{y} = \frac{1}{B}\sum_{b=1}^{B} T_b(x)$$

### Each tree's split criterion

Unchanged from a single decision tree — Gini impurity or entropy for classification, variance/MSE reduction for regression (see [Decision Tree: Mathematical formulation](../3.decision-tree/README.md#mathematical-formulation)) — just applied to a bootstrap sample and a random feature subset at each split, rather than the full data and all features.

### Feature importance

Scikit-learn's default (`feature_importances_`) is the **mean decrease in impurity (MDI)**: for each feature, sum the impurity reduction it produced across every split, in every tree, weighted by how many samples reached that split, then average over trees. It's fast to compute but biased toward high-cardinality and continuous features; **permutation importance** (shuffle one feature's values and measure the resulting drop in held-out accuracy) is a more reliable, if slower, alternative.

---

## Typical hyperparameters

### `n_estimators`

Number of trees. More trees essentially never hurts (only costs compute) — unlike boosting, adding more trees to a random forest does not overfit, it just gives a more stable average that eventually plateaus.

```python
RandomForestClassifier(n_estimators=200)
```

### `max_depth` / `min_samples_leaf`

Same meaning as in a single decision tree, applied per-tree. Random forests are often used with deeper, less-pruned trees than would be sensible standalone — since averaging handles the variance, individual trees are allowed to overfit somewhat.

### `max_features`

Number of features considered at each split. Scikit-learn defaults to `"sqrt"` for classification ($\sqrt{p}$ features out of $p$) and `1.0` (all features) for regression. Smaller values decorrelate trees more (see [Intuition](#intuition)) at some cost to each individual tree's fit.

```python
RandomForestClassifier(max_features="sqrt")
```

### `bootstrap` / `oob_score`

Whether to bootstrap-sample each tree's training set (`True`, the default and the "random forest" behavior) and whether to compute the free out-of-bag score described above.

```python
RandomForestClassifier(bootstrap=True, oob_score=True)
```

### `n_jobs`

Trees are trained independently, so fitting parallelizes trivially across cores; `n_jobs=-1` uses all of them.

### Modeling choices that matter more than any single constructor argument

- `n_estimators` large enough that the OOB/CV score has visibly plateaued, not just "a round number"
- Whether the dataset actually benefits from an ensemble at all — on simple, low-dimensional, low-noise problems a single well-tuned tree (or even logistic regression) can match a random forest with far less compute (see [Simple example](#simple-example))
- Class imbalance handling (`class_weight="balanced"`), same consideration as [Logistic Regression](../2.logistic-regression/README.md#limitations)

---

## Advantages

**Substantially lower variance than a single decision tree**, usually without a meaningful increase in bias — the direct fix for a single tree's main weakness.

**Handles nonlinearities and interactions** the same way a single tree does, but more robustly.

**Requires little preprocessing** — no feature scaling, and reasonably tolerant of irrelevant features (though not immune to them).

**Built-in validation signal** via out-of-bag error, without holding out a separate validation set.

**Provides a usable feature importance ranking** out of the box, useful for exploratory analysis even when the model itself isn't the final deliverable.

**Parallelizes trivially** across CPU cores since trees are trained independently.

---

## Limitations

**Less interpretable than a single tree** — you can no longer draw the whole model as one flowchart; a forest of hundreds of trees is closer to a black box, mitigated only by feature importances and tools like SHAP.

**Larger memory and compute footprint** — storing and querying hundreds of trees costs meaningfully more than one, both at training and prediction time.

**Weaker than boosting on many tabular benchmarks** — random forest reduces variance but doesn't iteratively correct its own mistakes the way [Gradient Boosting](../11.gradient-boosting/README.md)/[XGBoost](../12.xgboost/README.md) do; boosted trees frequently outperform random forests on structured/tabular data given proper tuning.

**Extrapolates poorly**, inheriting this from its tree base learners — predictions are bounded by the range of the training targets (regression) and can't represent a trend beyond the training data's feature range.

**Feature importance can mislead** — MDI importance is biased toward high-cardinality and continuous features (see [Mathematical formulation](#mathematical-formulation)), and correlated features split importance between them, making any single feature look less important than it is.

**Diminishing, not zero, benefit on simple problems** — if the true relationship is simple enough for one shallow tree (or even a linear model) to capture, an ensemble mainly adds compute cost, not accuracy (see [Simple example](#simple-example)).

---

## Simple example

The averaging mechanism, in miniature: suppose 5 decision stumps are each trained on a different bootstrap resample of a noisy dataset, and for some particular input $x$, they individually predict:

$$1, 1, 0, 1, 0$$

A majority vote gives $\hat{y} = 1$ (3 votes to 2), and — this is the actual point of the exercise — that vote is more stable across new bootstrap resamples than any single stump's prediction would be, precisely because it takes agreement among several independently-noisy trees to flip.

### Python example

See [`random_forest.py`](random_forest.py) for the runnable version, applied to the same hours-studied-vs-pass dataset used in [Logistic Regression](../2.logistic-regression/README.md) and [Decision Tree](../3.decision-tree/README.md):

```python
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

X = np.array([[0.5], [0.75], [1.0], [1.25], [1.5], [1.75], [1.75], [2.0],
              [2.25], [2.5], [2.75], [3.0], [3.25], [3.5], [4.0], [4.25],
              [4.5], [4.75], [5.0], [5.5]])
y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])

model = RandomForestClassifier(n_estimators=200, oob_score=True, random_state=42)
model.fit(X, y)

predictions = model.predict(X)
print("Training accuracy:", accuracy_score(y, predictions))
print("Out-of-bag accuracy:", model.oob_score_)
```

**Note on expected output:** unlike the earlier linear/logistic/decision-tree examples, this
one isn't hand-verified to an exact number — a random forest's fit depends on scikit-learn's
internal bootstrap and feature-subsampling RNG, which isn't practical to reproduce by hand.
Run it yourself to see the actual figures. Qualitatively, expect training accuracy at or above
the single stump's 0.8 from [Decision Tree](../3.decision-tree/README.md#simple-example), and
an OOB accuracy in the same neighborhood — this single-feature, low-noise dataset is exactly the
"simple enough for one tree" case from [Limitations](#limitations), so 200 trees shouldn't be
expected to outperform one stump by much here. Random forest's advantage shows up on
higher-dimensional, noisier data, not on a toy like this one.

---

## Resources

- [Scikit-learn `RandomForestClassifier` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) — parameters, attributes, OOB scoring.
- [Scikit-learn ensemble methods guide](https://scikit-learn.org/stable/modules/ensemble.html#random-forests) — bagging vs. boosting, feature importance caveats.
- [Breiman, "Random Forests" (2001)](https://link.springer.com/article/10.1023/A:1010933404324) — the original paper.
- [*The Elements of Statistical Learning*, Ch. 15](https://link.springer.com/book/10.1007/978-0-387-84858-7) — random forests within the broader ensemble-methods framework, including variance/bias analysis.

### Core fact to retain

> Random forest trades a single decision tree's instability for the stability of averaging many decorrelated trees — bootstrap sampling plus random feature subsets at each split — at the cost of interpretability and compute.
