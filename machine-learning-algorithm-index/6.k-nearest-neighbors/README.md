# K-Nearest Neighbors (KNN)

## Overview

K-nearest neighbors is a **supervised learning algorithm** for classification or regression that makes no assumptions about the data's underlying shape at all — it simply looks up the $k$ **closest training points** to a new observation and predicts based on them (majority class vote for classification, average target for regression).

It's the simplest possible instance-based ("lazy") learner: there is no training phase in the usual sense — "fitting" a KNN model just means storing the training data. All the work happens at prediction time.

---

## Intuition

To classify a new point, measure its distance to every training point, take the $k$ nearest, and let them vote. If most of a new patient's $k$ nearest neighbors (by lab values, age, etc.) had a condition, predict that the new patient does too.

$k$ controls the smoothness of the decision boundary:

- **Small $k$** (e.g., $k=1$): the boundary hugs individual training points tightly — very flexible, very sensitive to noise (a single mislabeled or unusual point can flip a prediction).
- **Large $k$**: predictions are smoothed over more neighbors — more stable, but can wash out real local structure and, taken to the extreme, just predicts the global majority class everywhere.

This is the same bias-variance trade-off that shows up everywhere else in this index, just controlled by a neighborhood size instead of a regularization strength or tree depth.

---

## Mathematical formulation

### Distance metric

Most commonly **Euclidean distance**:

$$d(x_a, x_b) = \sqrt{\sum_{j=1}^{p} (x_{aj} - x_{bj})^2}$$

though **Manhattan distance** ($\sum_j |x_{aj}-x_{bj}|$) and other metrics (Minkowski generalizes both) are common alternatives, especially for high-dimensional or non-continuous features.

### Prediction rule

For classification, given the $k$ nearest neighbors' labels $y_{(1)}, \ldots, y_{(k)}$:

$$\hat{y} = \text{mode}\{y_{(1)}, \ldots, y_{(k)}\}$$

optionally **distance-weighted**, so closer neighbors count more:

$$\hat{y} = \arg\max_{c} \sum_{i:\, y_{(i)}=c} \frac{1}{d(x, x_{(i)})}$$

For regression, replace the mode with a (optionally distance-weighted) mean of the neighbors' target values.

### Why scale matters

Because prediction is entirely distance-based, a feature measured in the thousands (e.g., income in dollars) will dominate a feature measured in single digits (e.g., years of experience) unless features are standardized first — a raw Euclidean distance calculation would treat a \$1,000 difference in income as "bigger" than a 10-year difference in experience regardless of which one actually matters more.

---

## Typical hyperparameters

### `n_neighbors`

The $k$ in KNN. Default is `5`. Chosen via cross-validation in practice; odd values are common for binary classification to avoid tied votes.

```python
KNeighborsClassifier(n_neighbors=5)
```

### `weights`

