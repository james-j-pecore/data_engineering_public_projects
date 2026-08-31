# Neural Networks (Multi-Layer Perceptron)

## Overview

A neural network is a **supervised learning algorithm** (though the same building block underlies unsupervised and reinforcement learning models too) built from layers of simple units — loosely inspired by neurons — each computing a weighted sum of its inputs followed by a nonlinear **activation function**. Stacking several such layers lets the network represent far more complex functions than any single layer could, which is why this family of models underlies everything from [CNNs](../14.convolutional-neural-networks/README.md) and [RNNs](../15.recurrent-neural-networks/README.md) to modern [LLMs](../17.large-language-models/README.md) — they're all neural networks with a particular choice of layer structure.

Every algorithm so far in this index either has a closed-form solution (linear regression) or a hand-designed decision rule (trees, KNN, Naive Bayes). A neural network instead learns its parameters entirely through **gradient descent on a loss function**, using **backpropagation** to compute how every single weight, however deeply buried in the network, should change — this README focuses on exactly that mechanism, since it's the one new idea every deeper architecture in this index builds on.

---

## Intuition

A single layer — a weighted sum followed by a nonlinearity — is really just [logistic regression](../2.logistic-regression/README.md) (or a linear model, if there's no nonlinearity at all): $\hat{y} = \sigma(w \cdot x + b)$. A single layer can only separate classes with a straight line/hyperplane, the same limitation logistic regression has.

Stack a second layer on top — feed the first layer's output into another weighted sum and nonlinearity — and the combination can represent a **nonlinear** decision boundary, built out of nothing but linear pieces and one simple nonlinearity repeated. This is the entire idea behind "deep" learning: depth (more layers) lets simple linear-plus-nonlinearity building blocks compose into increasingly complex functions, in the same way several straight-line segments can approximate a curve.

The catch is that **fitting** a multi-layer model has no closed form the way OLS linear regression does — there's no direct formula for the best weights. Instead, weights are adjusted iteratively via **gradient descent**, and **backpropagation** is simply the chain rule applied systematically, layer by layer, to compute how the loss changes with respect to every weight in the network, including ones in early layers that only affect the output indirectly, through everything downstream of them.

---

## Mathematical formulation

### Forward pass

For a single layer, each unit computes a weighted sum of its inputs plus a bias, then applies an activation function $\phi$:

$$z = w \cdot x + b, \qquad a = \phi(z)$$

Common choices for $\phi$: **sigmoid** ($\frac{1}{1+e^{-z}}$, used in the worked example below and in the output layer for binary classification, same function as [Logistic Regression](../2.logistic-regression/README.md#overview)), **tanh**, and **ReLU** ($\max(0, z)$, the modern default for hidden layers — cheap to compute and avoids some of sigmoid/tanh's gradient issues, see [Limitations](#limitations)). Stacking $L$ layers means feeding each layer's activations forward as the next layer's input.

### Loss function

The network's output is compared to the target via a loss function — squared error for regression, log loss/cross-entropy for classification (identical to the loss functions already covered for [Linear](../1.linear-regression/README.md#mathematical-formulation) and [Logistic Regression](../2.logistic-regression/README.md#mathematical-formulation), just now evaluated on a multi-layer function instead of a single linear one).

### Backpropagation

Backpropagation computes $\frac{\partial \mathcal{L}}{\partial w}$ for every weight $w$ in the network by applying the chain rule from the output layer backward. For a weight $w$ feeding into a unit with pre-activation $z$ and activation $a=\phi(z)$:

$$\frac{\partial \mathcal{L}}{\partial w} = \frac{\partial \mathcal{L}}{\partial a}\cdot\frac{\partial a}{\partial z}\cdot\frac{\partial z}{\partial w}$$

The key insight that makes this tractable layer by layer: $\frac{\partial \mathcal{L}}{\partial a}$ for a hidden unit is itself computed from the $\frac{\partial \mathcal{L}}{\partial z}$ terms of *every unit in the next layer* that it feeds into, weighted by the connecting weights — the "error signal" propagates backward through the same connections the forward pass used, one layer at a time, which is exactly why it's called backpropagation and why it's efficient (each weight's gradient is computed once, not by numerically perturbing every weight independently).

### Gradient descent update

Once every gradient is known, each weight is nudged in the direction that reduces the loss:

$$w \leftarrow w - \eta \frac{\partial \mathcal{L}}{\partial w}$$

where $\eta$ is the learning rate. In practice this is done on mini-batches of data at a time (**stochastic gradient descent**), not the full dataset per update, and with adaptive per-weight learning rate schemes (Adam being the most common default today) rather than a single fixed $\eta$ for every weight.

---

## Typical hyperparameters

### `hidden_layer_sizes` / architecture

Number of layers and units per layer. More capacity can fit more complex functions but risks overfitting and makes optimization harder; this is the neural network analogue of a decision tree's `max_depth`.

```python
MLPClassifier(hidden_layer_sizes=(64, 32))
```

### `activation`

The nonlinearity $\phi$ applied at each hidden layer — `"relu"` is the common modern default (see [Mathematical formulation](#mathematical-formulation)).

### `learning_rate_init` and `solver`

The step size $\eta$, and which optimization algorithm updates the weights using the computed gradients — `"adam"` (adaptive, per-weight learning rates) is the most common default; plain SGD is simpler but usually needs more careful tuning.

### `alpha`

L2 regularization strength on the weights — the same idea as `C` in logistic regression/SVM, just applied to every weight in every layer.

### `max_iter` / `early_stopping`

How many passes over the training data to allow, and whether to stop early once validation performance stops improving — important since, unlike a decision tree, a large enough network can eventually fit training data (including its noise) essentially perfectly.

### Modeling choices that matter more than any single constructor argument

- **Feature scaling** — gradient-based optimization converges far more reliably on standardized inputs, similar to logistic regression and SVM.
- Network depth/width relative to the amount of training data available — a large network on a small dataset is the fastest way to overfit in this index.
- Weight initialization scheme — poor initialization can leave gradients too small or too large to train effectively at all, especially in deep networks (this is exactly the problem [LSTMs](../16.long-short-term-memory/README.md) were designed to address for recurrent architectures specifically).

---

## Advantages

**Universal function approximation** — a network with even a single sufficiently wide hidden layer can, in principle, approximate any continuous function to arbitrary precision (the Universal Approximation Theorem), unlike linear/logistic regression's fixed functional form.

**Composable architecture** — the same layer-stacking idea specializes into convolutional layers for images ([CNN](../14.convolutional-neural-networks/README.md)), recurrent layers for sequences ([RNN](../15.recurrent-neural-networks/README.md)/[LSTM](../16.long-short-term-memory/README.md)), and attention layers for the models underlying modern [LLMs](../17.large-language-models/README.md) — one training mechanism (backpropagation + gradient descent) works across all of them.

**Scales with data** — given enough data and compute, larger networks tend to keep improving, unlike simpler models that saturate in what they can represent regardless of how much more data is added.

**Learns its own features** — hidden layers can be understood as learning increasingly abstract representations of the input, rather than requiring hand-engineered features the way linear/logistic regression often does.

---

## Limitations

**No closed-form solution and no guarantee of finding the global optimum** — gradient descent on a multi-layer network is a non-convex optimization problem; unlike OLS linear regression or a convex SVM objective, it can get stuck in local minima or saddle points (in practice, this matters less than early theory suggested, but it's a real qualitative difference from earlier entries in this index).

**Needs substantially more data than simpler models** to avoid overfitting, given how much more capacity a multi-layer network has relative to, say, logistic regression.

**Vanishing/exploding gradients** — in deep or recurrent networks, repeatedly multiplying gradients through many layers (or many timesteps, see [RNN: Limitations](../15.recurrent-neural-networks/README.md#limitations)) during backpropagation can make gradients shrink toward zero or grow without bound, stalling learning in early layers specifically.

**Effectively a black box** — there's no coefficient-based or tree-structure-based story for what the model learned; interpretability tools (saliency maps, SHAP, probing) exist but are approximate add-ons, not something inherent to the model the way a decision tree's structure is.

**Expensive to train** relative to the classical methods earlier in this index — more parameters, more hyperparameters, and typically requiring many passes over the data (and often specialized hardware) to converge.

**Requires careful tuning to train at all**, not just to train *well* — learning rate, initialization, and architecture choices can be the difference between a network that learns and one that never converges, a qualitatively different failure mode from, say, a poorly-tuned random forest, which still produces a reasonable model.

---

## Simple example

A single forward and backward pass through a tiny 2-input, 2-hidden-unit, 2-output network — the classic worked example popularized by Matt Mazur's backpropagation tutorial (see [Resources](#resources)), reproduced here because every number in it is independently checkable by hand.

**Network:** inputs $i_1=0.05, i_2=0.10$; hidden layer weights $w_1=0.15, w_2=0.20, w_3=0.25, w_4=0.30$, bias $b_1=0.35$; output layer weights $w_5=0.40, w_6=0.45, w_7=0.50, w_8=0.55$, bias $b_2=0.60$; targets $\text{target}_{o1}=0.01, \text{target}_{o2}=0.99$; sigmoid activation throughout; learning rate $\eta=0.5$.

**Forward pass:**

$$\text{net}_{h1} = w_1 i_1 + w_2 i_2 + b_1 = 0.3775 \;\Rightarrow\; \text{out}_{h1} = \sigma(0.3775) = 0.5933$$
$$\text{net}_{h2} = w_3 i_1 + w_4 i_2 + b_1 = 0.3925 \;\Rightarrow\; \text{out}_{h2} = \sigma(0.3925) = 0.5969$$
$$\text{net}_{o1} = w_5\,\text{out}_{h1} + w_6\,\text{out}_{h2} + b_2 = 1.1059 \;\Rightarrow\; \text{out}_{o1} = \sigma(1.1059) = 0.7514$$
$$\text{net}_{o2} = w_7\,\text{out}_{h1} + w_8\,\text{out}_{h2} + b_2 = 1.2249 \;\Rightarrow\; \text{out}_{o2} = \sigma(1.2249) = 0.7729$$

Total error: $\mathcal{L} = \frac{1}{2}(0.01-0.7514)^2 + \frac{1}{2}(0.99-0.7729)^2 = 0.2984$.

**Backward pass** (chain rule from the output back to $w_5$, one of the output-layer weights):

$$\frac{\partial \mathcal{L}}{\partial w_5} = \frac{\partial \mathcal{L}}{\partial \text{out}_{o1}}\cdot\frac{\partial \text{out}_{o1}}{\partial \text{net}_{o1}}\cdot\frac{\partial \text{net}_{o1}}{\partial w_5} = (-(0.01-0.7514)) \cdot (0.7514)(1-0.7514) \cdot 0.5933 = 0.0822$$

$$w_5 \leftarrow w_5 - \eta \cdot 0.0822 = 0.40 - 0.5(0.0822) = 0.3589$$

Propagating the same chain rule back one more layer (now summing the error contribution through *both* output units, since $w_1$ affects the loss via both of them) updates $w_1$ from $0.15$ to $0.1498$ — a much smaller change, since $w_1$'s influence on the total error is far more indirect.

### Python example

See [`neural_network.py`](neural_network.py) for the runnable version, which implements this exact forward/backward pass **from scratch with plain Python** (no framework) so every intermediate value can be printed and checked against the derivation above:

```python
predictions_before = forward_pass(weights)
print("Total error before update:", total_error(predictions_before, targets))

weights = backward_pass(weights, inputs, targets, learning_rate=0.5)
predictions_after = forward_pass(weights)
print("Total error after one update:", total_error(predictions_after, targets))
```

Expected output (matches the hand-derivation above):

```text
Total error before update: 0.2983711087600027
w5 after one update: 0.35891647971788465
w1 after one update: 0.1497807161327628
Total error after one update: 0.29102777369359933
```

---

## Resources

- [Matt Mazur, "A Step by Step Backpropagation Example"](https://mattmazur.com/2015/03/17/a-step-by-step-backpropagation-example/) — the original source of the worked example reproduced above, with every intermediate value shown.
- [Scikit-learn `MLPClassifier` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html) — a plain feedforward network implementation with the hyperparameters discussed above.
- [3Blue1Brown, "Neural Networks" video series](https://www.3blue1brown.com/topics/neural-networks) — strong visual intuition for forward propagation and backpropagation.
- [*Deep Learning* (Goodfellow, Bengio, Courville), Ch. 6](https://www.deeplearningbook.org/) — the mathematical foundations of feedforward networks and backpropagation in full generality.

### Core fact to retain

> A neural network is layers of weighted sums and nonlinearities, fit by using the chain rule (backpropagation) to compute every weight's effect on the loss, then nudging every weight via gradient descent — the one mechanism every deeper architecture in this index (CNNs, RNNs, LSTMs, transformers) reuses.
