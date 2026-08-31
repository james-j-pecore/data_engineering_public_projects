# Recurrent Neural Networks (RNN)

## Overview

An RNN is a [neural network](../13.neural-networks/README.md) specialized for **sequential data** — text, time series, audio — built around a **hidden state** that's carried forward from one timestep to the next. The same weights are reused at every timestep (a sequential analogue of a [CNN](../14.convolutional-neural-networks/README.md)'s weight sharing across spatial positions), which lets an RNN process sequences of any length with a fixed number of parameters, and in principle lets information from early in a sequence influence predictions much later in it.

---

## Intuition

A plain feedforward network has no memory between calls — given the same input, it always produces the same output, with no notion of "what came before." That's a poor fit for sequences, where the meaning of the current input often depends heavily on context: "bank" means something different after "I sat by the river" than after "I withdrew cash from the."

An RNN adds a **hidden state** — a running summary of everything the network has seen in the sequence so far — that gets updated at every timestep and fed back in alongside the next input. Conceptually, "unrolling" an RNN across a sequence turns it into a very deep feedforward network with one layer per timestep, except every one of those layers **shares the exact same weights** — which is both the source of an RNN's efficiency (fixed parameter count regardless of sequence length) and its central training difficulty (see [Limitations](#limitations)).

---

## Mathematical formulation

### Recurrence

At each timestep $t$, the hidden state is updated from the current input $x_t$ and the *previous* hidden state $h_{t-1}$:

$$h_t = \tanh(W_{xh}\, x_t + W_{hh}\, h_{t-1} + b_h)$$

and an output (if one is produced at every timestep, as in sequence labeling) is read out from the hidden state:

$$y_t = W_{hy}\, h_t + b_y$$

The same $W_{xh}, W_{hh}, W_{hy}$ are used at every single timestep — this is the weight sharing that makes an RNN's parameter count independent of sequence length, and it's why $h_{t-1}$ appearing on both sides of a chain of these equations is exactly what gives the network the ability to (in principle) carry information arbitrarily far into the future.

### Backpropagation through time (BPTT)

