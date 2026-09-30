"""End-to-end analysis run: download -> clean -> compute every metric module ->
render charts to images/ -> write results/headline_numbers.json (the real
computed figures the README quotes, so the README never hand-waves a number).

Usage:
    .venv/bin/python scripts/run_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.loader import load_clean_data
from src.metrics import customers, fulfillment, geography, profitability, trends
from src.viz import plotting
from src.viz.style import apply_style


def main():
    apply_style()
    df = load_clean_data()
    print(f"Loaded {len(df):,} clean line items across {df['base_order_id'].nunique():,} orders "
          f"and {df['Customer Name'].nunique():,} customers "
          f"({df['order_date'].min().date()} - {df['order_date'].max().date()})")

    results = {}
    results["row_counts"] = {
        "line_items": len(df),
        "orders": int(df["base_order_id"].nunique()),
        "customers": int(df["Customer Name"].nunique()),
        "dropped_null_qty_rows": int(df.attrs["dropped_null_qty_rows"]),
        "negative_shipping_days_rows": int(df.attrs["negative_shipping_days_rows"]),
        "date_range": [str(df["order_date"].min().date()), str(df["order_date"].max().date())],
    }

    # --- Profitability ---------------------------------------------------
    cat = profitability.category_summary(df)
    plotting.plot_category_revenue_margin(cat)
    results["category_summary"] = cat.round(4).to_dict(orient="index")

    bands = profitability.discount_bucket_analysis(df)
    plotting.plot_discount_analysis(bands)
    results["discount_bands"] = bands.round(4).reset_index().assign(
        discount_band=lambda d: d["discount_band"].astype(str)
    ).set_index("discount_band").to_dict(orient="index")

    results["discount_correlations"] = profitability.discount_correlations(df).round(4).to_dict()

    prod_matrix = profitability.product_portfolio_matrix(df)
    plotting.plot_product_matrix(prod_matrix)
    results["product_portfolio_quadrant_counts"] = prod_matrix["quadrant"].value_counts().to_dict()
    results["product_portfolio_top5_by_revenue"] = (
        prod_matrix.head(5)[["revenue", "margin_pct", "quadrant"]].round(2).reset_index().to_dict(orient="records")
    )

    # --- Customers ---------------------------------------------------
    seg = customers.segment_summary(df)
    plotting.plot_segment_value(seg)
    results["segment_summary"] = seg.round(4).to_dict(orient="index")

    pareto = customers.pareto_concentration(df)
    lorenz = customers.lorenz_curve(df)
    plotting.plot_lorenz(lorenz, pareto["top20_revenue_share"])
    results["pareto_concentration"] = {k: v for k, v in pareto.items() if k != "customer_revenue"}

    rfm = customers.rfm_table(df)
    rfm_seg = customers.rfm_segment_summary(rfm)
    plotting.plot_rfm_segments(rfm_seg)
    results["rfm_segment_summary"] = rfm_seg.round(4).to_dict(orient="index")

    # --- Trends ---------------------------------------------------
    monthly = trends.monthly_trend(df)
    plotting.plot_monthly_seasonality(monthly)
    seasonal = trends.seasonal_index_by_month(df)
    results["seasonal_index_by_month"] = seasonal.round(2).to_dict(orient="index")
    results["peak_month"] = int(seasonal["revenue"].idxmax())
    results["trough_month"] = int(seasonal["revenue"].idxmin())
    results["revenue_driver_decomposition"] = trends.revenue_driver_decomposition(df)

    yearly = trends.yearly_growth(df)
    plotting.plot_yearly_growth(yearly)
    results["yearly_growth"] = yearly.round(4).reset_index().to_dict(orient="records")

    # --- Geography ---------------------------------------------------
    state = geography.state_summary(df)
    plotting.plot_geography(state)
    results["geography"] = {f"{st}|{city}": v for (st, city), v in state.round(4).to_dict(orient="index").items()}

    # --- Fulfillment ---------------------------------------------------
    ship_mode = fulfillment.ship_mode_summary(df)
    priority = fulfillment.order_priority_summary(df)
    plotting.plot_fulfillment(ship_mode, priority)
    results["ship_mode_summary"] = ship_mode.round(3).to_dict(orient="index")
    results["order_priority_summary"] = priority.round(3).to_dict(orient="index")
    results["express_air_roi"] = fulfillment.express_air_roi(df).round(3).to_dict(orient="index")

    mgr = fulfillment.account_manager_summary(df)
    results["account_manager_top5_by_revenue_per_customer"] = (
        mgr.sort_values("revenue_per_customer", ascending=False)
        .head(5)[["revenue", "customers", "revenue_per_customer", "pct_corporate"]]
        .round(2).reset_index().to_dict(orient="records")
    )
    results["account_manager_corporate_mix_correlation"] = round(
        fulfillment.account_manager_corporate_share_correlation(df), 4
    )

    out_path = ROOT / "results" / "headline_numbers.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"Wrote {out_path}")
    print(f"Charts written to {plotting.IMAGES_DIR}")


if __name__ == "__main__":
    main()
