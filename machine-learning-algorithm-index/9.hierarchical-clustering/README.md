# Hierarchical Clustering

## Overview

Hierarchical clustering is an **unsupervised learning algorithm**, like [K-Means](../8.k-means-clustering/README.md), used to group unlabeled data — but instead of producing one flat partition into $k$ clusters, it builds a full **tree of nested clusters** (a dendrogram), from every point in its own cluster up to all points in one cluster. A flat clustering at any desired number of clusters can then be read off by "cutting" the tree at the right height, without re-running the algorithm.

The most common variant, and the one covered here, is **agglomerative** (bottom-up) clustering: start with every point as its own cluster, and repeatedly merge the two closest clusters until only one remains.

---

## Intuition

Unlike k-means, which needs $k$ decided before it starts, agglomerative clustering just keeps merging the two nearest clusters, one pair at a time, and records the order and distance of every merge. That record *is* the dendrogram: reading it top to bottom shows a series of splits from "everything is one cluster" down to "every point is its own cluster," and the height of each merge shows how (dis)similar the two merged clusters were.

This raises an immediate question the algorithm has to answer at every single merge step: once a cluster has more than one point in it, what does "distance between two clusters" even mean? That choice — the **linkage criterion** — is the main design decision in hierarchical clustering (see [Mathematical formulation](#mathematical-formulation)), and different choices can produce meaningfully different trees from the same data.

---

## Mathematical formulation

### Linkage criteria

Given two clusters $A$ and $B$, each containing multiple points, the distance between them can be defined several ways:

**Single linkage** (nearest-neighbor): the distance between the *closest* pair of points, one from each cluster.

$$d(A,B) = \min_{a \in A,\, b \in B} \lVert a - b \rVert$$

Tends to produce elongated, "chained" clusters — sensitive to a thin bridge of intermediate points linking two otherwise distinct groups.

**Complete linkage** (farthest-neighbor): the distance between the *farthest* pair of points.

$$d(A,B) = \max_{a \in A,\, b \in B} \lVert a - b \rVert$$

Tends to produce more compact, evenly-sized clusters than single linkage; more sensitive to outliers, since one distant point can make an otherwise-close cluster look far away.

**Average linkage**: the mean distance across every cross-cluster pair.

$$d(A,B) = \frac{1}{|A||B|}\sum_{a \in A}\sum_{b \in B}\lVert a - b \rVert$$

A middle ground between single and complete linkage.

**Ward's method**: merges whichever pair of clusters produces the *smallest increase* in total within-cluster variance (the same quantity [K-Means](../8.k-means-clustering/README.md#mathematical-formulation) minimizes) — not a simple pairwise-distance rule like the other three, but usually the best default for roughly spherical clusters, and scikit-learn's default.

### The agglomeration procedure

1. Start with $n$ clusters, one per data point.
2. Compute the distance between every pair of clusters using the chosen linkage.
3. Merge the two closest clusters into one; record the distance at which they merged.
4. Repeat from step 2 with $n-1$ clusters, until only one cluster remains.

This produces $n-1$ merges total, which is exactly what a dendrogram plots.

---

## Typical hyperparameters

### `n_clusters` or `distance_threshold`

Exactly one of these is specified (not both): either cut the tree to produce a fixed number of clusters, or cut it wherever the merge distance first exceeds a threshold — letting the data determine how many clusters result.

```python
AgglomerativeClustering(n_clusters=2)
```

### `linkage`

Which of the four criteria above to use. `"ward"` (default in scikit-learn) requires Euclidean distance; `"single"`, `"complete"`, and `"average"` work with any metric.

```python
AgglomerativeClustering(linkage="single")
```

### `metric`

The distance metric between individual points (Euclidean by default). Constrained to `"euclidean"` when `linkage="ward"`.

### Modeling choices that matter more than any single constructor argument

- **Which linkage criterion matches the expected cluster shape** — this changes the *structure* of the result, not just a tuning knob's fit (see [Limitations](#limitations)).
- Whether to cut the dendrogram by `n_clusters` or `distance_threshold` — the latter is more principled when the "right" number of clusters is genuinely unknown, since it lets a natural gap in merge distances decide.
- Feature scaling, for the same distance-based reasons as KNN, SVM, and k-means.

---

## Advantages

**No need to choose $k$ up front** — the full dendrogram is computed once, and any number of clusters can be read off afterward by cutting at a different height, unlike k-means, which must be re-run from scratch for each candidate $k$.

**Deterministic** — given a linkage criterion and distance metric, the result is exactly reproducible; there's no random initialization to worry about, unlike k-means's sensitivity to starting centroids.

**The dendrogram itself is a useful visualization**, showing not just a final grouping but the entire nested similarity structure of the data — which points/clusters are close, and at what distance groups start to look genuinely distinct.

**Flexible similarity notion** — any distance metric can be used (except with Ward linkage), unlike k-means, which is tied to Euclidean distance to a centroid.

---

## Limitations

**Computationally expensive at scale** — naively, computing and updating all pairwise cluster distances is $O(n^2)$ in memory and $O(n^3)$ (or $O(n^2 \log n)$ with efficient data structures) in time, which makes it impractical on datasets much beyond a few thousand points, unlike k-means's near-linear scaling.

**A merge is permanent** — once two clusters are merged, the algorithm can never undo it, even if a later merge reveals that an earlier one was a mistake. K-means, by contrast, can reassign a point away from its current cluster at every iteration.

**Sensitive to the choice of linkage**, and not in a "just tune it" way — single linkage can produce long, straggly "chains" of points connected by a series of short hops even when they don't form a visually coherent group; complete linkage can artificially split a genuinely elongated cluster because its farthest points look far apart.

**No explicit objective function being globally optimized** (except Ward's method, which approximates k-means's variance-minimization greedily) — most linkage criteria are pairwise distance rules, not derived from minimizing a stated loss the way k-means or Ward's method are.

**Cutting the dendrogram is still a judgment call** — like choosing $k$ for k-means, deciding where to cut requires either domain knowledge or a heuristic (a visually large gap between consecutive merge heights), not a fully automatic answer.

---

## Simple example

Five points on a number line, with two visibly tighter pairs and one point in between:

| Point | Value |
|---|---:|
| A | 1 |
| B | 2 |
| C | 4 |
| D | 7 |
| E | 8 |

Running **single-linkage** agglomerative clustering by hand, merging the two closest clusters at each step:

1. Merge **A, B** (distance 1) — the closest pair overall.
2. Merge **D, E** (distance 1) — tied for closest, merged in either order without changing the outcome below.
3. Merge **{A,B}** with **C** (distance $\min(|A-C|, |B-C|) = \min(3, 2) = 2$).
4. Merge **{A,B,C}** with **{D,E}** (distance $\min(|A-D|,|A-E|,|B-D|,|B-E|,|C-D|,|C-E|) = \min(6,7,5,6,3,4) = 3$, achieved by the $C$–$D$ pair).

Cutting the resulting dendrogram for 2 clusters (i.e., before the final merge) gives $\{A, B, C\}$ and $\{D, E\}$ — the same grouping k-means found on a similarly-shaped 2-D dataset in [K-Means: Simple example](../8.k-means-clustering/README.md#simple-example).

### Python example

See [`hierarchical_clustering.py`](hierarchical_clustering.py) for the runnable version:

```python
import numpy as np
from sklearn.cluster import AgglomerativeClustering

X = np.array([[1], [2], [4], [7], [8]])  # A, B, C, D, E

model = AgglomerativeClustering(n_clusters=2, linkage="single", compute_distances=True)
model.fit(X)

print("Labels:", model.labels_)
print("Merge distances:", sorted(model.distances_))
```

Expected output (labels 0/1 are arbitrary; merge distances match the hand computation above —
1, 1, 2, and the final merge at 3 isn't recorded since the tree is only built down to 2 clusters):

```text
Labels: [0 0 0 1 1]
Merge distances: [1.0, 1.0, 2.0]
```

---

## Resources

- [Scikit-learn `AgglomerativeClustering` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html) — parameters, linkage options, `distance_threshold`.
- [Scikit-learn clustering user guide](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering) — visual comparison of linkage criteria on the same datasets.
- [Ward, "Hierarchical Grouping to Optimize an Objective Function" (1963)](https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500845) — the original Ward's method paper.
- [*The Elements of Statistical Learning*, Ch. 14.3.12](https://link.springer.com/book/10.1007/978-0-387-84858-7) — hierarchical clustering and linkage criteria in the broader clustering framework.

### Core fact to retain

> Agglomerative clustering repeatedly merges the two closest clusters, recording every merge as a dendrogram — trading k-means's need to fix $k$ up front for a choice of linkage criterion that determines the shape of clusters it can represent well.
