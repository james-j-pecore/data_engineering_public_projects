"""Reads dbt marts + the model-training outputs straight out of DuckDB
(read-only) and renders the NYC electricity consumption/cost dashboard.

Chart styling follows the same design-token system as the sibling
spotify-dbt-analytics-pipeline app (see dataviz skill references/palette.md):
single-hue-per-series for one-measure charts, fixed categorical hue order
(never cycled) whenever more than one entity is compared, and a legend
whenever 2+ series appear on one chart.
"""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DUCKDB_PATH = Path(__file__).resolve().parent.parent / "data" / "nyc_electricity.duckdb"

# Design tokens — see dataviz skill references/palette.md for the full system.
SURFACE = "#fcfcfb"
GRIDLINE = "#e1e0d9"
AXIS_LINE = "#c3c2b7"
INK_PRIMARY = "#0b0b0b"
INK_MUTED = "#898781"
GOOD = "#0ca30c"

CATEGORICAL = {
    "blue": "#2a78d6",
    "aqua": "#1baf7a",
    "yellow": "#eda100",
    "green": "#008300",
    "violet": "#4a3aa7",
}
SERIES_1 = CATEGORICAL["blue"]

# Fixed borough -> hue assignment so color always tracks the entity, never its
# rank in a given filter/legend.
BOROUGH_COLORS = {
    "BRONX": CATEGORICAL["blue"],
    "BROOKLYN": CATEGORICAL["aqua"],
    "MANHATTAN": CATEGORICAL["yellow"],
    "QUEENS": CATEGORICAL["green"],
    "STATEN ISLAND": CATEGORICAL["violet"],
}

st.set_page_config(page_title="NYC Electricity Consumption & Cost", page_icon="⚡", layout="wide")


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DUCKDB_PATH), read_only=True)


def query(sql: str) -> pd.DataFrame:
    return get_connection().execute(sql).fetchdf()


def style_fig(fig, x_gridlines: bool = False, y_gridlines: bool = False, show_legend: bool = False):
    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(color=INK_PRIMARY, family="system-ui, -apple-system, 'Segoe UI', sans-serif"),
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0) if show_legend else None,
    )
    fig.update_xaxes(showgrid=x_gridlines, gridcolor=GRIDLINE, linecolor=AXIS_LINE, tickfont=dict(color=INK_MUTED))
    fig.update_yaxes(showgrid=y_gridlines, gridcolor=GRIDLINE, linecolor=AXIS_LINE, tickfont=dict(color=INK_MUTED))
    return fig


if not DUCKDB_PATH.exists():
    st.error(f"No DuckDB file found at {DUCKDB_PATH}. Run the pipeline first (see README).")
    st.stop()

st.title("⚡ NYC Electricity Consumption & Cost")
st.caption(
    "NYCHA (public housing) monthly electric consumption and cost, 2010–2025, "
    "with regression-based one-step-ahead forecasting and grid-wide demand context."
)

# ---------------------------------------------------------------------------
# Top metrics
# ---------------------------------------------------------------------------
citywide = query("select * from main_intermediate.int_citywide_monthly order by revenue_month").copy()
citywide["revenue_month"] = pd.to_datetime(citywide["revenue_month"])

latest_month = citywide["revenue_month"].max()
trailing_12 = citywide[citywide["revenue_month"] > latest_month - pd.DateOffset(months=12)]
prior_12 = citywide[
    (citywide["revenue_month"] <= latest_month - pd.DateOffset(months=12))
    & (citywide["revenue_month"] > latest_month - pd.DateOffset(months=24))
]

trailing_kwh = trailing_12["consumption_kwh"].sum()
prior_kwh = prior_12["consumption_kwh"].sum()
yoy_pct = (trailing_kwh / prior_kwh - 1) * 100 if prior_kwh else float("nan")

dev_count = query("select count(distinct development_name) as n from main_marts.mart_development_monthly").iloc[0]["n"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Developments tracked", int(dev_count))
c2.metric("Trailing 12mo kWh", f"{trailing_kwh / 1e6:.1f}M")
c3.metric("Trailing 12mo cost", f"${trailing_12['current_charges'].sum() / 1e6:.1f}M")
c4.metric("YoY change", f"{yoy_pct:+.1f}%")

# ---------------------------------------------------------------------------
# Citywide NYCHA trend
# ---------------------------------------------------------------------------
st.subheader("NYCHA-wide monthly consumption")
fig = px.line(citywide, x="revenue_month", y="consumption_kwh", labels={"revenue_month": "", "consumption_kwh": "kWh"})
fig.update_traces(line_color=SERIES_1, hovertemplate="%{x|%b %Y}: %{y:,.0f} kWh<extra></extra>")
st.plotly_chart(style_fig(fig, x_gridlines=True, y_gridlines=True), use_container_width=True)

# ---------------------------------------------------------------------------
# NYCHA vs. grid-wide demand (AI / data-center context)
# ---------------------------------------------------------------------------
st.subheader("NYCHA consumption vs. NYC grid-wide load")
grid_vs_nycha = query("select * from main_marts.mart_citywide_vs_grid order by revenue_month").copy()
grid_vs_nycha["revenue_month"] = pd.to_datetime(grid_vs_nycha["revenue_month"])

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=grid_vs_nycha["revenue_month"], y=grid_vs_nycha["nycha_index"],
        name="NYCHA consumption (indexed)", line=dict(color=CATEGORICAL["blue"], width=2),
        hovertemplate="NYCHA: %{y:.1f}<extra></extra>",
    )
)
fig.add_trace(
    go.Scatter(
        x=grid_vs_nycha["revenue_month"], y=grid_vs_nycha["grid_index"],
        name="NYC grid load (indexed)", line=dict(color=CATEGORICAL["aqua"], width=2),
        hovertemplate="Grid: %{y:.1f}<extra></extra>",
    )
)
fig.add_vrect(x0="2022-01-01", x1=grid_vs_nycha["revenue_month"].max(), fillcolor=INK_MUTED, opacity=0.08, line_width=0)
fig.update_layout(yaxis_title="Index (first available month = 100)")
st.plotly_chart(style_fig(fig, x_gridlines=True, y_gridlines=True, show_legend=True), use_container_width=True)
st.caption(
    "Both series indexed to their first available month = 100. The shaded region marks 2022 onward, "
    "when AI/data-center buildout is commonly cited as a driver of grid demand growth. **Caveat:** NYCHA "
    "is public housing only — a small, non-representative slice of total NYC load. Any divergence between "
    "the two lines is contextual, not causal proof of data-center demand."
)

