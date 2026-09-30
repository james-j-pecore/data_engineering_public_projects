"""Shared matplotlib style: validated categorical/sequential/status palette
(light mode, since charts are static PNGs embedded in a GitHub README), fixed
hue order, thin marks, minimal chrome. See the dataviz skill's
references/palette.md for the source values and validation.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

# Fixed categorical order -- never cycled/reassigned per chart.
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

DIVERGING_BLUE_RED = {"pos": "#2a78d6", "neg": "#e34948", "mid": "#f0efec"}

STATUS = {"good": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}

INK = {
    "surface": "#fcfcfb",
    "primary": "#0b0b0b",
    "secondary": "#52514e",
    "muted": "#898781",
    "gridline": "#e1e0d9",
    "baseline": "#c3c2b7",
}


def apply_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": INK["surface"],
        "axes.facecolor": INK["surface"],
        "savefig.facecolor": INK["surface"],
        "text.color": INK["primary"],
        "axes.labelcolor": INK["secondary"],
        "axes.edgecolor": INK["baseline"],
        "xtick.color": INK["muted"],
        "ytick.color": INK["muted"],
        "axes.grid": True,
        "grid.color": INK["gridline"],
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 10.5,
        "legend.frameon": False,
        "figure.dpi": 150,
        "savefig.dpi": 150,
    })


def save(fig, path, title=None, subtitle=None):
    fig.tight_layout(rect=[0, 0, 1, 0.86] if title else None)
    if title:
        fig.suptitle(title, x=0.02, y=1.06, ha="left", fontsize=14, fontweight="bold", color=INK["primary"])
    if subtitle:
        fig.text(0.02, 0.995, subtitle, ha="left", va="top", fontsize=10, color=INK["secondary"])
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
