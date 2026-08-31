# K-Means Clustering

## Overview

K-means is an **unsupervised learning algorithm** — the first one in this index — used for **clustering**: grouping data points into $k$ clusters based on similarity, with no labels provided at all. Every other algorithm covered so far learns to predict a known target; k-means instead discovers structure in unlabeled data by partitioning points so that points within a cluster are close to each other and far from points in other clusters.

Examples include:

- Grouping customers into segments by purchase behavior, with no predefined segment labels
- Compressing an image's colors down to $k$ representative colors
- Finding groups of similar documents by their feature vectors, as a preprocessing step before further analysis

---

## Intuition

Pick $k$ (the number of clusters), then alternate between two simple steps until nothing changes:

1. **Assign** every point to its nearest of the $k$ current cluster centers (centroids).
2. **Update** each centroid to be the mean of the points now assigned to it.

This is exactly [K-Nearest Neighbors](../6.k-nearest-neighbors/README.md)'s "nearest point wins" logic, run against a small set of *evolving* reference points instead of a fixed labeled training set, repeated until the assignments stop changing.

Because each step (assign to reduce within-cluster distance, then re-center to also reduce it) can only decrease or hold steady the total within-cluster distance, never increase it, this process is **guaranteed to converge** — though not necessarily to the best possible clustering (see [Limitations](#limitations)).

---

## Mathematical formulation

### Objective: minimize within-cluster variance

K-means minimizes the total squared distance from each point to its assigned cluster's centroid — the **inertia**, or within-cluster sum of squares (WCSS):

$$J = \sum_{i=1}^{k} \sum_{x \in C_i} \lVert x - \mu_i \rVert^2$$

where $C_i$ is the set of points assigned to cluster $i$ and $\mu_i$ is that cluster's centroid.

### Lloyd's algorithm

There's no closed-form solution — minimizing $J$ exactly over all possible cluster assignments is computationally intractable (NP-hard) for anything but tiny datasets. In practice, **Lloyd's algorithm** finds a good (locally optimal) solution by alternating:

**Assignment step:** given fixed centroids $\mu_1, \ldots, \mu_k$, assign each point to its closest centroid:

$$C_i = \{x : \lVert x - \mu_i \rVert \leq \lVert x - \mu_j \rVert \; \forall j\}$$

**Update step:** given fixed assignments, recompute each centroid as the mean of its assigned points — provably the point that minimizes total squared distance to a fixed set of points:

$$\mu_i = \frac{1}{|C_i|}\sum_{x \in C_i} x$$

Repeat until assignments stop changing (or a maximum iteration count is reached).

### Choosing $k$

K-means doesn't discover $k$ on its own — it must be chosen beforehand. The **elbow method** plots inertia against $k$ and looks for the point where adding more clusters stops meaningfully reducing it; the **silhouette score** measures how well-separated clusters are for a given $k$ and can be compared across values.

---

## Typical hyperparameters

### `n_clusters`

The $k$. The only hyperparameter that fundamentally changes what problem is being solved, not just how well it's solved — see [Choosing $k$](#choosing-k).

```python
KMeans(n_clusters=3)
```

### `init`

How initial centroids are chosen. `"k-means++"` (default) spreads out the initial centroids to be far from one another, which markedly reduces the chance of a poor local optimum compared to `"random"` initialization.

```python
KMeans(init="k-means++")
```

### `n_init`

Number of independent random initializations to run, keeping the best result by inertia. Because Lloyd's algorithm only finds a local optimum, running it multiple times from different starting points and keeping the best guards against a single unlucky initialization.

```python
KMeans(n_init=10)
```

### `max_iter`

Maximum assignment/update iterations per run. Convergence is usually fast in practice (tens of iterations), well before this default (`300`) is reached.

### Modeling choices that matter more than any single constructor argument

- **Feature scaling** — like KNN and SVM, k-means is distance-based, so unscaled features distort the notion of "closest" the same way described in [KNN: Mathematical formulation](../6.k-nearest-neighbors/README.md#why-scale-matters).
- The choice of $k$ itself, which is a modeling decision, not something cross-validation in the supervised sense can pick for you (there's no ground-truth label to validate against).
- Whether clusters are actually expected to be roughly spherical and similarly sized — see [Limitations](#limitations).

---

## Advantages

**Simple and fast** — Lloyd's algorithm is easy to reason about and scales well; each iteration is linear in the number of points, clusters, and features.

**Easy to interpret** — each cluster is summarized by a single centroid, a natural "typical member" description.

**Works well when clusters are genuinely compact and roughly spherical**, which is a common enough situation in practice (e.g., customer segments along a few continuous behavioral dimensions) to make k-means a reasonable default first attempt.

**Scales to large datasets** better than many alternatives (e.g., hierarchical clustering's $O(n^2)$ or worse distance computations — see [Hierarchical Clustering: Limitations](../9.hierarchical-clustering/README.md#limitations)).

---

## Limitations

**Requires choosing $k$ in advance**, and the "right" $k$ is often genuinely ambiguous — the elbow/silhouette heuristics are useful but not definitive, unlike a supervised model's hyperparameters, which can be tuned against an actual accuracy/error metric.

**Converges to a local, not global, optimum** — a poor initialization can land on a clustering that's clearly worse than another reachable one; `n_init` and `k-means++` mitigate but don't eliminate this.

**Assumes roughly spherical, similarly-sized clusters** — because it only ever compares distance to a single centroid per cluster, k-means struggles with elongated, non-convex, or very differently-sized/differently-dense clusters (a classic failure case: two concentric rings of points, which k-means cannot separate no matter the initialization, since no straight-line-distance-to-centroid boundary can trace a ring).

**Sensitive to outliers** — a single far-off point can pull a centroid noticeably toward it, since the centroid is a mean, not a median.

**Sensitive to feature scaling**, same caveat as KNN and SVM.

**No probabilistic or soft assignment** — every point belongs entirely to exactly one cluster; Gaussian Mixture Models are the usual next step when soft, probabilistic cluster membership is needed.

---

## Simple example

Six points that visibly form two groups:

| $x_1$ | $x_2$ |
|---:|---:|
| 1 | 1 |
| 1 | 2 |
| 2 | 1 |
| 8 | 8 |
| 8 | 9 |
| 9 | 8 |

Initializing centroids at $(1,1)$ and $(8,8)$ (two of the actual data points) and running Lloyd's algorithm by hand:

**Iteration 1 — assign:** every point is already closer to whichever initial centroid is in its own visual group, so the assignment doesn't change from the obvious grouping.

**Iteration 1 — update:** recompute each centroid as the mean of its group:

$$\mu_1 = \left(\frac{1+1+2}{3}, \frac{1+2+1}{3}\right) = (1.333, 1.333), \qquad \mu_2 = \left(\frac{8+8+9}{3}, \frac{8+9+8}{3}\right) = (8.333, 8.333)$$

**Iteration 2 — assign:** with the updated centroids, every point is still closest to the same centroid as before, so the assignment is unchanged — **the algorithm has converged** after just one update.

Final inertia (total squared distance to assigned centroid): $\approx 2.667$.

### Python example

See [`k_means_clustering.py`](k_means_clustering.py) for the runnable version:

```python
import numpy as np
from sklearn.cluster import KMeans

X = np.array([[1, 1], [1, 2], [2, 1], [8, 8], [8, 9], [9, 8]])

model = KMeans(n_clusters=2, init=np.array([[1, 1], [8, 8]]), n_init=1, random_state=42)
model.fit(X)

print("Cluster centers:", model.cluster_centers_)
print("Labels:", model.labels_)
print("Inertia:", model.inertia_)
```

Expected output (matches the hand-computed centroids and inertia above; label numbers 0/1 are
arbitrary and depend only on which initial centroid was listed first):

```text
Cluster centers: [[1.33333333 1.33333333]
 [8.33333333 8.33333333]]
Labels: [0 0 0 1 1 1]
Inertia: 2.666666666666667
```

---

## Resources

- [Scikit-learn `KMeans` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) — parameters, `k-means++` initialization, attributes.
- [Scikit-learn clustering user guide](https://scikit-learn.org/stable/modules/clustering.html#k-means) — comparison against other clustering algorithms, including where k-means's spherical-cluster assumption breaks down.
- [Lloyd, "Least Squares Quantization in PCM" (1982, written 1957)](https://ieeexplore.ieee.org/document/1056489) — the original algorithm.
- [Arthur & Vassilvitskii, "k-means++: The Advantages of Careful Seeding" (2007)](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf) — the initialization scheme scikit-learn defaults to.
- [*The Elements of Statistical Learning*, Ch. 14](https://link.springer.com/book/10.1007/978-0-387-84858-7) — k-means within the broader family of clustering methods.

### Core fact to retain

> K-means alternates between assigning points to the nearest centroid and re-centering each centroid at the mean of its assigned points, guaranteed to converge to *a* solution but not necessarily the best one — which is why it needs $k$ chosen up front and benefits from multiple random restarts.
