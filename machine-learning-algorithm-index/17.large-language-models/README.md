# Large Language Models (LLMs)

## Overview

A large language model is a [neural network](../13.neural-networks/README.md) — almost always a **transformer** — trained on enormous amounts of text to predict the next token in a sequence, then scaled up in parameters and data until that simple objective produces a model capable of far more than next-word prediction: following instructions, answering questions, writing code, reasoning through multi-step problems.

The architectural leap from [RNN](../15.recurrent-neural-networks/README.md)/[LSTM](../16.long-short-term-memory/README.md) sequence models is **self-attention**: instead of processing a sequence one token at a time through a recurrence, a transformer lets every token look directly at every other token in one step, which both models long-range dependencies more directly and — critically for training at this scale — parallelizes across the whole sequence rather than being stuck processing it step by step.

---

## Intuition

An LSTM has to route information from token 1 to token 500 through 499 sequential hidden-state updates, each one a potential place for that information to degrade. Self-attention instead lets token 500 directly compute "how relevant is token 1 to me right now?" in a single step, for every other token in the sequence simultaneously. That direct, all-pairs comparison is the mechanistic reason transformers handle long-range dependencies more gracefully than recurrent architectures — and because there's no step-by-step recurrence at all, every token's attention computation for a given layer can run in parallel on a GPU, which is what actually made training at today's scale computationally feasible.

**Tokenization** breaks text into subword pieces (not quite words, not quite characters) before any of this happens, so the model works over a manageable, fixed vocabulary rather than every possible whole word. Each token is mapped to a learned **embedding** vector, and a **positional encoding** is added so the model can tell *where* in the sequence a token is — self-attention on its own has no inherent notion of order, since it compares every pair of tokens symmetrically regardless of position.

