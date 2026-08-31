# Support Vector Machine (SVM)

## Overview

A support vector machine is a **supervised learning algorithm**, most commonly used for **classification**, that finds the decision boundary separating two classes with the **largest possible margin** — the widest possible buffer between the boundary and the nearest training points from each class.

Unlike logistic regression, which fits every point's contribution to a likelihood, an SVM's decision boundary is determined entirely by the handful of points closest to it — the **support vectors**. Combined with the **kernel trick**, SVMs can also draw nonlinear decision boundaries without ever explicitly constructing the higher-dimensional features that would make the boundary linear.

---

## Intuition

Suppose two classes are cleanly separable by a straight line. Infinitely many lines could separate them — logistic regression finds *a* separating boundary, but doesn't specifically maximize how far it sits from either class. SVM asks a sharper question: **of all the lines that separate the classes, which one has the most breathing room on both sides?**

That "breathing room" is the **margin**, and only the closest point(s) from each class — the support vectors — determine where the maximum-margin boundary sits. Every other point could move around (as long as it doesn't cross into the margin) without changing the boundary at all — a very different behavior from linear/logistic regression, where every point pulls on the fit.

### Soft margins

Real data is rarely perfectly separable. The **soft-margin** SVM allows some points to sit inside the margin, or even on the wrong side of the boundary, paying a penalty proportional to how far they violate it. The `C` hyperparameter controls that trade-off (see [Typical hyperparameters](#typical-hyperparameters)).

### The kernel trick

If classes aren't linearly separable in the original feature space, mapping the data into a higher-dimensional space can make them separable there — but computing that mapping explicitly can be expensive or infeasible. SVM's optimization only ever needs the *dot product* between pairs of transformed points, and a **kernel function** computes that dot product directly, without ever materializing the mapping:

- **Linear kernel:** $K(x_i, x_j) = x_i \cdot x_j$ — no transformation, a straight-line/hyperplane boundary.
- **RBF (Gaussian) kernel:** $K(x_i, x_j) = \exp(-\gamma \lVert x_i - x_j \rVert^2)$ — effectively infinite-dimensional, produces smooth curved boundaries.
- **Polynomial kernel:** $K(x_i, x_j) = (\gamma\, x_i \cdot x_j + r)^d$ — captures interactions up to degree $d$.

---

## Mathematical formulation

### Hard-margin primal (linearly separable case)

Find the hyperplane $w \cdot x + b = 0$ that maximizes the margin $2/\lVert w \rVert$, equivalently:

$$\min_{w, b} \frac{1}{2}\lVert w \rVert^2 \quad \text{subject to} \quad y_i(w \cdot x_i + b) \geq 1 \;\; \forall i$$

where $y_i \in \{-1, +1\}$. Points where the constraint holds with equality ($y_i(w\cdot x_i + b)=1$) are exactly the **support vectors** — they, and only they, determine $w$ and $b$.

### Soft-margin primal

Introduce slack variables $\xi_i \geq 0$ to allow margin violations, penalized by $C$:

$$\min_{w, b, \xi} \frac{1}{2}\lVert w \rVert^2 + C\sum_{i=1}^{n}\xi_i \quad \text{subject to} \quad y_i(w \cdot x_i + b) \geq 1 - \xi_i,\;\; \xi_i \geq 0$$

Equivalently, this is minimizing $\lVert w \rVert^2$ regularization plus the **hinge loss** $\max(0, 1 - y_i(w\cdot x_i+b))$ summed over all points — a margin-based loss that is exactly zero once a point is correctly classified with margin $\geq 1$, unlike log loss (logistic regression), which keeps rewarding increasing confidence even past that point.

### Dual formulation and kernels

The dual form of this optimization depends on the data only through pairwise dot products $x_i \cdot x_j$ — which is what lets the kernel trick substitute $K(x_i, x_j)$ for $x_i \cdot x_j$ and implicitly work in a transformed feature space without ever computing the transformation.

---

## Typical hyperparameters

### `C`

Inverse regularization strength — the same role it plays in [Logistic Regression](../2.logistic-regression/README.md#typical-hyperparameters), but here it directly trades margin width for margin violations. Smaller `C` allows more violations for a wider margin (more regularization, less overfitting); larger `C` penalizes violations more, producing a narrower margin that fits the training data more tightly.

```python
SVC(C=1.0)
```

### `kernel`

`"linear"`, `"rbf"` (default), `"poly"`, or `"sigmoid"` — see [The kernel trick](#the-kernel-trick). `"linear"` is the right choice when the boundary is expected to be roughly linear or the feature count is very high relative to the sample count (text classification is the classic example).

```python
SVC(kernel="linear")
```

### `gamma`

For `"rbf"` and `"poly"` kernels: how far a single training point's influence reaches. Small `gamma` → smooth, far-reaching influence (simpler boundary, risk of underfitting); large `gamma` → each point only influences its immediate neighborhood (highly flexible boundary, risk of overfitting).

```python
SVC(kernel="rbf", gamma="scale")
```

### `degree`

Degree of the polynomial kernel (ignored by other kernels). Default `3`.

### `class_weight`

Same purpose as in logistic regression — `"balanced"` reweights the margin penalty to counteract class imbalance.

### Modeling choices that matter more than any single constructor argument

- **Feature scaling** — SVMs are distance/dot-product based, so unscaled features (one ranging 0–1, another 0–1,000,000) will make the larger-scale feature dominate the margin calculation; standardizing features is close to mandatory.
- Whether `kernel="linear"` is enough, or a nonlinear kernel is actually needed — starting linear and only adding kernel complexity if the linear model underperforms is the usual workflow.
- `C` and `gamma` are typically tuned together via grid/random search with cross-validation, since they interact.

---

## Advantages

**Effective in high-dimensional spaces**, including cases where the number of features exceeds the number of samples (a classic strength for text and genomic data).

**Memory-efficient at prediction time** — the fitted model only needs to store the support vectors, not the entire training set.

**Versatile via kernels** — the same algorithm handles linear and highly nonlinear decision boundaries just by swapping the kernel function.

**Strong theoretical grounding** — the margin-maximization objective has well-studied generalization guarantees (VC theory), and the hinge loss is convex, so training finds a global optimum, not just a local one.

**Robust to overfitting in high dimensions when properly regularized** — because the boundary only depends on support vectors, not every point, it isn't as easily swayed by every noisy observation as some other methods.

---

## Limitations

**Doesn't scale well to very large datasets** — standard SVM training scales roughly quadratically to cubically with the number of samples, making it impractical much past tens of thousands of rows without specialized solvers.

**Requires feature scaling** — see [Typical hyperparameters](#typical-hyperparameters); skipping this is a common, silent way to get a poorly performing SVM.

**No probability estimates by default** — `SVC` outputs a class label from which side of the boundary a point falls on, not a calibrated probability; scikit-learn's `probability=True` option adds Platt scaling (an extra internal cross-validated fit), which is noticeably slower and only approximately calibrated.

**Kernel and hyperparameter choice requires real tuning** — an RBF SVM's performance is quite sensitive to `C` and `gamma` together, and there's no default combination that works well across problems the way, say, `LinearRegression()`'s defaults usually do.

**Inherently binary** — multiclass problems are handled via one-vs-one or one-vs-rest wrappers (scikit-learn does this automatically), adding some indirection compared to logistic regression's native multinomial extension.

**Less interpretable** than linear/logistic regression or a single decision tree — especially with a nonlinear kernel, there's no simple coefficient-based story for what the model learned.

---

## Simple example

Suppose two classes are cleanly separated on a single feature:

| $x$ | Class $y$ |
|---:|---:|
| 0 | $-1$ |
| 1 | $-1$ |
| 3 | $+1$ |
| 4 | $+1$ |

The maximum-margin boundary must sit exactly halfway between the closest points of each class — here, $x=1$ (class $-1$) and $x=3$ (class $+1$) — putting the boundary at $x=2$. Solving the two support-vector equality constraints $y_i(wx_i+b)=1$ by hand:

$$w(1) + b = -1, \qquad w(3) + b = 1$$

gives $w = 1$, $b = -2$, i.e., the decision function is $f(x) = x - 2$. The points $x=0$ and $x=4$ satisfy the margin constraint with room to spare ($y \cdot f(x) = 2 > 1$) and are **not** support vectors; $x=1$ and $x=3$ satisfy it with equality ($y \cdot f(x) = 1$) and **are** the support vectors — moving $x=0$ or $x=4$ anywhere further from the boundary wouldn't change $w$ or $b$ at all.

### Python example

See [`support_vector_machine.py`](support_vector_machine.py) for the runnable version:

```python
import numpy as np
from sklearn.svm import SVC

X = np.array([[0], [1], [3], [4]])
y = np.array([-1, -1, 1, 1])

# Large C approximates a hard margin (heavily penalizes any violation),
# matching the by-hand solution above since this data is linearly separable.
model = SVC(kernel="linear", C=1000)
model.fit(X, y)

print("Coefficient (w):", model.coef_[0][0])
print("Intercept (b):", model.intercept_[0])
print("Support vectors:", model.support_vectors_.ravel())
```

Expected output (matches the hand-derived $w=1$, $b=-2$ above):

```text
Coefficient (w): 1.0
Intercept (b): -2.0
Support vectors: [1. 3.]
```

---

## Resources

- [Scikit-learn `SVC` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html) — parameters, kernels, and the `probability=True` caveat.
- [Scikit-learn SVM user guide](https://scikit-learn.org/stable/modules/svm.html) — mathematical formulation, complexity, and practical tips (including scaling).
- [Cortes & Vapnik, "Support-Vector Networks" (1995)](https://link.springer.com/article/10.1007/BF00994018) — the original soft-margin SVM paper.
- [*The Elements of Statistical Learning*, Ch. 12](https://link.springer.com/book/10.1007/978-0-387-84858-7) — SVMs, the hinge loss, and kernel methods in the broader classification framework.

### Core fact to retain

> An SVM's decision boundary is determined entirely by the support vectors — the closest points to the margin — and the kernel trick lets it draw nonlinear boundaries by implicitly working in a higher-dimensional space, without ever computing the transformation explicitly.
