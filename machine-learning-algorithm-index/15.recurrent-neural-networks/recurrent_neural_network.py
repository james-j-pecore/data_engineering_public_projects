"""
A single-hidden-unit RNN, unrolled over 3 timesteps — from scratch.

Companion code for README.md's "Simple example" section. Implemented with
plain Python (no ML framework) so the arithmetic matches the hand
computation in README.md exactly.

Run:
    python recurrent_neural_network.py
"""

import math


def run_rnn(inputs: list, w_xh: float, w_hh: float, w_hy: float,
            b_h: float = 0.0, b_y: float = 0.0, h0: float = 0.0) -> tuple:
    """Run a single-hidden-unit RNN over `inputs`, returning (hidden_states, outputs)."""
    h = h0
    hidden_states, outputs = [], []
    for x_t in inputs:
        h = math.tanh(w_xh * x_t + w_hh * h + b_h)
        y = w_hy * h + b_y
        hidden_states.append(h)
        outputs.append(y)
    return hidden_states, outputs


if __name__ == "__main__":
    hidden_states, outputs = run_rnn(
        inputs=[1.0, 0.5, -1.0], w_xh=0.5, w_hh=0.8, w_hy=1.0
    )
    for t, (h, y) in enumerate(zip(hidden_states, outputs), start=1):
        print(f"t={t}: h_t={h:.4f}, y_t={y:.4f}")
