"""Reads dbt marts straight out of DuckDB (read-only) and renders the 8 example
analytics questions from the README. No dependency on src/config.py or Spotify
credentials — this only needs data/spotify.duckdb to already exist.

Chart styling follows a single-hue-per-series convention: each chart here shows
one measure across many entities, so every bar uses the same accent color rather
than a color-per-bar rainbow (which would encode identity where none exists).
"""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

DUCKDB_PATH = Path(__file__).resolve().parent.parent / "data" / "spotify.duckdb"

# Design tokens — see dataviz skill references/palette.md for the full system.
SERIES_1 = "#2a78d6"
SURFACE = "#fcfcfb"
GRIDLINE = "#e1e0d9"
AXIS_LINE = "#c3c2b7"
INK_PRIMARY = "#0b0b0b"
INK_MUTED = "#898781"
BLUE_SEQUENTIAL = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]

st.set_page_config(page_title="Spotify Library Analytics", page_icon="🎧", layout="wide")


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DUCKDB_PATH), read_only=True)


def query(sql: str) -> pd.DataFrame:
    return get_connection().execute(sql).fetchdf()


def style_fig(fig, x_gridlines: bool = False, y_gridlines: bool = False):
    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(color=INK_PRIMARY, family="system-ui, -apple-system, 'Segoe UI', sans-serif"),
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=x_gridlines, gridcolor=GRIDLINE, linecolor=AXIS_LINE, tickfont=dict(color=INK_MUTED))
    fig.update_yaxes(showgrid=y_gridlines, gridcolor=GRIDLINE, linecolor=AXIS_LINE, tickfont=dict(color=INK_MUTED))
    return fig


def ranked_bar(df: pd.DataFrame, value_col: str, label_col: str, value_label: str, hover_suffix: str):
    fig = px.bar(
        df.sort_values(value_col),
        x=value_col, y=label_col, orientation="h",
        labels={value_col: value_label, label_col: ""},
    )
    fig.update_traces(marker_color=SERIES_1, hovertemplate=f"%{{y}}: %{{x}}{hover_suffix}<extra></extra>")
    return style_fig(fig, x_gridlines=True)


if not DUCKDB_PATH.exists():
    st.error(f"No DuckDB file found at {DUCKDB_PATH}. Run the pipeline first (see README).")
    st.stop()

st.title("🎧 Spotify Library Analytics")
st.caption("Playlist composition, artist concentration, release-year trends, and playlist overlap.")

summary = query("select * from main_marts.mart_library_summary").iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Playlists", int(summary.playlist_count))
c2.metric("Unique tracks", int(summary.unique_track_count))
c3.metric("Unique artists", int(summary.unique_artist_count))
c4.metric("Library hours", f"{summary.total_library_hours:.1f}")

c5, c6, c7 = st.columns(3)
c5.metric("Explicit tracks", f"{summary.explicit_track_share:.0%}")
c6.metric("Saved tracks", int(summary.saved_track_count))
c7.metric("Singleton albums", int(summary.singleton_album_count))

st.divider()

# 1. Which artists appear most frequently across playlists?
st.subheader("Most frequent artists across playlists")
top_artists = query("""
    select artist_name, playlist_count, track_count
    from main_marts.mart_artist_concentration
    order by playlist_count desc, track_count desc
    limit 15
""")
st.plotly_chart(
    ranked_bar(top_artists, "playlist_count", "artist_name", "Playlists appeared in", " playlists"),
    width="stretch",
)
with st.expander("View data"):
    st.dataframe(top_artists, width="stretch", hide_index=True)

# 2. Which playlists overlap the most?
st.subheader("Playlist overlap")
sim = query("select playlist_name_a, playlist_name_b, jaccard_similarity from main_marts.mart_playlist_similarity")
playlist_names = query("select playlist_name from main_marts.mart_playlist_profile order by playlist_name")["playlist_name"].tolist()
matrix = pd.DataFrame(0.0, index=playlist_names, columns=playlist_names)
for _, row in sim.iterrows():
    matrix.loc[row.playlist_name_a, row.playlist_name_b] = row.jaccard_similarity
    matrix.loc[row.playlist_name_b, row.playlist_name_a] = row.jaccard_similarity
