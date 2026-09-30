"""Fulfillment operations: does Ship Mode / Order Priority actually buy
faster delivery, and is the Express Air premium worth it? Also account-manager
performance, normalized by customer-type mix rather than raw totals.

Rows with `shipping_days_valid == False` (ship date before order date -- a
data-entry error, 75 of 4,999 rows / 1.5%) are excluded from every time-based
metric in this module; they are kept in the revenue-based metrics elsewhere.
"""

from __future__ import annotations

import pandas as pd


def ship_mode_summary(df: pd.DataFrame) -> pd.DataFrame:
    valid = df[df["shipping_days_valid"]]
    g = valid.groupby("Ship Mode")
    out = g.agg(
        line_items=("Order No", "count"),
        avg_ship_days=("shipping_days", "mean"),
        median_ship_days=("shipping_days", "median"),
        avg_shipping_cost=("shipping_cost", "mean"),
    )
    return out.sort_values("avg_ship_days")


def order_priority_summary(df: pd.DataFrame) -> pd.DataFrame:
    valid = df[df["shipping_days_valid"]]
    priority_order = ["Critical", "High", "Medium", "Low", "Not Specified"]
    out = valid.groupby("Order Priority").agg(
        line_items=("Order No", "count"),
        avg_ship_days=("shipping_days", "mean"),
        median_ship_days=("shipping_days", "median"),
        avg_shipping_cost=("shipping_cost", "mean"),
    )
    return out.reindex([p for p in priority_order if p in out.index])


def express_air_roi(df: pd.DataFrame) -> pd.DataFrame:
    """Cost premium and days-saved of Express Air vs. Regular Air vs. Delivery
    Truck, plus a derived $-per-day-saved figure relative to the slowest mode."""
    summary = ship_mode_summary(df)
    baseline_days = summary["avg_ship_days"].max()
    summary = summary.copy()
    summary["days_saved_vs_slowest"] = baseline_days - summary["avg_ship_days"]
    summary["cost_premium_vs_slowest"] = (
        summary["avg_shipping_cost"] - summary.loc[summary["avg_ship_days"].idxmax(), "avg_shipping_cost"]
    )
    summary["cost_per_day_saved"] = summary["cost_premium_vs_slowest"] / summary["days_saved_vs_slowest"].replace(0, pd.NA)
    return summary


def account_manager_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("Account Manager")
    out = g.agg(
        revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        customers=("Customer Name", "nunique"),
    )
    out["orders"] = g["base_order_id"].nunique()
    out["revenue_per_customer"] = out["revenue"] / out["customers"]
    out["profit_per_customer"] = out["gross_profit"] / out["customers"]

    # Customer-type mix per manager, to show whether high totals are a
    # portfolio-composition artifact (e.g. more Corporate accounts) rather
    # than manager skill.
    mix = (
        df.groupby(["Account Manager", "Customer Type"])["Customer Name"]
        .nunique()
        .unstack(fill_value=0)
    )
    mix_share = mix.div(mix.sum(axis=1), axis=0)
    mix_share.columns = [f"pct_{c.lower().replace(' ', '_')}" for c in mix_share.columns]
    out = out.join(mix_share)
    return out.sort_values("revenue_per_customer", ascending=False)


def account_manager_corporate_share_correlation(df: pd.DataFrame) -> float:
    """Correlation between an account manager's revenue-per-customer and the
    share of their book that is Corporate customers -- tests whether apparent
    manager performance is really a portfolio-mix effect."""
    summary = account_manager_summary(df)
    if "pct_corporate" not in summary.columns:
        return float("nan")
    return summary["revenue_per_customer"].corr(summary["pct_corporate"])
