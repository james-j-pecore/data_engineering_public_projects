"""Revenue vs. profitability decomposition: category mix, discount behavior,
and the product-level Stars / Traffic-Drivers / Niche / Rationalize matrix."""

from __future__ import annotations

import pandas as pd


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue, margin, and order economics by Product Category."""
    orders = df.groupby("Product Category")["base_order_id"].nunique()
    out = df.groupby("Product Category").agg(
        revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        units=("order_qty", "sum"),
        line_items=("Order No", "count"),
        avg_unit_price=("retail_price", "mean"),
    )
    out["orders"] = orders
    out["margin_pct"] = out["gross_profit"] / out["revenue"]
    out["revenue_per_order"] = out["revenue"] / out["orders"]
    out["revenue_share"] = out["revenue"] / out["revenue"].sum()
    return out.sort_values("revenue", ascending=False)


def discount_bucket_analysis(df: pd.DataFrame, bin_width: int = 5) -> pd.DataFrame:
    """Compare average basket size, revenue, and profit per line item across
    Discount % levels -- tests whether deeper discounts buy incremental volume
    or just give away margin. This dataset's Discount % is discrete (integer
    0-10%), so each level is its own group rather than a binned range."""
    d = df.copy()
    d["discount_band"] = (d["discount_pct"] * 100).round().astype(int).astype(str) + "%"
    out = d.groupby("discount_band", observed=True).agg(
        line_items=("Order No", "count"),
        avg_qty=("order_qty", "mean"),
        avg_revenue=("revenue", "mean"),
        avg_gross_profit=("gross_profit", "mean"),
        avg_net_contribution=("net_contribution", "mean"),
        total_revenue=("revenue", "sum"),
        total_gross_profit=("gross_profit", "sum"),
    )
    out["margin_pct"] = out["total_gross_profit"] / out["total_revenue"]
    out["_sort"] = out.index.str.rstrip("%").astype(int)
    return out.sort_values("_sort").drop(columns="_sort")


def discount_correlations(df: pd.DataFrame) -> pd.Series:
    """Pearson correlation of Discount % against quantity/revenue/profit --
    associational only, not a causal elasticity estimate."""
    cols = ["discount_pct", "order_qty", "revenue", "gross_profit", "margin_pct"]
    return df[cols].corr()["discount_pct"].drop("discount_pct")


def product_portfolio_matrix(df: pd.DataFrame, min_line_items: int = 5) -> pd.DataFrame:
    """Classify each product into a revenue x margin quadrant:
    Stars (high revenue, high margin), Traffic Drivers (high revenue, low margin),
    Niche (low revenue, high margin), Rationalize (low revenue, low margin).
    Products with fewer than `min_line_items` orders are excluded as too thin
    to classify reliably."""
    prod = df.groupby(["Product Name", "Product Category"]).agg(
        revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        units=("order_qty", "sum"),
        line_items=("Order No", "count"),
    )
    prod = prod[prod["line_items"] >= min_line_items].copy()
    prod["margin_pct"] = prod["gross_profit"] / prod["revenue"]

    rev_median = prod["revenue"].median()
    margin_median = prod["margin_pct"].median()

    def classify(row):
        high_rev = row["revenue"] >= rev_median
        high_margin = row["margin_pct"] >= margin_median
        if high_rev and high_margin:
            return "Star"
        if high_rev and not high_margin:
            return "Traffic Driver"
        if not high_rev and high_margin:
            return "Niche"
        return "Rationalize"

    prod["quadrant"] = prod.apply(classify, axis=1)
    prod.attrs["revenue_median"] = rev_median
    prod.attrs["margin_median"] = margin_median
    return prod.sort_values("revenue", ascending=False)
