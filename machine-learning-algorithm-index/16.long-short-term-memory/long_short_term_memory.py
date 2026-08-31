"""
A single LSTM cell, one timestep, single hidden unit — from scratch.

Companion code for README.md's "Simple example" section. Implemented with
plain Python (no ML framework) so the arithmetic matches the hand
computation in README.md exactly.

Run:
    python long_short_term_memory.py
"""

import math

WEIGHTS = dict(
    Wf_x=0.5, Wf_h=0.3, bf=0.1,
    Wi_x=0.4, Wi_h=0.2, bi=0.0,
    Wc_x=0.6, Wc_h=0.1, bc=0.0,
    Wo_x=0.3, Wo_h=0.4, bo=0.1,
)


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def lstm_cell_step(x_t: float, h_prev: float, c_prev: float, weights: dict) -> tuple:
    """Run one LSTM cell timestep. Returns ((f_t, i_t, c_tilde, o_t), c_t, h_t)."""
    w = weights
    f_t = sigmoid(w["Wf_x"] * x_t + w["Wf_h"] * h_prev + w["bf"])
    i_t = sigmoid(w["Wi_x"] * x_t + w["Wi_h"] * h_prev + w["bi"])
    c_tilde = math.tanh(w["Wc_x"] * x_t + w["Wc_h"] * h_prev + w["bc"])
    c_t = f_t * c_prev + i_t * c_tilde
    o_t = sigmoid(w["Wo_x"] * x_t + w["Wo_h"] * h_prev + w["bo"])
    h_t = o_t * math.tanh(c_t)

    return (f_t, i_t, c_tilde, o_t), c_t, h_t


if __name__ == "__main__":
    gates, c_t, h_t = lstm_cell_step(x_t=1.0, h_prev=0.2, c_prev=0.5, weights=WEIGHTS)

    print("f_t, i_t, c_tilde, o_t:", tuple(round(g, 4) for g in gates))
    print("c_t:", round(c_t, 4))
    print("h_t:", round(h_t, 4))