for name in playlist_names:
    matrix.loc[name, name] = float("nan")  # self-similarity isn't meaningful

fig = px.imshow(matrix, color_continuous_scale=BLUE_SEQUENTIAL, labels=dict(color="Jaccard similarity"))
fig.update_traces(hovertemplate="%{y} vs %{x}: %{z:.0%}<extra></extra>")
fig.update_layout(showlegend=False)
st.plotly_chart(style_fig(fig), width="stretch")
with st.expander("View data"):
    st.dataframe(sim.sort_values("jaccard_similarity", ascending=False), width="stretch", hide_index=True)

# 3. Release-year distribution of the library
st.subheader("Release-year distribution")
years = query("select release_year, track_count from main_marts.mart_release_year_trends order by release_year")
fig = px.bar(years, x="release_year", y="track_count", labels={"release_year": "Release year", "track_count": "Tracks"})
fig.update_traces(marker_color=SERIES_1, hovertemplate="%{x}: %{y} tracks<extra></extra>")
st.plotly_chart(style_fig(fig, y_gridlines=True), width="stretch")

# 4. Which playlists are most diverse by artist?
st.subheader("Playlist artist diversity")
diversity = query("""
    select playlist_name, artist_diversity_ratio
    from main_marts.mart_playlist_profile
    order by artist_diversity_ratio desc
""")
fig = ranked_bar(diversity, "artist_diversity_ratio", "playlist_name", "Unique artists / track", " unique-artist ratio")
fig.update_xaxes(tickformat=".0%")
fig.update_traces(hovertemplate="%{y}: %{x:.0%} unique artists<extra></extra>")
st.plotly_chart(fig, width="stretch")

# 5. Which albums are represented by only one song?
st.subheader("Singleton albums")
singleton_albums = query("""
    with singleton_album_ids as (
        select album_id
        from main_staging.stg_spotify__tracks
        group by album_id
        having count(*) = 1
    )
    select alb.album_name, art.artist_name, alb.release_date_raw
    from singleton_album_ids s
    join main_staging.stg_spotify__albums alb on s.album_id = alb.album_id
    left join main_staging.stg_spotify__artists art on alb.primary_artist_id = art.artist_id
    order by alb.release_date_raw desc
""")
st.write(f"**{len(singleton_albums)}** albums are represented by exactly one track in your library.")
st.dataframe(singleton_albums, width="stretch", hide_index=True)

# 6. What share of tracks are explicit?
st.subheader("Explicit content share")
explicit_by_playlist = query("""
    select playlist_name, explicit_share
    from main_marts.mart_playlist_profile
    order by explicit_share desc
""")
fig = ranked_bar(explicit_by_playlist, "explicit_share", "playlist_name", "Explicit share", "% explicit")
fig.update_xaxes(tickformat=".0%")
fig.update_traces(hovertemplate="%{y}: %{x:.0%} explicit<extra></extra>")
st.plotly_chart(fig, width="stretch")

# 7. What are the largest playlists?
st.subheader("Largest playlists")
largest = query("select playlist_name, track_count from main_marts.mart_playlist_profile order by track_count desc")
st.plotly_chart(ranked_bar(largest, "track_count", "playlist_name", "Tracks", " tracks"), width="stretch")

# 8. Which artists dominate specific playlists?
st.subheader("Dominant artist per playlist")
dominance = query("""
    select playlist_name, top_artist_name, top_artist_share
    from main_marts.mart_playlist_profile
    order by top_artist_share desc
""")
fig = px.bar(
    dominance.sort_values("top_artist_share"),
    x="top_artist_share", y="playlist_name", orientation="h", text="top_artist_name",
    labels={"top_artist_share": "Share of playlist", "playlist_name": ""},
)
fig.update_traces(
    marker_color=SERIES_1, textposition="outside",
    hovertemplate="%{y}: %{text} — %{x:.0%} of tracks<extra></extra>",
)
fig.update_xaxes(tickformat=".0%")
st.plotly_chart(style_fig(fig, x_gridlines=True), width="stretch")
