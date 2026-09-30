"""Geographic performance: separates market *scale* (total revenue, which
mostly reflects customer count) from customer *productivity* (revenue and
profit per customer) and *commercial quality* (margin %).

This dataset only contains two markets (Sydney/NSW and Melbourne/VIC), so the
comparison is a direct two-way split rather than a ranked table.
"""

from __future__ import annotations

import pandas as pd


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["State", "City"])
    out = g.agg(
        revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        customers=("Customer Name", "nunique"),
        units=("order_qty", "sum"),
    )
    out["orders"] = g["base_order_id"].nunique()
    out["margin_pct"] = out["gross_profit"] / out["revenue"]
    out["revenue_per_customer"] = out["revenue"] / out["customers"]
    out["profit_per_customer"] = out["gross_profit"] / out["customers"]
    out["revenue_share"] = out["revenue"] / out["revenue"].sum()
    return out.sort_values("revenue", ascending=False)
