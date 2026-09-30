"""Chart functions. Each takes already-computed metrics (never raw data) and
writes one PNG to the images/ directory. No dual-axis charts -- a second metric
on a different scale gets its own panel (small multiples) instead. Colors are
assigned per entity from a fixed map, never by post-sort position, so the same
category keeps the same color across every chart it appears in."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from .style import CATEGORICAL, INK, save

IMAGES_DIR = Path(__file__).resolve().parents[2] / "images"

# Fixed entity -> color maps (first-slot-first, in the order each dimension's
# values are most naturally introduced), so identity never shifts with sort order.
CATEGORY_COLORS = {"Office Supplies": CATEGORICAL[0], "Technology": CATEGORICAL[1], "Furniture": CATEGORICAL[2]}
SEGMENT_COLORS = {
    "Corporate": CATEGORICAL[0], "Home Office": CATEGORICAL[1],
    "Small Business": CATEGORICAL[2], "Consumer": CATEGORICAL[3],
}
GEO_COLORS = {"NSW|Sydney": CATEGORICAL[0], "VIC|Melbourne": CATEGORICAL[1]}
SHIP_MODE_COLORS = {"Regular Air": CATEGORICAL[0], "Express Air": CATEGORICAL[1], "Delivery Truck": CATEGORICAL[2]}
PRIORITY_COLORS = {
    "Critical": CATEGORICAL[7], "High": CATEGORICAL[1], "Medium": CATEGORICAL[3],
    "Low": CATEGORICAL[0], "Not Specified": INK["muted"],
}
QUADRANT_COLORS = {"Star": CATEGORICAL[0], "Traffic Driver": CATEGORICAL[1], "Niche": CATEGORICAL[2], "Rationalize": INK["muted"]}


def _compact_money(x: float) -> str:
    ax_ = abs(x)
    if ax_ >= 1_000_000:
        return f"${x/1_000_000:,.1f}M"
    if ax_ >= 1_000:
        return f"${x/1_000:,.1f}K"
    return f"${x:,.0f}"


def _money_fmt(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: _compact_money(x))
    axis_obj = ax.yaxis if axis == "y" else ax.xaxis
    axis_obj.set_major_formatter(fmt)
    axis_obj.set_major_locator(mticker.MaxNLocator(nbins=5))


def _pct_fmt(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"{x:.0%}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def plot_category_revenue_margin(cat: pd.DataFrame, path: Path = IMAGES_DIR / "01_category_revenue_margin.png"):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    cat = cat.sort_values("revenue", ascending=True)
    colors = [CATEGORY_COLORS[c] for c in cat.index]

    ax = axes[0]
    ax.barh(cat.index, cat["revenue"], color=colors, height=0.6)
    ax.set_title("Revenue", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    _money_fmt(ax, "x")
    ax.grid(axis="y", visible=False)

    ax = axes[1]
    ax.barh(cat.index, cat["margin_pct"], color=colors, height=0.6)
    ax.set_title("Gross margin %", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    _pct_fmt(ax, "x")
    ax.set_xlim(0, cat["margin_pct"].max() * 1.25)
    ax.set_yticklabels([])
    ax.grid(axis="y", visible=False)

    save(fig, path, "Revenue leadership does not imply margin leadership",
         "Product Category: total revenue vs. gross margin %")
    return path


def plot_discount_analysis(bands: pd.DataFrame, path: Path = IMAGES_DIR / "02_discount_analysis.png"):
    bands = bands.dropna(subset=["avg_qty"])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    ax = axes[0]
    ax.bar(bands.index.astype(str), bands["avg_qty"], color=CATEGORICAL[0], width=0.6)
    ax.set_title("Avg. units per line item", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")

    ax = axes[1]
    ax.bar(bands.index.astype(str), bands["margin_pct"], color=CATEGORICAL[1], width=0.6)
    ax.set_title("Gross margin % (band total)", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    _pct_fmt(ax)
    ax.set_ylim(0, bands["margin_pct"].max() * 1.25)

    save(fig, path, "Discount depth shows no meaningful relationship to basket size or margin",
         "By Discount % band: average order quantity vs. resulting gross margin %")
    return path


def plot_segment_value(seg: pd.DataFrame, path: Path = IMAGES_DIR / "03_customer_segment_value.png"):
    seg = seg.sort_values("revenue_per_customer", ascending=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    colors = [SEGMENT_COLORS[c] for c in seg.index]

    ax = axes[0]
    ax.barh(seg.index, seg["revenue_per_customer"], color=colors, height=0.6)
    ax.set_title("Revenue per customer", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    _money_fmt(ax, "x")
    ax.grid(axis="y", visible=False)

    ax = axes[1]
    ax.barh(seg.index, seg["orders_per_customer"], color=colors, height=0.6)
    ax.set_title("Orders per customer", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    ax.set_yticklabels([])
    ax.grid(axis="y", visible=False)

    save(fig, path, "Customer Type value ranking, not just sales share",
         "Customer Type: revenue per customer vs. order frequency per customer")
    return path


def plot_lorenz(lorenz: pd.DataFrame, top20_share: float, path: Path = IMAGES_DIR / "04_customer_concentration.png"):
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ax.plot(lorenz["cum_customer_share"], lorenz["cum_revenue_share"], color=CATEGORICAL[0], linewidth=2.5, label="Actual revenue distribution")
    ax.plot([0, 1], [0, 1], color=INK["baseline"], linewidth=1.5, linestyle="--", label="Perfect equality")
    ax.fill_between(lorenz["cum_customer_share"], lorenz["cum_revenue_share"], lorenz["cum_customer_share"], color=CATEGORICAL[0], alpha=0.08)
    ax.axvline(0.2, color=INK["muted"], linewidth=0.8, linestyle=":")
    ax.annotate(f"top 20% of customers\n= {top20_share:.0%} of revenue", xy=(0.2, top20_share),
                xytext=(0.34, top20_share - 0.22), fontsize=9.5, color=INK["secondary"],
                arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.8))
    _pct_fmt(ax, "x")
    _pct_fmt(ax, "y")
    ax.set_xlabel("Cumulative share of customers")
    ax.set_ylabel("Cumulative share of revenue")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, path, "Revenue concentration across the customer base",
         "Lorenz curve: cumulative customers (ranked by spend) vs. cumulative revenue")
    return path


def plot_rfm_segments(rfm_seg: pd.DataFrame, path: Path = IMAGES_DIR / "05_rfm_segments.png"):
    rfm_seg = rfm_seg.sort_values("revenue_share", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(rfm_seg))
    height = 0.35
    ax.barh(y + height / 2, rfm_seg["customer_share"], height=height, color=INK["baseline"], label="Share of customers")
    ax.barh(y - height / 2, rfm_seg["revenue_share"], height=height, color=CATEGORICAL[0], label="Share of revenue")
    ax.set_yticks(y)
    ax.set_yticklabels(rfm_seg.index)
    _pct_fmt(ax, "x")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", visible=False)
    save(fig, path, "RFM segments: customer share vs. revenue share",
         "Recency / Frequency / Monetary segmentation, quartile-scored per customer")
    return path


def plot_monthly_seasonality(monthly: pd.DataFrame, path: Path = IMAGES_DIR / "06_monthly_seasonality.png"):
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [1.4, 1]})

    ax = axes[0]
    ax.plot(monthly.index, monthly["revenue"], color=CATEGORICAL[0], linewidth=2)
    ax.fill_between(monthly.index, monthly["revenue"], color=CATEGORICAL[0], alpha=0.08)
    ax.set_title("Monthly revenue", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    _money_fmt(ax)
    ax.set_ylim(0, None)

    ax = axes[1]
    idx_aov = monthly["aov"] / monthly["aov"].mean() * 100
    idx_orders = monthly["orders"] / monthly["orders"].mean() * 100
    ax.plot(monthly.index, idx_orders, color=CATEGORICAL[2], linewidth=1.8, label="Order count (indexed, avg=100)")
    ax.plot(monthly.index, idx_aov, color=CATEGORICAL[1], linewidth=1.8, label="AOV (indexed, avg=100)")
    ax.axhline(100, color=INK["baseline"], linewidth=0.8, linestyle=":")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("What's driving the swings: order volume vs. basket value", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")

    save(fig, path, "Monthly revenue swings track AOV more closely than order volume",
         "Feb 2013 - Feb 2017 monthly revenue, decomposed into order count vs. AOV (both indexed to their own average)")
    return path


def plot_yearly_growth(yearly: pd.DataFrame, path: Path = IMAGES_DIR / "07_yearly_growth.png"):
    yearly = yearly.dropna(subset=["revenue_growth"])
    fig, ax = plt.subplots(figsize=(8.5, 5))
    x = np.arange(len(yearly))
    width = 0.35
    ax.bar(x - width / 2, yearly["revenue_growth"], width, color=CATEGORICAL[0], label="Revenue growth")
    ax.bar(x + width / 2, yearly["customer_growth"], width, color=CATEGORICAL[2], label="Active-customer growth")
    ax.axhline(0, color=INK["baseline"], linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in yearly.index])
    _pct_fmt(ax)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="x", visible=False)
    save(fig, path, "Year-over-year: is growth coming from spend-per-customer or new customers?",
         "Full calendar years only (2014-2016; 2013 and 2017 are partial in this dataset)")
    return path


def plot_geography(state: pd.DataFrame, path: Path = IMAGES_DIR / "08_geography.png"):
    keys = [f"{st}|{city}" for st, city in state.index]
    labels = [f"{city}, {st}" for st, city in state.index]
    colors = [GEO_COLORS[k] for k in keys]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))

    for ax, col, title, fmt in [
        (axes[0], "revenue_share", "Share of revenue", "pct"),
        (axes[1], "revenue_per_customer", "Revenue per customer", "money"),
        (axes[2], "margin_pct", "Gross margin %", "pct"),
    ]:
        ax.bar(labels, state[col], color=colors, width=0.5)
        ax.set_title(title, loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
        if fmt == "pct":
            _pct_fmt(ax)
            ax.set_ylim(0, state[col].max() * 1.25)
        else:
            _money_fmt(ax)
            ax.set_ylim(0, state[col].max() * 1.25)
        ax.grid(axis="x", visible=False)

    save(fig, path, "Market scale vs. customer quality: Sydney (NSW) vs. Melbourne (VIC)",
         "Sydney carries the larger revenue *share* primarily through a larger customer base")
    return path


def plot_fulfillment(ship_mode: pd.DataFrame, priority: pd.DataFrame, path: Path = IMAGES_DIR / "09_fulfillment.png"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    colors = [SHIP_MODE_COLORS[m] for m in ship_mode.index]
    ax.bar(ship_mode.index, ship_mode["avg_ship_days"], color=colors, width=0.5)
    ax.set_title("Avg. days to ship, by Ship Mode", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    ax.set_ylabel("days")
    ax.set_ylim(0, ship_mode["avg_ship_days"].max() * 1.3)
    ax.grid(axis="x", visible=False)
    for i, v in enumerate(ship_mode["avg_ship_days"]):
        ax.text(i, v + 0.06, f"{v:.1f}d", ha="center", fontsize=9, color=INK["secondary"])

    ax = axes[1]
    colors2 = [PRIORITY_COLORS[p] for p in priority.index]
    ax.bar(priority.index, priority["avg_ship_days"], color=colors2, width=0.5)
    ax.set_title("Avg. days to ship, by Order Priority", loc="left", fontsize=11, color=INK["secondary"], fontweight="normal")
    ax.set_ylim(0, priority["avg_ship_days"].max() * 1.3)
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="x", visible=False)
    for i, v in enumerate(priority["avg_ship_days"]):
        ax.text(i, v + 0.06, f"{v:.1f}d", ha="center", fontsize=9, color=INK["secondary"])

    save(fig, path, "Does Ship Mode or Order Priority actually change delivery speed?",
         "Rows with a negative ship-minus-order gap (data-entry errors, 1.5% of lines) are excluded")
    return path


def plot_product_matrix(prod: pd.DataFrame, path: Path = IMAGES_DIR / "10_product_portfolio_matrix.png"):
    fig, ax = plt.subplots(figsize=(9, 6.5))
    for q, color in QUADRANT_COLORS.items():
        sub = prod[prod["quadrant"] == q]
        ax.scatter(sub["revenue"], sub["margin_pct"], s=28, color=color, alpha=0.8, label=f"{q} ({len(sub)})", edgecolors="white", linewidths=0.4)

    rev_med = prod.attrs.get("revenue_median", prod["revenue"].median())
    margin_med = prod.attrs.get("margin_median", prod["margin_pct"].median())
    ax.axvline(rev_med, color=INK["baseline"], linewidth=0.8, linestyle=":")
    ax.axhline(margin_med, color=INK["baseline"], linewidth=0.8, linestyle=":")
    ax.set_xscale("log")
    tick_vals = [5_000, 15_000, 50_000, 150_000, 500_000, 1_000_000]
    ax.set_xticks(tick_vals)
    ax.set_xticklabels([_compact_money(v) for v in tick_vals])
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    _pct_fmt(ax, "y")
    ax.set_xlabel("Total revenue (log scale)")
    ax.set_ylabel("Gross margin %")
    ax.legend(loc="lower right", fontsize=9, title="Quadrant (n products)", title_fontsize=9)
    save(fig, path, "Product portfolio: revenue scale vs. margin quality",
         f"{len(prod)} products with >=5 line items; dotted lines mark the median revenue/margin split")
    return path
