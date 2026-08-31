# Naive Bayes

## Overview

Naive Bayes is a **supervised learning algorithm** for classification built directly on **Bayes' theorem**, with one deliberately simplifying assumption: every feature is treated as **conditionally independent of every other feature, given the class**. That assumption is almost never literally true — hence "naive" — but the resulting classifier is fast, needs very little data to estimate, and is a surprisingly strong baseline in practice, especially for text classification (spam filtering, sentiment analysis).

---

## Intuition

Bayes' theorem lets you flip a conditional probability around: instead of needing $P(\text{class} \mid \text{features})$ directly, estimate $P(\text{features} \mid \text{class})$ and $P(\text{class})$ from training data — both of which are far easier to count from examples — and combine them:

$$P(\text{class} \mid \text{features}) \propto P(\text{class}) \times P(\text{features} \mid \text{class})$$

The "naive" independence assumption is what makes $P(\text{features} \mid \text{class})$ tractable to estimate at all: instead of needing enough data to estimate the joint probability of every combination of features occurring together (which grows exponentially with the number of features), it factors into a simple product of one-feature-at-a-time probabilities:

$$P(x_1, \ldots, x_p \mid \text{class}) \approx \prod_{j=1}^{p} P(x_j \mid \text{class})$$

Using the classic "Play Tennis" dataset from [Decision Tree](../3.decision-tree/README.md#intuition): to decide whether to play tennis on a `Sunny, Cool, High humidity, Strong wind` day, Naive Bayes doesn't need to have seen that *exact* combination before (unlike, in spirit, KNN needing similar neighbors, or a decision tree needing that exact path to be well-populated). It only needs to have seen enough examples of `Sunny` days, `Cool` days, `High humidity` days, and `Strong wind` days *individually*, within each class, to estimate each one-feature probability separately, then multiplies them together.

---

## Mathematical formulation

### Bayes' theorem

$$P(y \mid x) = \frac{P(y) \, P(x \mid y)}{P(x)}$$

Since $P(x)$ is the same for every candidate class, it can be dropped for the purpose of picking the most likely class:

$$\hat{y} = \arg\max_{y} \, P(y) \prod_{j=1}^{p} P(x_j \mid y)$$

### Estimating the pieces from data

- **Class prior** $P(y)$: just the fraction of training examples in each class.
- **Likelihood** $P(x_j \mid y)$: depends on the feature type and which Naive Bayes variant is used:
  - **CategoricalNB**: $P(x_j = v \mid y)$ is simply the fraction of class-$y$ training examples where feature $j$ equals category $v$.
  - **GaussianNB**: assumes each continuous feature is normally distributed within each class, and estimates that class-conditional mean and variance.
  - **MultinomialNB**: designed for count data (e.g., word counts in a document), models each feature as drawn from a multinomial distribution.

### Smoothing

If a feature value never appears with a given class in the training data, its raw estimated probability is exactly zero — which would zero out the entire product regardless of how strongly every other feature points the other way. **Laplace (additive) smoothing** adds a small pseudo-count $\alpha$ to every count before normalizing, so no probability is ever exactly zero:

$$P(x_j = v \mid y) = \frac{\text{count}(x_j = v, y) + \alpha}{\text{count}(y) + \alpha \cdot |\text{values of } x_j|}$$

scikit-learn defaults to $\alpha = 1$ ("add-one" smoothing).

### Log-space computation

In practice, the product of many small probabilities underflows numerically, so implementations sum log-probabilities instead:

$$\hat{y} = \arg\max_{y} \left[ \log P(y) + \sum_{j=1}^{p} \log P(x_j \mid y) \right]$$

---

## Typical hyperparameters

### `alpha`

The Laplace/Lidstone smoothing strength (see [Smoothing](#smoothing) above). Default `1.0`. Set lower (even near `0`) to more closely match the raw, unsmoothed maximum-likelihood estimate — usually a bad idea on small or sparse datasets, since it reintroduces the zero-probability problem smoothing exists to solve.

```python
CategoricalNB(alpha=1.0)
```

### `fit_prior`

Whether to learn the class prior $P(y)$ from the training data's class frequencies (default `True`) or assume a uniform prior over classes (`False`) — useful if the training set's class balance is known to be unrepresentative of deployment.

### `var_smoothing` (GaussianNB only)

A small constant added to each feature's estimated variance, purely for numerical stability (avoids division by a variance of exactly zero for a feature that's constant within a class).

### Which variant to use

This is the real "hyperparameter" choice for Naive Bayes — picking the variant that matches the feature type: `CategoricalNB` for unordered categorical features, `GaussianNB` for continuous features, `MultinomialNB`/`BernoulliNB` for word-count or presence/absence text features.

---

## Advantages

**Extremely fast to train and predict** — fitting is just counting (or computing means/variances); there's no iterative optimization at all, unlike logistic regression or SVM.

**Works well with very little training data**, precisely because it only ever needs to estimate one-feature-at-a-time statistics rather than the full joint distribution.

**Handles high-dimensional data naturally** — the independence assumption that makes it "naive" is exactly what avoids the exponential blowup that would otherwise come with estimating a joint distribution over many features (relevant for text classification, where "features" are often thousands of vocabulary words).

**A genuinely strong baseline for text classification** despite the crude independence assumption — word occurrences being treated as independent given the topic/class turns out to be a good enough approximation in practice for many text tasks.

**Naturally multiclass**, same as KNN and decision trees, with no need for one-vs-rest wrappers.

---

## Limitations

**The independence assumption is usually false**, sometimes badly — if two features are strongly correlated given the class (e.g., "humidity" and "outlook" in the tennis example aren't really independent), Naive Bayes effectively double-counts the evidence they provide, which can distort the predicted probabilities even when the final class prediction still happens to be correct.

**Predicted probabilities are often poorly calibrated** — because of that double-counting, Naive Bayes tends to push probabilities toward 0 or 1 more confidently than is actually justified. The *ranking* of classes by probability is often still reasonable even when the raw probability values shouldn't be trusted.

**Zero-frequency problem without smoothing** — any unseen feature/class combination would otherwise zero out an entire prediction (see [Smoothing](#smoothing)); this is solved, not a residual risk, as long as smoothing is left on.

**Wrong variant for the data type gives a genuinely wrong model, not just a suboptimal one** — feeding continuous features into `CategoricalNB` (or count data into `GaussianNB`) means the likelihood model doesn't match how the data was actually generated, unlike, say, choosing a slightly-too-shallow decision tree, which merely underfits.

**Not competitive as a similarity/interaction-aware model** — since it can't represent interactions between features at all (by construction), it will systematically underperform models that can (tree ensembles, SVM with an appropriate kernel) whenever those interactions actually matter for the outcome.

---

## Simple example

Using the "Play Tennis" dataset from [Decision Tree](../3.decision-tree/README.md#intuition) (9 "Yes" days, 5 "No" days out of 14), predict whether a new day — `Outlook=Sunny, Temperature=Cool, Humidity=High, Wind=Strong` — is a "Yes" or "No", using the raw (unsmoothed) class-conditional frequencies from the training data:

$$P(\text{Yes}) \cdot P(\text{Sunny}|\text{Yes}) \cdot P(\text{Cool}|\text{Yes}) \cdot P(\text{High}|\text{Yes}) \cdot P(\text{Strong}|\text{Yes}) = \frac{9}{14}\cdot\frac{2}{9}\cdot\frac{3}{9}\cdot\frac{3}{9}\cdot\frac{3}{9} = \frac{1}{189} \approx 0.00529$$

$$P(\text{No}) \cdot P(\text{Sunny}|\text{No}) \cdot P(\text{Cool}|\text{No}) \cdot P(\text{High}|\text{No}) \cdot P(\text{Strong}|\text{No}) = \frac{5}{14}\cdot\frac{3}{5}\cdot\frac{1}{5}\cdot\frac{4}{5}\cdot\frac{3}{5} = \frac{18}{875} \approx 0.02057$$

Normalizing so the two add to 1:

$$P(\text{Yes} \mid x) \approx 0.205, \qquad P(\text{No} \mid x) \approx 0.795$$

**Predicted class: No** — despite `Sunny` alone being a fairly weak signal either way, the combination of `Cool`, `High humidity`, and `Strong wind` tips the product toward "No" (this is the same worked example, and the same conclusion, as the one in Mitchell's *Machine Learning* textbook — see [Resources](#resources)).

### Python example

See [`naive_bayes.py`](naive_bayes.py) for the runnable version:

```python
import numpy as np
from sklearn.naive_bayes import CategoricalNB
from sklearn.preprocessing import OrdinalEncoder

# Columns: Outlook, Temperature, Humidity, Wind
X_raw = [
    ["Sunny", "Hot", "High", "Weak"], ["Sunny", "Hot", "High", "Strong"],
    ["Overcast", "Hot", "High", "Weak"], ["Rain", "Mild", "High", "Weak"],
    ["Rain", "Cool", "Normal", "Weak"], ["Rain", "Cool", "Normal", "Strong"],
    ["Overcast", "Cool", "Normal", "Strong"], ["Sunny", "Mild", "High", "Weak"],
    ["Sunny", "Cool", "Normal", "Weak"], ["Rain", "Mild", "Normal", "Weak"],
    ["Sunny", "Mild", "Normal", "Strong"], ["Overcast", "Mild", "High", "Strong"],
    ["Overcast", "Hot", "Normal", "Weak"], ["Rain", "Mild", "High", "Strong"],
]
y = ["No", "No", "Yes", "Yes", "Yes", "No", "Yes", "No",
     "Yes", "Yes", "Yes", "Yes", "Yes", "No"]

encoder = OrdinalEncoder()
X = encoder.fit_transform(X_raw)

# alpha near 0 approximates the unsmoothed, hand-computed probabilities above;
# scikit-learn's default alpha=1.0 (Laplace smoothing) would shift them
# slightly, which is what you want in practice (see README's "Smoothing").
model = CategoricalNB(alpha=1e-10)
model.fit(X, y)

query = encoder.transform([["Sunny", "Cool", "High", "Strong"]])
probabilities = model.predict_proba(query)[0]

for class_name, p in zip(model.classes_, probabilities):
    print(f"P({class_name} | x) = {p:.3f}")
print("Prediction:", model.predict(query)[0])
```

Expected output (matches the hand-derived probabilities above; `alpha=1e-10` rather than exactly
`0` avoids a divide-by-zero in scikit-learn's smoothing formula but is numerically indistinguishable
from it here):

```text
P(No | x) = 0.795
P(Yes | x) = 0.205
Prediction: No
```

---

## Resources

- [Scikit-learn `CategoricalNB` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.CategoricalNB.html) — parameters and the categorical likelihood model.
- [Scikit-learn Naive Bayes user guide](https://scikit-learn.org/stable/modules/naive_bayes.html) — all variants (Gaussian, Multinomial, Bernoulli, Categorical, Complement) and when to use each.
- [Mitchell, *Machine Learning* (1997), Ch. 6](https://www.cs.cmu.edu/~tom/mlbook.html) — the textbook source of the Play Tennis Naive Bayes worked example reproduced above.
- [*The Elements of Statistical Learning*, Ch. 6.6](https://link.springer.com/book/10.1007/978-0-387-84858-7) — Naive Bayes framed within the broader class of generative classifiers.

### Core fact to retain

> Naive Bayes turns classification into a product of easy-to-estimate one-feature-at-a-time probabilities by assuming features are independent given the class — an assumption that's almost always technically wrong, but cheap enough to make and often good enough in practice, especially for text.