**Pretraining** is just next-token prediction (minimizing cross-entropy loss, identical in kind to [Logistic Regression](../2.logistic-regression/README.md#mathematical-formulation)'s loss, just over a vocabulary-sized set of classes instead of 2) on a huge, broad text corpus. **Instruction tuning** and **RLHF** (reinforcement learning from human feedback) are additional training stages on top of that pretrained model, aimed at making its behavior follow instructions and match human preferences rather than just continuing text in a statistically plausible way.

---

## Mathematical formulation

### Scaled dot-product self-attention

For a sequence of token embeddings, each token's embedding is linearly projected into a **query** ($Q$), **key** ($K$), and **value** ($V$) vector. Attention output for the whole sequence is:

$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

Reading this left to right: $QK^\top$ computes a raw similarity score between every pair of tokens' query and key vectors (a large score means "this token's content is highly relevant to that query"); dividing by $\sqrt{d_k}$ (the key dimension) keeps those scores in a numerically well-behaved range; the softmax turns each token's row of scores into a proper probability distribution over "how much attention to pay to every other token"; and multiplying by $V$ produces, for every token, a weighted blend of every other token's value vector — weighted exactly by that attention distribution.

### Multi-head attention

Rather than one attention computation, the model runs several ("heads") in parallel, each with its own learned $Q$/$K$/$V$ projections, then concatenates their outputs. Different heads can end up specializing in different kinds of relationships (e.g., one head tracking syntactic dependency, another tracking coreference) — a similar spirit to a CNN's multiple filters per layer, each learning a different pattern.

### The transformer block

A full transformer layer wraps self-attention with residual connections and layer normalization, followed by a small feedforward network (the same fully-connected layer-with-nonlinearity idea from [Neural Networks](../13.neural-networks/README.md), applied independently to each token's representation):

$$x \leftarrow x + \text{MultiHeadAttention}(x), \qquad x \leftarrow x + \text{FeedForward}(\text{LayerNorm}(x))$$

Stacking many such blocks (dozens to over a hundred, in the largest models) is what "large" in "large language model" mostly refers to, along with a correspondingly large embedding dimension and attention head count.

### Causal masking

For autoregressive generation (predicting each next token from only what came before it), the attention computation is **masked** so a token can only attend to itself and earlier tokens, never later ones — otherwise the model could "cheat" during training by looking ahead at the very token it's supposed to be predicting.

---

## Typical hyperparameters

*(These mostly matter to people pretraining or fine-tuning a model from scratch; using an existing LLM through an API mainly involves the inference-time settings below instead.)*

### Model scale (parameters, layers, heads, context length)

Determines raw capability ceiling; scaling laws (empirically, performance improves smoothly and predictably as parameters, data, and compute all scale up together) are why the field has consistently pushed all three larger over time.

### `temperature` (inference-time)

Scales the logits before the final softmax when sampling the next token — lower temperature makes the output distribution more peaked (more deterministic, repetitive); higher temperature flattens it (more varied, more likely to include a low-probability but occasionally interesting or nonsensical token).

```python
client.messages.create(model="...", temperature=0.7, ...)
```

### `top_p` / `top_k` (inference-time)

Alternative ways to restrict sampling to only the most probable next tokens (top_p: smallest set of tokens whose cumulative probability exceeds $p$; top_k: the $k$ most probable tokens), rather than sampling from the full vocabulary every time.

### Context window

The maximum number of tokens the model can attend over at once — a hard architectural limit (self-attention's cost grows quadratically with sequence length, which is what makes very long context windows expensive) rather than a tunable knob in the usual sense.

### Modeling choices that matter more than any single constructor argument

- **Prompting/context construction** — for anyone building *with* an existing LLM rather than training one, how the input is structured (system instructions, few-shot examples, retrieved context — see [RAG](../18.retrieval-augmented-generation/README.md)) matters far more day to day than any inference parameter.
- Whether fine-tuning, retrieval augmentation, or better prompting actually solves the problem at hand — fine-tuning a base model is expensive and often unnecessary when the real issue is that the model simply doesn't have the relevant information in its weights, which retrieval augmentation addresses directly (see [RAG](../18.retrieval-augmented-generation/README.md)).

---

## Advantages

**General-purpose across an enormous range of language tasks** from a single pretrained model — translation, summarization, question answering, code generation — without needing a separately trained model per task, unlike essentially every other entry in this index.

**Attention parallelizes across the sequence during training**, unlike RNN/LSTM's inherently sequential recurrence, which is a major reason training at today's scale is computationally feasible at all.

**Directly models long-range dependencies** via all-pairs attention, rather than routing information through a chain of recurrent updates.

**In-context learning** — a sufficiently large pretrained model can often perform a new task reasonably well just from a few examples given in the prompt, without any weight updates at all, a qualitatively different capability from any earlier model in this index.

---

## Limitations

**Hallucination** — an LLM will confidently generate plausible-sounding but factually wrong text, since its training objective is "predict plausible next tokens," not "only state verified facts." This is the central motivation for [RAG](../18.retrieval-augmented-generation/README.md): grounding generation in retrieved, verifiable source text rather than relying purely on what got baked into the weights during training.

**Quadratic attention cost in sequence length** — doubling the context length roughly quadruples the compute (and memory) for self-attention, which is why context window size has historically been a hard architectural/cost trade-off, not just a setting to turn up freely.

**Enormous training cost and data requirements** — pretraining a frontier model requires massive compute clusters and web-scale text data, putting training a comparable model from scratch out of reach for nearly everyone; most practitioners use or fine-tune an existing pretrained model rather than training one.

**No inherent notion of truth or up-to-date knowledge** — a pretrained model's knowledge is frozen at its training cutoff and encoded implicitly across its weights, with no built-in mechanism to look up current information or cite where a fact came from.

**Sensitive to prompt phrasing** — the same underlying request phrased differently can produce meaningfully different outputs, an odd kind of fragility with no clean analogue in the classical models earlier in this index.

**Interpretability is an open research area**, not a solved problem — attention weights can be inspected but don't straightforwardly explain *why* a model produced a given output, especially in very deep, many-headed stacks.

---

## Simple example

Self-attention on 3 toy tokens with 2-dimensional embeddings, using **identity** query/key/value projection matrices ($Q=K=V=X$) — an intentional simplification that isolates the attention *mechanism* itself from the learned projections, which is where the actual pattern-learning would happen in a real model:

$$X = \begin{pmatrix} 1 & 0 \\ 0 & 1 \\ 1 & 1 \end{pmatrix}$$

Raw scores $QK^\top / \sqrt{d_k}$ (here $d_k=2$, so scale by $\sqrt{2}\approx 1.414$) — for example, token 1 vs. token 3: $\frac{(1,0)\cdot(1,1)}{\sqrt{2}} = \frac{1}{\sqrt{2}} = 0.7071$. The full matrix of scores:

$$\begin{pmatrix} 0.7071 & 0 & 0.7071 \\ 0 & 0.7071 & 0.7071 \\ 0.7071 & 0.7071 & 1.4142 \end{pmatrix}$$

Applying softmax to each row (so each token's attention weights over all tokens, including itself, sum to 1) gives, for token 1:

$$\text{softmax}(0.7071, 0, 0.7071) = (0.4011,\ 0.1978,\ 0.4011)$$

Token 1's output is then this row's weighted blend of every token's value vector $V=X$:

$$0.4011(1,0) + 0.1978(0,1) + 0.4011(1,1) = (0.8022,\ 0.5989)$$

Repeating for all 3 tokens gives the full attention output — every row is a context-aware blend of the original embeddings, weighted by how much each token "attends to" every other token.

### Python example

See [`large_language_model.py`](large_language_model.py) for the runnable version, implemented **from scratch with plain Python** (no framework, no matrix library):

```python
weights, output = scaled_dot_product_attention(X, X, X)  # Q=K=V=X (identity projections)
for row in output:
    print([round(v, 4) for v in row])
```

Expected output (matches the hand computation above):

```text
[0.8022, 0.5989]
[0.5989, 0.8022]
[0.7517, 0.7517]
```

---

## Resources

- [Vaswani et al., "Attention Is All You Need" (2017)](https://arxiv.org/abs/1706.03762) — the original transformer paper, source of the scaled dot-product attention formula used above.
- [Jay Alammar, "The Illustrated Transformer"](https://jalammar.github.io/illustrated-transformer/) — a widely used, diagram-heavy walkthrough of the full transformer architecture.
- [Anthropic's Claude API documentation](https://docs.claude.com/) — practical, production-facing documentation for prompting, context management, and inference-time parameters when *using* an LLM rather than training one.
- [Kaplan et al., "Scaling Laws for Neural Language Models" (2020)](https://arxiv.org/abs/2001.08361) — the empirical basis for "bigger model + more data + more compute reliably performs better," referenced above under [Typical hyperparameters](#typical-hyperparameters).

### Core fact to retain

> A large language model is a transformer trained on next-token prediction at massive scale — self-attention lets every token directly weigh every other token in one parallelizable step, which is both what makes long-range language understanding work and what made training at today's scale computationally possible in the first place.
