# Long Short-Term Memory (LSTM)

## Overview

An LSTM is a variant of the [RNN](../15.recurrent-neural-networks/README.md) cell, purpose-built to fix the vanishing-gradient problem that keeps plain RNNs from learning long-range dependencies. It does this by adding a second recurrent pathway — the **cell state** — that information can flow along with only *linear*, gate-controlled modifications, rather than being squashed through a $\tanh$ nonlinearity at every single timestep the way a plain RNN's hidden state is.

---

## Intuition

A plain RNN has exactly one place to store everything it needs to remember, and that memory is completely overwritten (via a $\tanh$) at every timestep — nothing is explicitly protected across time. An LSTM instead maintains a **cell state** $c_t$ that acts more like a conveyor belt running through time, with three learned **gates** deciding what happens to it at each step:

- The **forget gate** decides what fraction of the existing cell state to keep vs. discard.
- The **input gate** decides how much of a new candidate value to write into the cell state.
- The **output gate** decides how much of the (updated) cell state to actually expose as the hidden state used for output/prediction at this timestep.

Each gate is itself a small sigmoid-activated layer (output between 0 and 1, so it behaves like a learned, per-dimension "how much to let through" knob), and — critically — updating the cell state involves only elementwise multiplication and addition (see [Mathematical formulation](#mathematical-formulation)), not repeatedly passing it through a squashing nonlinearity like a plain RNN's hidden state. That's the specific design choice that lets gradients flow back through many timesteps largely unimpeded, as long as the forget gate stays open.

---

## Mathematical formulation

At each timestep, an LSTM cell takes the current input $x_t$, previous hidden state $h_{t-1}$, and previous cell state $c_{t-1}$, and computes:

**Forget gate** — how much of the old cell state to keep:

$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$$

**Input gate** and **candidate cell state** — how much of a new candidate value to add:

$$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i), \qquad \tilde{c}_t = \tanh(W_c \cdot [h_{t-1}, x_t] + b_c)$$

**Cell state update** — combining what's kept from before with what's newly written, entirely through elementwise operations:

$$c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t$$

**Output gate** and **hidden state** — how much of the (new) cell state to expose:

$$o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o), \qquad h_t = o_t \odot \tanh(c_t)$$

where $\odot$ denotes elementwise multiplication and $[h_{t-1}, x_t]$ denotes concatenation.

### Why this fixes vanishing gradients

Compare the cell-state update to a plain RNN's hidden-state update (see [RNN: Recurrence](../15.recurrent-neural-networks/README.md#recurrence)): $c_t$ depends on $c_{t-1}$ through **addition and elementwise multiplication by $f_t$** — not a matrix multiply followed by a squashing nonlinearity. When $f_t \approx 1$, gradients can flow backward through $c_t$ across many timesteps with very little shrinkage, in sharp contrast to a plain RNN, where every single timestep multiplies the gradient by the derivative of $\tanh$ (always $\leq 1$, and often much less) times the recurrent weight matrix. The gates themselves are learned, so the network can choose, per dimension, what's worth preserving across long spans of time and what should be forgotten quickly.

---

## Typical hyperparameters

### `hidden_size`

The dimensionality of $h_t$ and $c_t$ — same meaning as an RNN's `hidden_size`, just now sized for two state vectors (hidden and cell) instead of one.

```python
nn.LSTM(input_size=10, hidden_size=32)
```

### `num_layers`

Stacking LSTM layers, same idea as stacking plain RNN layers.

### `bidirectional`

