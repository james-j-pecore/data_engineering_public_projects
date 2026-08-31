"""
A 2-input, 2-hidden-unit, 2-output neural network — one forward pass and one
backpropagation update, implemented from scratch (no ML framework) so every
intermediate value can be inspected directly.

This is the classic worked example from Matt Mazur's backpropagation
tutorial (see README.md's Resources) — every number here was independently
hand/computer-verified against the chain-rule derivation in README.md before
this script was written.

Run:
    python neural_network.py
"""

import math

INPUTS = (0.05, 0.10)
TARGETS = (0.01, 0.99)
B1, B2 = 0.35, 0.60  # biases, shared across the two units in each layer
LEARNING_RATE = 0.5


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def forward_pass(w: dict) -> tuple:
    """Return (out_h1, out_h2, out_o1, out_o2) for the current weights."""
    i1, i2 = INPUTS
    net_h1 = w["w1"] * i1 + w["w2"] * i2 + B1
    net_h2 = w["w3"] * i1 + w["w4"] * i2 + B1
    out_h1, out_h2 = sigmoid(net_h1), sigmoid(net_h2)

    net_o1 = w["w5"] * out_h1 + w["w6"] * out_h2 + B2
    net_o2 = w["w7"] * out_h1 + w["w8"] * out_h2 + B2
    out_o1, out_o2 = sigmoid(net_o1), sigmoid(net_o2)

    return out_h1, out_h2, out_o1, out_o2


def total_error(out_o1: float, out_o2: float) -> float:
    target_o1, target_o2 = TARGETS
    return 0.5 * (target_o1 - out_o1) ** 2 + 0.5 * (target_o2 - out_o2) ** 2


def backward_pass(w: dict) -> dict:
    """Run one backpropagation update and return the new weights."""
    i1, i2 = INPUTS
    target_o1, target_o2 = TARGETS
    out_h1, out_h2, out_o1, out_o2 = forward_pass(w)

    # Output layer: dL/d(out) * d(out)/d(net) for each output unit.
    d_o1 = -(target_o1 - out_o1) * out_o1 * (1 - out_o1)
    d_o2 = -(target_o2 - out_o2) * out_o2 * (1 - out_o2)

    d_w5, d_w6 = d_o1 * out_h1, d_o1 * out_h2
    d_w7, d_w8 = d_o2 * out_h1, d_o2 * out_h2

    # Hidden layer: each hidden unit's error is the sum of its contribution
    # to BOTH output units' errors, propagated back through w5..w8.
    d_h1 = (d_o1 * w["w5"] + d_o2 * w["w7"]) * out_h1 * (1 - out_h1)
    d_h2 = (d_o1 * w["w6"] + d_o2 * w["w8"]) * out_h2 * (1 - out_h2)

    d_w1, d_w2 = d_h1 * i1, d_h1 * i2
    d_w3, d_w4 = d_h2 * i1, d_h2 * i2

    grads = dict(w1=d_w1, w2=d_w2, w3=d_w3, w4=d_w4,
                 w5=d_w5, w6=d_w6, w7=d_w7, w8=d_w8)
    return {name: value - LEARNING_RATE * grads[name] for name, value in w.items()}


if __name__ == "__main__":
    weights = dict(w1=0.15, w2=0.20, w3=0.25, w4=0.30,
                   w5=0.40, w6=0.45, w7=0.50, w8=0.55)

    *_, out_o1, out_o2 = forward_pass(weights)
    print("Total error before update:", total_error(out_o1, out_o2))

    weights = backward_pass(weights)
    print("w5 after one update:", weights["w5"])
    print("w1 after one update:", weights["w1"])

    *_, out_o1, out_o2 = forward_pass(weights)
    print("Total error after one update:", total_error(out_o1, out_o2))
