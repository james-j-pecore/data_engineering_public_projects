"""
Scaled dot-product self-attention on 3 toy tokens — from scratch.

Companion code for README.md's "Simple example" section: identity Q/K/V
projections (Q=K=V=X) isolate the attention mechanism itself from the
learned projections a real model would use. Implemented with plain Python
(no ML framework, no matrix library) so the arithmetic matches the hand
computation in README.md exactly.

Run:
    python large_language_model.py
"""

import math


def dot(a: list, b: list) -> float:
    return sum(x * y for x, y in zip(a, b))


def softmax(row: list) -> list:
    m = max(row)  # subtract max for numerical stability; doesn't change the result
    exps = [math.exp(v - m) for v in row]
    total = sum(exps)
    return [e / total for e in exps]


def scaled_dot_product_attention(Q: list, K: list, V: list) -> tuple:
    """Return (attention_weights, output) for token embeddings Q, K, V (each n_tokens x d)."""
    n, d_k = len(Q), len(Q[0])
    scale = math.sqrt(d_k)

    scores = [[dot(Q[i], K[j]) / scale for j in range(n)] for i in range(n)]
    weights = [softmax(row) for row in scores]

    output = [
        [sum(weights[i][j] * V[j][d] for j in range(n)) for d in range(len(V[0]))]
        for i in range(n)
    ]
    return weights, output


if __name__ == "__main__":
    X = [[1, 0], [0, 1], [1, 1]]  # 3 tokens, 2-dim embeddings

    weights, output = scaled_dot_product_attention(X, X, X)  # Q=K=V=X

    print("Attention weights:")
    for row in weights:
        print([round(v, 4) for v in row])

    print("Output:")
    for row in output:
        print([round(v, 4) for v in row])