Same trade-off as for plain RNNs (see [RNN: Typical hyperparameters](../15.recurrent-neural-networks/README.md#bidirectional)) — useful when the full sequence is available upfront, not for autoregressive generation.

### `dropout`

Applied between stacked LSTM layers (not within a single layer's recurrence) as a standard overfitting countermeasure, same underlying idea as dropout in any neural network.

### Modeling choices that matter more than any single constructor argument

- **Forget gate bias initialization** — initializing $b_f$ to a positive value (e.g., 1) at the start of training is a well-known practical trick that biases the network toward *remembering by default* early in training, which noticeably helps optimization on long sequences.
- Whether an LSTM is still the right choice at all — for many sequence tasks today, transformer-based architectures (see [LLMs](../17.large-language-models/README.md)) have matched or exceeded LSTM performance while parallelizing far better across a sequence during training; LSTMs remain a strong, lighter-weight choice for smaller-scale or genuinely streaming/online sequence problems.
- Gradient clipping — still standard practice, even though LSTMs are considerably more resistant to exploding/vanishing gradients than plain RNNs.

---

## Advantages

**Substantially better long-range gradient flow than a plain RNN**, directly from the additive, gated cell-state update described above — the entire reason this architecture exists.

**Learned, per-dimension control over memory** — the network decides, via the forget/input/output gates, what to retain and for how long, rather than every timestep uniformly overwriting the hidden state.

**Drop-in replacement for a plain RNN cell** — same input/output interface (sequence in, sequence or final state out), so it fits into the same architectures (stacked, bidirectional, encoder-decoder) with a straightforward swap.

**Well-established and battle-tested** for sequence tasks — speech recognition, time series forecasting, and (before transformers took over) machine translation and language modeling all had long production runs built on LSTMs.

---

## Limitations

**Still fundamentally sequential** — like a plain RNN, computing $h_t$ requires $h_{t-1}$ and $c_{t-1}$ first, so a single sequence's forward/backward pass can't be parallelized across timesteps the way convolution or attention can, which matters a great deal for training speed on modern hardware.

**More parameters and compute per cell than a plain RNN** — four sets of weights (forget, input, candidate, output) instead of one, roughly quadrupling the per-timestep computation.

**Doesn't fully eliminate long-range difficulty, just substantially mitigates it** — extremely long sequences (thousands of steps) can still be challenging; attention-based architectures generally handle very long-range dependencies more directly (every position can attend to every other position in one step, rather than information having to survive being passed through a gated state at every intermediate step).

**Largely superseded by transformer-based architectures** for the largest-scale sequence modeling tasks (particularly language), for the parallelism reason above — though LSTMs remain very much in production use for smaller or latency-sensitive sequence problems where a full transformer is unnecessary or too costly.

**Same black-box interpretability limitations** as any neural network — gate activations can be inspected, but there's no compact structural summary of "what the model learned" the way a decision tree has.

---

## Simple example

A single LSTM cell, single hidden unit, one timestep, with:

$$W_{f,x}=0.5,\ W_{f,h}=0.3,\ b_f=0.1 \qquad W_{i,x}=0.4,\ W_{i,h}=0.2,\ b_i=0$$
$$W_{c,x}=0.6,\ W_{c,h}=0.1,\ b_c=0 \qquad W_{o,x}=0.3,\ W_{o,h}=0.4,\ b_o=0.1$$

Inputs: $x_t=1.0$, $h_{t-1}=0.2$, $c_{t-1}=0.5$.

$$f_t = \sigma(0.5(1.0)+0.3(0.2)+0.1) = \sigma(0.66) = 0.6593$$
$$i_t = \sigma(0.4(1.0)+0.2(0.2)+0) = \sigma(0.44) = 0.6083$$
$$\tilde{c}_t = \tanh(0.6(1.0)+0.1(0.2)+0) = \tanh(0.62) = 0.5511$$
$$c_t = (0.6593)(0.5) + (0.6083)(0.5511) = 0.3297 + 0.3352 = 0.6649$$
$$o_t = \sigma(0.3(1.0)+0.4(0.2)+0.1) = \sigma(0.48) = 0.6177$$
$$h_t = (0.6177)\tanh(0.6649) = (0.6177)(0.5817) = 0.3593$$

### Python example

See [`long_short_term_memory.py`](long_short_term_memory.py) for the runnable version, implemented **from scratch with plain Python**:

```python
gates, c_t, h_t = lstm_cell_step(x_t=1.0, h_prev=0.2, c_prev=0.5, weights=WEIGHTS)
print("f_t, i_t, c_tilde, o_t:", gates)
print("c_t:", c_t)
print("h_t:", h_t)
```

Expected output (matches the hand computation above):

```text
f_t, i_t, c_tilde, o_t: (0.6593, 0.6083, 0.5511, 0.6177)
c_t: 0.6649
h_t: 0.3593
```

---

## Resources

- [Christopher Olah, "Understanding LSTM Networks"](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — the canonical, diagram-heavy walkthrough of exactly how information flows through an LSTM cell; the notation above follows this post closely.
- [Hochreiter & Schmidhuber, "Long Short-Term Memory" (1997)](https://www.bioinf.jku.at/publications/older/2604.pdf) — the original paper.
- [PyTorch `LSTM` documentation](https://pytorch.org/docs/stable/generated/torch.nn.LSTM.html) — the standard framework-level implementation.
- [*Deep Learning* (Goodfellow, Bengio, Courville), Ch. 10.10](https://www.deeplearningbook.org/) — LSTMs and gated RNNs within the broader treatment of sequence modeling.

### Core fact to retain

> An LSTM adds a separately-maintained cell state that flows across timesteps through addition and elementwise gating rather than a repeated nonlinear squash — the specific design choice that fixes a plain RNN's vanishing-gradient problem and lets the network learn what to remember and for how long.