Training an RNN uses the same backpropagation idea as any neural network (see [Neural Networks: Mathematical formulation](../13.neural-networks/README.md#backpropagation)), applied to the *unrolled* network across all timesteps. Because $W_{hh}$ is reused at every step, its gradient is a **sum of contributions from every timestep**:

$$\frac{\partial \mathcal{L}}{\partial W_{hh}} = \sum_{t=1}^{T} \frac{\partial \mathcal{L}_t}{\partial W_{hh}}$$

and each term in that sum involves a product of Jacobians going back through every intermediate timestep — which is exactly where the vanishing/exploding gradient problem (see [Limitations](#limitations)) comes from: that product can shrink toward zero or blow up as $T$ grows.

---

## Typical hyperparameters

### `hidden_size`

The dimensionality of $h_t$ — how much information the hidden state can carry forward at once. Larger hidden states can represent richer context but cost more compute and are more prone to overfitting on small datasets.

```python
nn.RNN(input_size=10, hidden_size=32)
```

### `num_layers`

Stacking RNN layers (the output sequence of one layer becomes the input sequence to the next) — a sequential analogue of adding depth in a feedforward network.

### `bidirectional`

Whether to also run a second RNN backward over the sequence and combine both directions' hidden states — useful whenever the *entire* sequence is available at prediction time (e.g., classifying a whole sentence) and both past and future context matter, but not applicable to autoregressive generation, where the future genuinely isn't available yet.

### Sequence length / truncated BPTT

Very long sequences are often processed in truncated chunks (backpropagating only a fixed number of steps back, not the entire sequence) purely for computational and gradient-stability reasons — a practical necessity more than a tunable "hyperparameter" in the usual sense.

### Modeling choices that matter more than any single constructor argument

- **Whether a plain RNN is even the right choice** — see [Limitations](#limitations); for most practical sequence lengths, [LSTM](../16.long-short-term-memory/README.md) (or GRU) cells have almost entirely replaced plain RNN cells, for reasons that are the entire subject of the next entry in this index.
- Gradient clipping — capping the gradient's norm during BPTT is close to mandatory in practice to prevent the exploding-gradient half of the problem described above from derailing training entirely.

---

## Advantages

**Handles variable-length sequences** with a fixed number of parameters, unlike a feedforward network, which needs a fixed-size input.

**Weight sharing across time**, the sequential analogue of a CNN's weight sharing across space — the same update rule applies regardless of how far into the sequence a given timestep is.

**Naturally suited to online/streaming use** — a hidden state can be updated one new input at a time without reprocessing the whole sequence from scratch.

**Conceptually simple recurrence** — the core update rule is a single equation, easy to reason about even though training it well in practice is not (see [Limitations](#limitations)).

---

## Limitations

**Vanishing and exploding gradients over long sequences** — as sketched in [Backpropagation through time](#backpropagation-through-time-bptt), gradients flowing back through many timesteps are repeatedly multiplied by the same Jacobian; if its dominant eigenvalue is less than 1, gradients vanish (early timesteps stop receiving any meaningful learning signal); if greater than 1, gradients explode. This is *the* defining limitation of plain RNNs and the direct motivation for [LSTM](../16.long-short-term-memory/README.md)'s gating mechanism.

**Struggles with long-range dependencies in practice** — even before gradients vanish numerically, a plain RNN's hidden state is a fixed-size summary that has to compress everything relevant from arbitrarily far in the past into the same number of dimensions, and information not actively reinforced tends to get overwritten by more recent inputs.

**Inherently sequential computation** — unlike a CNN's spatial convolutions (parallelizable across positions) or a transformer's attention (parallelizable across tokens, see [LLMs](../17.large-language-models/README.md)), computing $h_t$ strictly requires $h_{t-1}$ first, which limits how much a single sequence's training step can be parallelized on modern hardware.

**Mostly superseded in practice** — for the tasks plain RNNs were originally used for, LSTMs/GRUs (better gradient flow) and transformer-based architectures (better parallelism and long-range modeling) are now the default choices; plain RNNs are mainly of pedagogical and historical interest today, which is exactly their role in this index.

---

## Simple example

A single-input, single-hidden-unit RNN with $\tanh$ activation and a linear readout, run over 3 timesteps:

$$W_{xh}=0.5, \quad W_{hh}=0.8, \quad b_h=0, \quad W_{hy}=1, \quad b_y=0, \quad h_0=0$$

Input sequence: $x = (1.0,\ 0.5,\ -1.0)$.

$$h_1 = \tanh(0.5(1.0) + 0.8(0) + 0) = \tanh(0.5) = 0.4621, \qquad y_1 = 0.4621$$
$$h_2 = \tanh(0.5(0.5) + 0.8(0.4621)) = \tanh(0.6197) = 0.5509, \qquad y_2 = 0.5509$$
$$h_3 = \tanh(0.5(\text{-}1.0) + 0.8(0.5509)) = \tanh(\text{-}0.0593) = \text{-}0.0592, \qquad y_3 = \text{-}0.0592$$

Notice $h_3$ still carries a (small, positive-leaning) trace of the earlier inputs even though $x_3=-1.0$ alone would pull it negative — exactly the "hidden state carries context forward" mechanism in action, on a scale small enough to trace by hand.

### Python example

See [`recurrent_neural_network.py`](recurrent_neural_network.py) for the runnable version, implemented **from scratch with plain Python**:

```python
hidden_states, outputs = run_rnn(inputs=[1.0, 0.5, -1.0], w_xh=0.5, w_hh=0.8, w_hy=1.0)
for t, (h, y) in enumerate(zip(hidden_states, outputs), start=1):
    print(f"t={t}: h_t={h:.4f}, y_t={y:.4f}")
```

Expected output (matches the hand computation above):

```text
t=1: h_t=0.4621, y_t=0.4621
t=2: h_t=0.5509, y_t=0.5509
t=3: h_t=-0.0592, y_t=-0.0592
```

---

## Resources

- [PyTorch `RNN` documentation](https://pytorch.org/docs/stable/generated/torch.nn.RNN.html) — the standard framework-level implementation and its parameters.
- [Christopher Olah, "Understanding LSTM Networks"](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — opens with an excellent plain-RNN explanation before introducing why LSTMs were needed (directly relevant to [LSTM](../16.long-short-term-memory/README.md), the next entry in this index).
- [Stanford CS224n: NLP with Deep Learning](https://web.stanford.edu/class/cs224n/) — course notes covering RNNs, BPTT, and the vanishing gradient problem in depth.
- [*Deep Learning* (Goodfellow, Bengio, Courville), Ch. 10](https://www.deeplearningbook.org/) — the mathematical foundations of recurrent networks and BPTT in full generality.

### Core fact to retain

> An RNN carries a hidden state forward across timesteps using the same shared weights at every step — enabling variable-length sequence processing, but making gradients that flow back through many timesteps prone to vanishing or exploding, the problem LSTMs were specifically designed to fix.
