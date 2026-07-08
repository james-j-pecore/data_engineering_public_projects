# Spotify Analytics Pipeline

Spotify Web API → DuckDB → dbt → Dagster → Streamlit.

Pulls your playlists, tracks, artists, albums, and saved tracks from the Spotify API, models them
with dbt into analytics marts, orchestrates the whole thing with Dagster, and surfaces the results
in a Streamlit app.

> Full setup instructions, architecture diagram, and example output are being filled in as the
> project is built — see the build order in progress.
