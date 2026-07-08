"""Pulls raw entities from the Spotify API as plain lists of dicts.

Track and album metadata come embedded in the playlist/saved-tracks/recently-played
responses (Spotify returns full track objects there, not simplified ones), so no extra
calls are needed for those. Artists are only embedded as simplified refs (no genres,
popularity, follower count), so those are batch-fetched separately via GET /artists.
"""

from src.spotify_client import SpotifyClient

BATCH_SIZE = 50  # Spotify's max ids per batch endpoint (e.g. GET /artists)


def _chunks(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def extract_profile(client: SpotifyClient) -> dict:
    return client.get("/me")


def extract_playlists(client: SpotifyClient) -> list[dict]:
    return client.get_paginated("/me/playlists")


def extract_playlist_tracks(client: SpotifyClient, playlist_ids: list[str]) -> list[dict]:
    """Returns one row per (playlist, track), tagged with the owning playlist_id."""
    rows = []
    for playlist_id in playlist_ids:
        items = client.get_paginated(f"/playlists/{playlist_id}/tracks")
        for item in items:
            if item.get("track") is None or item.get("is_local"):
                continue  # removed, region-locked, or local-only tracks have no usable data
            rows.append({**item, "playlist_id": playlist_id})
    return rows


def extract_saved_tracks(client: SpotifyClient) -> list[dict]:
    items = client.get_paginated("/me/tracks")
    return [item for item in items if item.get("track") is not None]


def extract_recently_played(client: SpotifyClient) -> list[dict]:
    items = client.get_paginated("/me/player/recently-played")
    return [item for item in items if item.get("track") is not None]


def extract_tracks(*track_sources: list[dict]) -> list[dict]:
    """Dedupes full track objects embedded across playlist/saved/recently-played rows."""
    tracks_by_id = {}
    for rows in track_sources:
        for row in rows:
            track = row["track"]
            tracks_by_id[track["id"]] = track
    return list(tracks_by_id.values())


def extract_albums(tracks: list[dict]) -> list[dict]:
    """Dedupes album objects embedded in track responses."""
    albums_by_id = {}
    for track in tracks:
        album = track["album"]
        albums_by_id[album["id"]] = album
    return list(albums_by_id.values())


def extract_artists(client: SpotifyClient, tracks: list[dict]) -> list[dict]:
    """Batch-fetches full artist objects (genres, popularity) for every artist on every track."""
    artist_ids = {artist["id"] for track in tracks for artist in track["artists"]}
    artists = []
    for chunk in _chunks(sorted(artist_ids), BATCH_SIZE):
        response = client.get("/artists", {"ids": ",".join(chunk)})
        artists.extend(response["artists"])
    return artists


def extract_all(client: SpotifyClient) -> dict[str, list[dict] | dict]:
    profile = extract_profile(client)
    playlists = extract_playlists(client)
    playlist_tracks = extract_playlist_tracks(client, [p["id"] for p in playlists])
    saved_tracks = extract_saved_tracks(client)
    recently_played = extract_recently_played(client)

    tracks = extract_tracks(playlist_tracks, saved_tracks, recently_played)
    albums = extract_albums(tracks)
    artists = extract_artists(client, tracks)

    return {
        "profile": profile,
        "playlists": playlists,
        "playlist_tracks": playlist_tracks,
        "saved_tracks": saved_tracks,
        "recently_played": recently_played,
        "tracks": tracks,
        "albums": albums,
        "artists": artists,
    }
