"""Download and clean the Kaggle "Retail Insights" dataset.

Source: https://www.kaggle.com/datasets/rajneesh231/retail-insights-a-comprehensive-sales-dataset
5,000 order line items, Feb 2013 - Feb 2017, synthetic Australian office-supply
retailer data (NSW/VIC only).

Data-quality note (see README "Data quality" section for the full writeup):
the supplied `Sub Total`, `Discount $`, `Order Total`, and `Total` columns do not
reliably reconcile with `Retail Price * Order Quantity` (mismatched on ~99% of
rows). `Profit Margin` (= Retail Price - Cost Price) is internally consistent.
Rather than trust the supplied aggregate columns, every financial metric in this
project is recomputed from the primitive fields: Cost Price, Retail Price,
Order Quantity, Discount %, and Shipping Cost.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

DATASET_SLUG = "rajneesh231/retail-insights-a-comprehensive-sales-dataset"


def download_dataset() -> Path:
    """Download (or reuse the local kagglehub cache of) the raw CSV. No Kaggle
    account/API key is required for this public dataset."""
    import kagglehub

    path = Path(kagglehub.dataset_download(DATASET_SLUG))
    csv_path = path / "data.csv"
    if not csv_path.exists():
        candidates = list(path.glob("*.csv"))
        if not candidates:
            raise FileNotFoundError(f"No CSV found in downloaded dataset at {path}")
        csv_path = candidates[0]
    return csv_path


def _money_to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(r"[\$,]", "", regex=True), errors="coerce"
    )


def _pct_to_float(series: pd.Series) -> pd.Series:
    return (
        pd.to_numeric(series.astype(str).str.replace("%", "", regex=False), errors="coerce")
        / 100.0
    )


def load_clean_data(csv_path: Path | str | None = None) -> pd.DataFrame:
    """Load the raw CSV and return a cleaned, analysis-ready DataFrame.

    Cleaning steps (each is a deliberate, documented decision):
      - Parse currency/percent strings to floats.
      - Parse Order Date / Ship Date (DD-MM-YYYY).
      - Drop the 1 row with a null Order Quantity (0.02% of rows) -- no
        reasonable imputation exists for a missing unit count.
      - Recompute revenue, cost, gross profit, margin %, and discount-adjusted
        net revenue directly from Cost Price / Retail Price / Order Quantity /
        Discount % -- the supplied Sub Total / Discount $ / Order Total / Total
        columns are NOT used for any downstream metric (see module docstring).
      - Derive `shipping_days` from Ship Date - Order Date and flag the rows
        where it is negative (ship date before order date) as a data-quality
        flag (`shipping_days_valid`) rather than silently dropping them, so
        callers can choose to exclude them from time-based fulfillment metrics.
      - Derive `base_order_id` (the order number before the "-N" line-item
        suffix) so order-level metrics (AOV, basket size) aren't inflated by
        counting each product line as its own order.
    """
    if csv_path is None:
        csv_path = download_dataset()

    df = pd.read_csv(csv_path)

    before = len(df)
    df = df.dropna(subset=["Order Quantity"]).copy()
    dropped_null_qty = before - len(df)

    df["order_date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y")
    df["ship_date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y")

    df["cost_price"] = _money_to_float(df["Cost Price"])
    df["retail_price"] = _money_to_float(df["Retail Price"])
    df["shipping_cost"] = _money_to_float(df["Shipping Cost"])
    df["discount_pct"] = _pct_to_float(df["Discount %"])
    df["order_qty"] = df["Order Quantity"].astype(int)

    df["base_order_id"] = df["Order No"].astype(str).str.split("-").str[0]

    # Recomputed financial truth -- see module docstring.
    df["revenue"] = df["retail_price"] * df["order_qty"]
    df["cost_total"] = df["cost_price"] * df["order_qty"]
    df["gross_profit"] = df["revenue"] - df["cost_total"]
    df["margin_pct"] = np.where(
        df["retail_price"] > 0, (df["retail_price"] - df["cost_price"]) / df["retail_price"], np.nan
    )
    df["discount_amount"] = df["revenue"] * df["discount_pct"]
    df["net_revenue"] = df["revenue"] - df["discount_amount"]
    df["net_contribution"] = df["net_revenue"] - df["cost_total"] - df["shipping_cost"]

    df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["shipping_days_valid"] = df["shipping_days"] >= 0

    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    df["year_month"] = df["order_date"].dt.to_period("M")

    df.attrs["dropped_null_qty_rows"] = dropped_null_qty
    df.attrs["negative_shipping_days_rows"] = int((~df["shipping_days_valid"]).sum())

    keep_cols = [
        "Order No", "base_order_id", "order_date", "ship_date",
        "Customer Name", "City", "State", "Customer Type", "Account Manager",
        "Order Priority", "Product Name", "Product Category", "Product Container",
        "Ship Mode",
        "cost_price", "retail_price", "margin_pct", "order_qty",
        "discount_pct", "discount_amount", "shipping_cost",
        "revenue", "cost_total", "gross_profit", "net_revenue", "net_contribution",
        "shipping_days", "shipping_days_valid",
        "order_year", "order_month", "year_month",
    ]
    return df[keep_cols].reset_index(drop=True)


if __name__ == "__main__":
    data = load_clean_data()
    print(f"Loaded {len(data):,} clean line items")
    print(f"Dropped (null qty): {data.attrs['dropped_null_qty_rows']}")
    print(f"Negative shipping-day rows flagged: {data.attrs['negative_shipping_days_rows']}")
    print(data.head())