`"uniform"` (default, every neighbor's vote counts equally) or `"distance"` (closer neighbors count more, per [Mathematical formulation](#mathematical-formulation)).

```python
KNeighborsClassifier(weights="distance")
```

### `metric`

The distance function: `"minkowski"` (default, with `p=2` this is Euclidean, `p=1` is Manhattan), or others like `"cosine"` for text/embedding data where direction matters more than magnitude.

### `algorithm`

How neighbors are actually found at prediction time: `"brute"` (compute all pairwise distances — always correct, but $O(n)$ per query), or spatial index structures `"kd_tree"` / `"ball_tree"` that make lookup sublinear on low-to-moderate-dimensional data. `"auto"` (default) picks based on the data.

### Modeling choices that matter more than any single constructor argument

- **Feature scaling** (see [Mathematical formulation](#mathematical-formulation)) — arguably more important here than for any other algorithm in this index, since there's no learned weight per feature to compensate for scale differences.
- Choice of $k$ relative to dataset size and noise level — there's no default that's broadly safe the way, say, `LinearRegression()`'s defaults are.
- Dimensionality — see [Limitations](#limitations); KNN degrades as the number of features grows, sometimes badly.

---

## Advantages

**No training phase and no distributional assumptions** — it can represent arbitrarily complex decision boundaries directly from the data, unconstrained by a parametric form (unlike linear/logistic regression).

**Simple to understand and explain** — "it predicted this because these were the most similar past examples" is an intuitive, auditable explanation.

**Naturally multiclass** — the voting mechanism extends to any number of classes with no special handling, unlike SVM's need for one-vs-rest/one-vs-one wrappers.

**Effective as a quick baseline** on small-to-medium, low-dimensional datasets where "similar inputs should have similar outputs" is a reasonable assumption.

---

## Limitations

**Prediction is slow and memory-heavy at scale** — with no real training step, every prediction requires a search over (some or all of) the stored training set; both prediction time and memory scale with the size of the training data, unlike a fitted linear model or tree, whose prediction cost doesn't depend on how much data it was trained on.

**The curse of dimensionality** — as the number of features grows, distances between points become increasingly similar to one another (everything ends up "far away" and roughly equidistant), making "nearest" a much less meaningful concept. KNN tends to degrade faster than model-based methods in high dimensions unless dimensionality is reduced first (see [Principal Component Analysis](../10.principal-component-analysis/README.md)).

**Requires feature scaling**, as discussed above — an easy thing to forget since nothing in the API forces it.

**Sensitive to irrelevant features** — because every feature contributes to the distance calculation, adding noisy or irrelevant features actively degrades performance, unlike a tree, which can simply ignore a useless feature by never splitting on it.

**Sensitive to class imbalance** — in an imbalanced dataset, a query point's nearest neighbors are more likely to belong to the majority class purely by virtue of there being more of them nearby, independent of whether that's the correct prediction.

**No model to inspect** — there are no coefficients, no tree structure, nothing learned to interpret beyond "here are the stored training points."

---

## Simple example

Two well-separated 2-D clusters, and a query point to classify:

| $x_1$ | $x_2$ | Class |
|---:|---:|---:|
| 1 | 2 | 0 |
| 2 | 3 | 0 |
| 2 | 1 | 0 |
| 3 | 2 | 0 |
| 6 | 5 | 1 |
| 7 | 7 | 1 |
| 8 | 6 | 1 |
| 6 | 8 | 1 |

Query point: $(5, 5)$. Computing Euclidean distance from the query to every training point and sorting:

| Point | Class | Distance |
|---|---:|---:|
| (6, 5) | 1 | 1.000 |
| (7, 7) | 1 | 2.828 |
| (6, 8) | 1 | 3.162 |
| (8, 6) | 1 | 3.162 |
| (2, 3) | 0 | 3.606 |
| (3, 2) | 0 | 3.606 |
| (1, 2) | 0 | 5.000 |
| (2, 1) | 0 | 5.000 |

For $k=1$, $k=3$, or $k=5$, the nearest neighbors are all (or mostly) class 1, so the prediction is **class 1** regardless of which $k$ is chosen here — a case where the classes are separated cleanly enough that $k$ doesn't matter much. (Note the exact tie in distance between (6, 8) and (8, 6) at $k=3$'s boundary — both are class 1, so it doesn't change the vote here, but ties are a real thing KNN has to break somehow, typically by insertion order rather than anything meaningful.)

### Python example

See [`k_nearest_neighbors.py`](k_nearest_neighbors.py) for the runnable version:

```python
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

X = np.array([[1, 2], [2, 3], [2, 1], [3, 2],
              [6, 5], [7, 7], [8, 6], [6, 8]])
y = np.array([0, 0, 0, 0, 1, 1, 1, 1])

model = KNeighborsClassifier(n_neighbors=3)
model.fit(X, y)

query = np.array([[5, 5]])
distances, indices = model.kneighbors(query)

print("Distances to 3 nearest neighbors:", distances[0])
print("Prediction for (5, 5):", model.predict(query)[0])
```

Expected output (distances independently hand-computed above):

```text
Distances to 3 nearest neighbors: [1.         2.82842712 3.16227766]
Prediction for (5, 5): 1
```

---

## Resources

- [Scikit-learn `KNeighborsClassifier` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html) — parameters, distance metrics, and the `algorithm` options.
- [Scikit-learn nearest neighbors user guide](https://scikit-learn.org/stable/modules/neighbors.html) — KD-tree/ball-tree internals and complexity trade-offs.
- [Cover & Hart, "Nearest Neighbor Pattern Classification" (1967)](https://ieeexplore.ieee.org/document/1053964) — the original theoretical analysis.
- [*The Elements of Statistical Learning*, Ch. 13](https://link.springer.com/book/10.1007/978-0-387-84858-7) — KNN and the curse of dimensionality in the broader context of local methods.

### Core fact to retain

> KNN makes no assumptions about the relationship between features and target — it just asks "what happened to similar points before?" — which makes it flexible and easy to explain, but slow at prediction time and increasingly unreliable as the number of features grows.
