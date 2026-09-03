# Principal Component Analysis (PCA)

## Overview

PCA is an **unsupervised algorithm** for **dimensionality reduction**: given data with many (possibly correlated) features, it finds a smaller set of new, uncorrelated features — the **principal components** — that are linear combinations of the originals and capture as much of the data's variance as possible.

It's used for:

- Compressing high-dimensional data before feeding it to another model (mitigating the [curse of dimensionality](../6.k-nearest-neighbors/README.md#limitations) that hurts KNN, for instance)
- Visualizing high-dimensional data in 2 or 3 dimensions
- Removing multicollinearity among features before linear/logistic regression
- Noise reduction, by keeping only the components that capture the bulk of the signal

---

## Intuition

Imagine a scatter of points that roughly forms an elongated cloud, tilted diagonally. Describing each point by its original $(x, y)$ coordinates works, but a lot of the spread in $x$ and the spread in $y$ is really the *same* underlying variation — points that are high in $x$ also tend to be high in $y$.

PCA finds a new axis — a direction in the data — along which the points are spread out the most. That direction is the **first principal component**. The second principal component is the direction of next-most spread, constrained to be perpendicular (uncorrelated) to the first, and so on. Rotating the data onto these new axes doesn't lose any information by itself (with as many components as original features, it's just a rotation) — the dimensionality reduction comes from then **keeping only the first few components** and discarding the rest, on the assumption that they capture only noise or negligible variation.

---

## Mathematical formulation

### Covariance matrix

For centered data (mean-subtracted so each feature has mean 0), the $p \times p$ covariance matrix $\Sigma$ captures how every pair of features co-varies:

$$\Sigma_{jk} = \frac{1}{n-1}\sum_{i=1}^{n} x_{ij}x_{ik}$$

The diagonal holds each feature's variance; the off-diagonal entries hold covariances between feature pairs.

### Eigendecomposition

The principal components are the **eigenvectors** of $\Sigma$, and each component's captured variance is its corresponding **eigenvalue**:

$$\Sigma v_j = \lambda_j v_j$$

Sorting eigenvectors by eigenvalue (largest first) orders the components from most to least variance explained. The eigenvectors of a covariance matrix are guaranteed orthogonal (uncorrelated), which is exactly the property that makes the new axes non-redundant.

(In practice, PCA is computed via the **singular value decomposition (SVD)** of the centered data matrix directly, rather than explicitly forming the covariance matrix and eigendecomposing it — mathematically equivalent, but more numerically stable. scikit-learn uses SVD internally.)

### Explained variance ratio

$$\text{explained variance ratio of component } j = \frac{\lambda_j}{\sum_{k=1}^{p}\lambda_k}$$

This is what a scree plot shows: how much of the total variance each successive component accounts for, used to decide how many components to keep.

### Projection

A data point $x$ is projected onto the first $m$ components by taking its dot product with each retained eigenvector:

$$z_j = x \cdot v_j, \qquad j = 1, \ldots, m$$

giving the point's coordinates $z = (z_1, \ldots, z_m)$ in the new, reduced-dimensional space.

---

## Typical hyperparameters

### `n_components`

How many components to keep. Can be an integer (keep exactly that many), a float between 0 and 1 (keep however many components are needed to explain at least that fraction of total variance — e.g., `0.95`), or omitted (keeps all components, useful for inspecting the full explained-variance ratio before deciding).

```python
PCA(n_components=2)
```

### `svd_solver`

The numerical method used. `"auto"` (default) picks based on data size; `"full"` computes the exact SVD; `"randomized"` uses a faster approximate method, worthwhile on large, high-dimensional data when only a small number of components are needed.

### `whiten`

If `True`, additionally scales each component to unit variance. Occasionally useful as a preprocessing step for algorithms sensitive to the relative scale of input features, at the cost of discarding the components' relative variance information.

### Modeling choices that matter more than any single constructor argument

- **Standardizing features before PCA** — PCA is variance-based, so a feature with a much larger raw scale (and therefore artificially larger variance) will dominate the first component regardless of whether it's actually more informative, unless features are standardized first (`StandardScaler`).
- How many components to keep — driven by the explained variance ratio and the downstream use case (visualization essentially requires 2–3; a modeling preprocessing step can often keep far more).
- Whether linear PCA is appropriate at all, versus a nonlinear alternative (e.g., kernel PCA, t-SNE, UMAP) when the data's structure isn't well captured by linear combinations of features.

---

## Advantages

**Reduces dimensionality without discarding features arbitrarily** — rather than dropping specific original features outright, it finds the combinations of all of them that matter most.

**Removes multicollinearity by construction** — the resulting components are mathematically guaranteed to be uncorrelated with one another, which can help linear/logistic regression's coefficient stability (see [Linear Regression: Limitations](../1.linear-regression/README.md#limitations)).

**Enables visualization of high-dimensional data** by projecting down to 2–3 dimensions while retaining as much structure as a linear projection can.

**Can reduce noise and overfitting risk** in downstream models by dropping low-variance components that often correspond to noise rather than signal.

**Speeds up downstream algorithms** that scale with feature count, and directly helps distance-based methods (KNN, k-means, SVM) suffering from the curse of dimensionality.

---

## Limitations

**Components are linear combinations of all original features**, which usually makes them hard to interpret directly — "principal component 1" is rarely a clean, nameable concept the way an original feature was, unlike a decision tree's splits or a regression's coefficients.

**Only captures linear structure** — if the data's real structure is nonlinear (e.g., points lying on a curved manifold), PCA's straight-line projections can badly distort or fail to separate it; kernel PCA or manifold learning methods exist for exactly this reason.

**Sensitive to feature scaling** — see [Typical hyperparameters](#typical-hyperparameters); skipping standardization is one of the most common ways to get a misleading PCA result.

**Maximizing variance isn't the same as maximizing predictive or class-discriminative information** — a component can capture a lot of variance while being nearly useless for a downstream classification task, and vice versa; for supervised dimensionality reduction, Linear Discriminant Analysis is a more targeted alternative.

**Sensitive to outliers** — since it's built from variances and covariances (both mean-based, squared quantities), a handful of extreme points can dominate and distort the first component's direction.

**Loses information whenever components are dropped**, by design — the only question is whether what's dropped was signal or noise, which PCA itself doesn't know; that judgment is left to the modeler.

---

## Simple example

A classic small dataset for illustrating PCA (10 points, 2 features):

| $x$ | $y$ |
|---:|---:|
| 2.5 | 2.4 |
| 0.5 | 0.7 |
| 2.2 | 2.9 |
| 1.9 | 2.2 |
| 3.1 | 3.0 |
| 2.3 | 2.7 |
| 2.0 | 1.6 |
| 1.0 | 1.1 |
| 1.5 | 1.6 |
| 1.1 | 0.9 |

Centering the data (mean $\approx (1.81, 1.91)$) and computing the sample covariance matrix:

```math
\Sigma =
\begin{pmatrix}
0.6166 & 0.6154 \\
0.6154 & 0.7166
\end{pmatrix}
```

Solving for the eigenvalues of this $2 \times 2$ symmetric matrix, using

```math
\lambda =
\frac{\mathrm{tr}(\Sigma)}{2}
\pm
\sqrt{\left(\frac{a-d}{2}\right)^2 + b^2}
```

for

```math
\Sigma =
\begin{pmatrix}
a & b \\
b & d
\end{pmatrix},
```

gives:

```math
\lambda_1 \approx 1.2840,
\qquad
\lambda_2 \approx 0.0491
```

so the first component alone explains

```math
\frac{1.2840}{1.2840 + 0.0491} \approx 96.3\%
```

of the total variance — consistent with the data visibly lying close to a single diagonal line.

The corresponding unit-length eigenvector for $\lambda_1$ is approximately $(0.6779, 0.7352)$, and projecting the first centered data point, $(0.69, 0.49)$, onto it:

```math
z_1 =
0.69 \times 0.6779 +
0.49 \times 0.7352
\approx 0.828
```

### Python example

See [`principal_component_analysis.py`](principal_component_analysis.py) for the runnable version:

```python
import numpy as np
from sklearn.decomposition import PCA

X = np.array([
    [2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], [3.1, 3.0],
    [2.3, 2.7], [2.0, 1.6], [1.0, 1.1], [1.5, 1.6], [1.1, 0.9],
])

model = PCA(n_components=2)
X_transformed = model.fit_transform(X)

print("Explained variance ratio:", model.explained_variance_ratio_)
print("First principal component direction:", model.components_[0])
print("First data point's PC1 score:", X_transformed[0, 0])
```

Expected output (matches the hand-computed eigenvalues/eigenvector/projection above; scikit-learn
may report the eigenvector with the opposite sign — an arbitrary, equally valid choice of
direction along the same axis — which would flip the sign of every projected score too):

```text
Explained variance ratio: [0.96318131 0.03681869]
First principal component direction: [0.6778734  0.73517866]
First data point's PC1 score: 0.8279701825211814
```

---

## Resources

- [Scikit-learn `PCA` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html) — parameters, attributes, and the SVD-based implementation.
- [Scikit-learn decomposition user guide](https://scikit-learn.org/stable/modules/decomposition.html#pca) — relationship to SVD, whitening, and randomized solvers.
- [Smith, "A Tutorial on Principal Component Analysis" (2002)](https://www.cs.otago.ac.nz/cosc453/student_tutorials/principal_components.pdf) — source of the worked 10-point example reproduced above, with the full derivation.
- [*The Elements of Statistical Learning*, Ch. 14.5](https://link.springer.com/book/10.1007/978-0-387-84858-7) — PCA within the broader context of dimensionality reduction methods.

### Core fact to retain

> PCA rotates the data onto new, uncorrelated axes ordered by how much variance each one explains — dimensionality reduction happens by keeping only the top few axes, which only works well if most of the meaningful signal really does live in high-variance directions.
