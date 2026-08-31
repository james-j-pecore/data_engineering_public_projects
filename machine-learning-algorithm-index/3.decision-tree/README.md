# Decision Tree

## Overview

A decision tree is a **supervised learning algorithm** used for both **classification** and **regression**. It predicts an outcome by asking a sequence of simple, single-feature yes/no questions, arranged in a tree, until it reaches a leaf that holds a prediction.

Examples include predicting:

- Whether a loan applicant defaults, by splitting on income, credit score, debt ratio
- A house's price bracket, by splitting on square footage, location, age
- Whether a patient has a condition, by splitting on lab values and symptoms

Unlike linear or logistic regression, a decision tree makes no assumption that the relationship between features and target is linear (or linear in log-odds) — it partitions the feature space into axis-aligned regions and predicts a constant value (classification: majority class; regression: mean target) within each region.

---

## Intuition

The classic worked example (Quinlan's "Play Tennis" dataset) asks: given the weather, will a person play tennis?

| Outlook | Temperature | Humidity | Wind | Play? |
|---|---|---|---|---|
| Sunny | Hot | High | Weak | No |
| Sunny | Hot | High | Strong | No |
| Overcast | Hot | High | Weak | Yes |
| Rain | Mild | High | Weak | Yes |
| Rain | Cool | Normal | Weak | Yes |
| Rain | Cool | Normal | Strong | No |
| Overcast | Cool | Normal | Strong | Yes |
| Sunny | Mild | High | Weak | No |
| Sunny | Cool | Normal | Weak | Yes |
| Rain | Mild | Normal | Weak | Yes |
| Sunny | Mild | Normal | Strong | Yes |
| Overcast | Mild | High | Strong | Yes |
| Overcast | Hot | Normal | Weak | Yes |
| Rain | Mild | High | Strong | No |

9 of the 14 days say "Yes." A decision tree picks the single feature that best separates Yes from No, splits on it, and repeats within each resulting group. Trying every feature as the first (root) split and measuring how much each one reduces uncertainty about the outcome (see [Mathematical formulation](#mathematical-formulation)) gives:

| Split on | Information gain |
|---|---:|
| **Outlook** | **0.247** |
| Humidity | 0.152 |
| Wind | 0.048 |
| Temperature | 0.029 |

`Outlook` wins, so it becomes the root split. Within the `Sunny` branch, the tree would then recurse and pick the next best feature (here, `Humidity` perfectly separates the remaining Sunny days) — this greedy, one-feature-at-a-time process is exactly how a decision tree is built.

---

## Mathematical formulation

### Impurity measures

A tree needs a way to score "how mixed" the labels are in a node, so it can pick the split that reduces mixing the most. Two common measures for classification:

**Entropy** (used by the classic ID3/C4.5 algorithms):

$$H(S) = -\sum_{c} p_c \log_2 p_c$$

where $p_c$ is the proportion of class $c$ in node $S$. A pure node ($p_c=1$ for one class) has entropy 0; a 50/50 binary split has entropy 1 (maximum uncertainty).

**Gini impurity** (used by scikit-learn's and CART's default):

$$G(S) = 1 - \sum_{c} p_c^2$$

For a binary outcome, this ranges from 0 (pure) to 0.5 (perfectly mixed) — both measures behave similarly and usually pick similar splits in practice.

### Information gain / impurity reduction

For a candidate split of node $S$ into children $S_{\text{left}}, S_{\text{right}}$:

$$\text{Gain} = \text{Impurity}(S) - \left[\frac{|S_{\text{left}}|}{|S|}\text{Impurity}(S_{\text{left}}) + \frac{|S_{\text{right}}|}{|S|}\text{Impurity}(S_{\text{right}})\right]$$

The tree-building algorithm (CART) considers every feature and, for numeric features, every possible threshold, picks whichever split maximizes this gain, and recurses on each child — a **greedy** search, not a globally optimal one (see [Limitations](#limitations)).

### Regression trees

For a continuous target, impurity is instead the **variance** (or mean squared error) within a node, and each leaf predicts the mean target of the training points that land in it.

### Stopping / pruning

Left unconstrained, a tree keeps splitting until every leaf is pure (or has one sample), which almost always overfits. Real trees stop early via depth/size limits, or are grown fully and then **pruned** back (scikit-learn's `ccp_alpha` implements cost-complexity pruning).

---

## Typical hyperparameters

### `max_depth`

Maximum depth of the tree. The single most important lever against overfitting — an unconstrained tree can reach 100% training accuracy by memorizing noise.

```python
DecisionTreeClassifier(max_depth=3)
```

### `min_samples_split` / `min_samples_leaf`

Minimum samples required to split a node, and minimum samples allowed in a resulting leaf, respectively. Larger values produce simpler, more conservative trees.

```python
DecisionTreeClassifier(min_samples_leaf=5)
```

### `criterion`

The impurity measure: `"gini"` (default, slightly cheaper to compute) or `"entropy"` (log-based information gain, per [Mathematical formulation](#mathematical-formulation)). Usually makes little practical difference.

```python
DecisionTreeClassifier(criterion="gini")
```

### `max_features`

Number of features considered at each split. Restricting this (`"sqrt"`, an integer, or a fraction) adds randomness — the core idea behind Random Forest, which is literally many decision trees each grown with this restriction on a bootstrap sample.

### `ccp_alpha`

Cost-complexity pruning strength. `0.0` (default) does no pruning; larger values prune more aggressively, trading training fit for a smaller, more generalizable tree.

### Modeling choices that matter more than any single constructor argument

- Whether the tree is regularized at all (depth/leaf-size limits or pruning) — an unregularized tree is close to guaranteed to overfit
- Categorical feature encoding — scikit-learn's `DecisionTreeClassifier` does not natively split on unordered categories; they must be one-hot (or otherwise) encoded first
- Whether a single tree is enough, or an ensemble (Random Forest, Gradient Boosting) is warranted for the variance reduction a single tree can't provide

---

## Advantages

**Naturally interpretable** — the fitted tree can be printed or plotted as a flowchart of if/else questions, understandable to a non-technical audience without translation.

**No feature scaling required** — splits are threshold comparisons on one feature at a time, so the algorithm is invariant to monotonic transformations of any feature.

**Captures nonlinearities and interactions automatically** — a tree can represent "if income is high AND debt ratio is low" without the modeler having to manually engineer that interaction term, unlike linear/logistic regression.

**Handles mixed numeric and (encoded) categorical data** in one model without needing separate treatment.

**Fast to train and predict** on small-to-medium datasets, and prediction is a simple root-to-leaf walk.

---

## Limitations

**High variance / prone to overfitting** — a small change in the training data can produce a substantially different tree, especially if it's grown deep. This is the central motivation for ensembles (Random Forest averages away this instability; Gradient Boosting/XGBoost build on the same base learner differently).

**Greedy, not globally optimal** — the algorithm picks the locally best split at each node; it does not search over the space of all possible trees, so it can miss a better tree that requires a locally suboptimal first split.

**Axis-aligned splits only** — a single tree approximates diagonal decision boundaries with a staircase of many axis-aligned splits, which can need considerable depth (and risks overfitting) to represent a simple linear boundary well.

**Biased toward features with many distinct values** when using information gain on categorical splits (a feature that's nearly unique per row can look artificially informative) — Gini and gain-ratio variants mitigate but don't eliminate this.

**Extrapolates poorly** — a leaf's prediction is the training-data mean/majority within that region, so a regression tree in particular predicts a constant outside the range of training data rather than continuing a trend.

**No native categorical support in scikit-learn** — unlike some other implementations (e.g., in R, or gradient-boosting libraries like LightGBM/CatBoost), scikit-learn's `DecisionTreeClassifier`/`Regressor` requires categorical features to be numerically encoded before fitting.

---

## Simple example

Reusing the hours-studied-vs-pass dataset from [Logistic Regression](../2.logistic-regression/README.md) lets the two algorithms be compared directly on identical data.

Considering every possible single threshold on `hours studied` and picking the one that minimizes weighted Gini impurity (i.e., growing a depth-1 tree, a "decision stump") gives:

- **Best split:** hours studied $\leq 3.75$ vs. $> 3.75$
- **Left node** (14 students, $\leq 3.75$ hours): 4 passed / 10 failed → predicts **fail**, Gini $\approx 0.408$
- **Right node** (6 students, $> 3.75$ hours): 6 passed / 0 failed → predicts **pass**, Gini $= 0$
- **Weighted Gini after split:** $\approx 0.286$, down from a root Gini of $0.5$ (10 pass / 10 fail)

### Python example

See [`decision_tree.py`](decision_tree.py) for the runnable version:

```python
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score

X = np.array([[0.5], [0.75], [1.0], [1.25], [1.5], [1.75], [1.75], [2.0],
              [2.25], [2.5], [2.75], [3.0], [3.25], [3.5], [4.0], [4.25],
              [4.5], [4.75], [5.0], [5.5]])
y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])

model = DecisionTreeClassifier(max_depth=1, criterion="gini")
model.fit(X, y)

predictions = model.predict(X)
print(export_text(model, feature_names=["hours_studied"]))
print("Accuracy:", accuracy_score(y, predictions))
```

Expected output (threshold and accuracy independently hand-verified above; the printed tree
structure follows directly from that same threshold):

```text
|--- hours_studied <= 3.75
|   |--- class: 0
|--- hours_studied >  3.75
|   |--- class: 1

Accuracy: 0.8
```

Notice this depth-1 tree gets the same 0.8 accuracy as unregularized logistic regression on this
dataset — for a single, roughly monotonic feature, a threshold rule and a sigmoid curve end up
drawing a similar boundary. The two algorithms diverge more once there are several interacting
features, which a single linear boundary can't represent but a deeper tree can.

---

## Resources

- [Scikit-learn `DecisionTreeClassifier` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html) — parameters, attributes, and pruning path API.
- [Scikit-learn decision trees user guide](https://scikit-learn.org/stable/modules/tree.html) — algorithm details (CART), complexity, and tips on practical use.
- [Quinlan, "Induction of Decision Trees" (1986)](https://link.springer.com/article/10.1007/BF00116251) — the original ID3 paper introducing information-gain-based tree induction, source of the classic Play Tennis dataset style used above.
- [*The Elements of Statistical Learning*, Ch. 9](https://link.springer.com/book/10.1007/978-0-387-84858-7) — CART, impurity measures, and pruning in the broader context of tree-based methods.

### Core fact to retain

> A decision tree greedily splits the feature space, one threshold at a time, to minimize impurity within each resulting region — powerful and interpretable on its own, but its instability is exactly what tree ensembles (Random Forest, Gradient Boosting) exist to fix.
