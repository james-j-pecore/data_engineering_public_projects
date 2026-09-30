"""Seasonality and year-over-year growth decomposition.

The goal in both cases is to decompose a revenue change into its mechanical
drivers (more orders? bigger baskets? higher prices?) rather than reporting
the revenue change alone.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("year_month")
    out = g.agg(
        revenue=("revenue", "sum"),
        units=("order_qty", "sum"),
        gross_profit=("gross_profit", "sum"),
    )
    out["orders"] = g["base_order_id"].nunique()
    out["aov"] = out["revenue"] / out["orders"]
    out["units_per_order"] = out["units"] / out["orders"]
    out.index = out.index.to_timestamp()
    return out


def seasonal_index_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Average revenue/orders/AOV by calendar month (1-12), pooled across all
    years in the dataset, indexed to the all-month average = 100."""
    g = df.groupby("order_month")
    out = g.agg(
        revenue=("revenue", "sum"),
        units=("order_qty", "sum"),
    )
    out["orders"] = g["base_order_id"].nunique()
    out["aov"] = out["revenue"] / out["orders"]
    out["revenue_index"] = out["revenue"] / out["revenue"].mean() * 100
    out["aov_index"] = out["aov"] / out["aov"].mean() * 100
    out["orders_index"] = out["orders"] / out["orders"].mean() * 100
    return out


def revenue_driver_decomposition(df: pd.DataFrame) -> dict:
    """Log-variance decomposition of monthly revenue into its two multiplicative
    components, log(revenue) = log(orders) + log(AOV): how much of the
    month-to-month swing in revenue is attributable to order-count variance vs.
    AOV variance (plus their covariance, which can be negative)."""
    m = monthly_trend(df)
    log_rev, log_orders, log_aov = np.log(m["revenue"]), np.log(m["orders"]), np.log(m["aov"])
    var_rev = log_rev.var()
    var_orders, var_aov = log_orders.var(), log_aov.var()
    cov_term = 2 * log_orders.cov(log_aov)
    return {
        "corr_revenue_orders": round(m["revenue"].corr(m["orders"]), 4),
        "corr_revenue_aov": round(m["revenue"].corr(m["aov"]), 4),
        "orders_share_of_log_variance": round(var_orders / var_rev, 4),
        "aov_share_of_log_variance": round(var_aov / var_rev, 4),
        "covariance_share_of_log_variance": round(cov_term / var_rev, 4),
    }


def yearly_growth(df: pd.DataFrame, exclude_partial_years: bool = True) -> pd.DataFrame:
    """Year-over-year revenue/customer/order growth. 2013 and 2017 are partial
    calendar years in this dataset (Feb 2013 - Feb 2017 coverage), so they are
    flagged; pass exclude_partial_years=False to keep them in the growth calc."""
    g = df.groupby("order_year")
    out = g.agg(
        revenue=("revenue", "sum"),
        units=("order_qty", "sum"),
        customers=("Customer Name", "nunique"),
    )
    out["orders"] = g["base_order_id"].nunique()
    out["aov"] = out["revenue"] / out["orders"]
    out["revenue_per_customer"] = out["revenue"] / out["customers"]

    month_counts = df.groupby("order_year")["order_month"].nunique()
    out["months_observed"] = month_counts
    out["is_partial_year"] = out["months_observed"] < 12

    calc = out.copy()
    if exclude_partial_years:
        calc = calc[~calc["is_partial_year"]]
    calc = calc.sort_index()
    out["revenue_growth"] = calc["revenue"].pct_change().reindex(out.index)
    out["customer_growth"] = calc["customers"].pct_change().reindex(out.index)
    out["order_growth"] = calc["orders"].pct_change().reindex(out.index)
    return out