# ---------------------------------------------------------------------------
# Borough breakdown
# ---------------------------------------------------------------------------
st.subheader("Consumption by borough")
borough_monthly = query(
    "select * from main_marts.mart_borough_monthly where borough in ({}) order by revenue_month".format(
        ",".join(f"'{b}'" for b in BOROUGH_COLORS)
    )
).copy()
borough_monthly["revenue_month"] = pd.to_datetime(borough_monthly["revenue_month"])

fig = px.line(
    borough_monthly, x="revenue_month", y="consumption_kwh", color="borough",
    color_discrete_map=BOROUGH_COLORS, labels={"revenue_month": "", "consumption_kwh": "kWh", "borough": ""},
)
fig.update_traces(hovertemplate="%{fullData.name}, %{x|%b %Y}: %{y:,.0f} kWh<extra></extra>")
st.plotly_chart(style_fig(fig, x_gridlines=True, y_gridlines=True, show_legend=True), use_container_width=True)

# ---------------------------------------------------------------------------
# Model leaderboard
# ---------------------------------------------------------------------------
st.subheader("Regression model leaderboard")
st.caption("One-step-ahead monthly kWh prediction per development. Time-based holdout (last 12 months) — never a random shuffle.")

try:
    leaderboard = query("select * from analytics.model_leaderboard order by rmse")
except duckdb.CatalogException:
    leaderboard = None

if leaderboard is None or leaderboard.empty:
    st.info("No trained models yet — run the Dagster `model_leaderboard` asset (see README) to populate this table.")
else:
    display = leaderboard.copy()
    display["model_name"] = display.apply(
        lambda r: f"✅ {r['model_name']}" if r["is_best"] else r["model_name"], axis=1
    )
    display = display.rename(
        columns={
            "model_name": "Model", "rmse": "RMSE", "mae": "MAE", "mape": "MAPE (%)",
            "r2": "R²", "hit_rate_10pct": "Hit rate ±10% (%)",
        }
    )[["Model", "RMSE", "MAE", "MAPE (%)", "R²", "Hit rate ±10% (%)"]]
    st.dataframe(display.style.format(precision=2), use_container_width=True, hide_index=True)

    # ---------------------------------------------------------------------
    # Predicted vs. actual for the best model
    # ---------------------------------------------------------------------
    st.subheader("Predicted vs. actual (best model)")
    predictions = query("select * from analytics.model_predictions order by revenue_month")
    predictions["revenue_month"] = pd.to_datetime(predictions["revenue_month"])

    developments = sorted(predictions["development_name"].unique())
    selected = st.selectbox("Development", ["All (scatter)"] + developments)

    if selected == "All (scatter)":
        fig = px.scatter(
            predictions, x="actual_kwh", y="predicted_kwh",
            labels={"actual_kwh": "Actual kWh", "predicted_kwh": "Predicted kWh"}, opacity=0.5,
        )
        fig.update_traces(marker=dict(color=SERIES_1, size=6), hovertemplate="Actual: %{x:,.0f}<br>Predicted: %{y:,.0f}<extra></extra>")
        max_val = max(predictions["actual_kwh"].max(), predictions["predicted_kwh"].max())
        fig.add_trace(
            go.Scatter(x=[0, max_val], y=[0, max_val], mode="lines", line=dict(color=INK_MUTED, dash="dash", width=1), hoverinfo="skip")
        )
        st.plotly_chart(style_fig(fig, x_gridlines=True, y_gridlines=True), use_container_width=True)
    else:
        subset = predictions[predictions["development_name"] == selected]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=subset["revenue_month"], y=subset["actual_kwh"], name="Actual",
                       line=dict(color=CATEGORICAL["blue"], width=2), hovertemplate="Actual: %{y:,.0f}<extra></extra>")
        )
        fig.add_trace(
            go.Scatter(x=subset["revenue_month"], y=subset["predicted_kwh"], name="Predicted",
                       line=dict(color=CATEGORICAL["aqua"], width=2, dash="dot"), hovertemplate="Predicted: %{y:,.0f}<extra></extra>")
        )
        st.plotly_chart(style_fig(fig, x_gridlines=True, y_gridlines=True, show_legend=True), use_container_width=True)
