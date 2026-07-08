"""Generates a realistic fake Spotify library and loads it via src.load.load_all().

This exists so the dbt/Dagster/Streamlit layers can be built and demoed without a live
Spotify API connection (e.g. no Premium account available yet on the app-owner's
account). The generated dicts match the exact shapes src/extract.py produces, so
load.py, dbt, and everything downstream treat this identically to real extracted data.
Swap it out later by simply running `python -m src.load` for real once API access works.
"""

import random
from datetime import datetime, timedelta, timezone

from src.load import load_all

random.seed(42)

GENRE_POOL = [
    "indie rock", "dream pop", "synthpop", "alternative rock", "lo-fi",
    "bedroom pop", "post-punk", "electronic", "folk", "jazz fusion",
    "hip hop", "neo soul", "ambient", "shoegaze", "indie folk",
]

ARTIST_NAMES = [
    "Nightshade Radio", "Velvet Static", "Coastal Drift", "The Paper Moons",
    "Amber & Iron", "Glass Horizon", "Kindred Echo", "The Low Signals",
    "Marigold Season", "Static Lullaby", "Painted Wolves", "Blue Hour Society",
    "The Quiet Parade", "Hollow Coast", "Fever Dream Radio", "Little Machines",
    "The Sunday Static", "Wildflower Radio",
]

ADJECTIVES = ["Faded", "Golden", "Slow", "Quiet", "Neon", "Hollow", "Midnight", "Paper", "Velvet", "Static"]
NOUNS = ["Horizon", "Static", "Bloom", "Echo", "Drift", "Season", "Signal", "Parade", "Coast", "Lullaby"]


def _track_name() -> str:
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"


def _random_datetime(days_back: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, days_back), seconds=random.randint(0, 86400)
    )
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _image() -> list[dict]:
    return [{"url": "https://i.scdn.co/image/ab67616d0000b273placeholder", "height": 640, "width": 640}]


def build_profile() -> dict:
    return {
        "id": "sample_user_1",
        "display_name": "Sample User",
        "country": "US",
        "product": "premium",
        "followers": {"total": 12},
        "images": _image(),
    }


def build_artists(n: int) -> list[dict]:
    artists = []
    for i, name in enumerate(ARTIST_NAMES[:n]):
        artists.append(
            {
                "id": f"artist_{i}",
                "name": name,
                "genres": random.sample(GENRE_POOL, k=random.randint(1, 3)),
                "popularity": random.randint(15, 85),
                "followers": {"total": random.randint(500, 500_000)},
                "images": _image(),
            }
        )
    return artists


def build_albums(artists: list[dict], n: int) -> list[dict]:
    albums = []
    for i in range(n):
        artist = random.choice(artists)
        year = random.randint(1978, 2025)
        albums.append(
            {
                "id": f"album_{i}",
                "name": f"{_track_name()} {'EP' if random.random() < 0.25 else ''}".strip(),
                "album_type": "single" if random.random() < 0.2 else "album",
                "release_date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "release_date_precision": "day",
                "total_tracks": random.randint(1, 14),
                "images": _image(),
                "artists": [{"id": artist["id"], "name": artist["name"]}],
            }
        )
    return albums


def build_tracks(albums: list[dict], artists_by_id: dict, n: int) -> list[dict]:
    tracks = []
    for i in range(n):
        album = random.choice(albums)
        primary_artist_id = album["artists"][0]["id"]
        track_artists = [{"id": primary_artist_id, "name": artists_by_id[primary_artist_id]["name"]}]
        if random.random() < 0.15:  # occasional featured artist
            feat = random.choice([a for a in artists_by_id if a != primary_artist_id])
            track_artists.append({"id": feat, "name": artists_by_id[feat]["name"]})

        tracks.append(
            {
                "id": f"track_{i}",
                "name": _track_name(),
                "duration_ms": random.randint(120_000, 320_000),
                "explicit": random.random() < 0.2,
                "popularity": random.randint(5, 90),
                "disc_number": 1,
                "track_number": random.randint(1, album["total_tracks"]),
                "external_urls": {"spotify": f"https://open.spotify.com/track/track_{i}"},
                "album": album,
                "artists": track_artists,
            }
        )
    return tracks


def build_playlists(n: int, owner_id: str) -> list[dict]:
    names = [
        "Late Night Drive", "Sunday Coffee", "Focus Flow", "Summer 2024",
        "Rainy Day", "Workout Mix", "Road Trip", "Chill Study Beats",
    ]
    playlists = []
    for i in range(n):
        playlists.append(
            {
                "id": f"playlist_{i}",
                "name": names[i % len(names)],
                "description": "",
                "public": random.random() < 0.5,
                "collaborative": False,
                "owner": {"id": owner_id, "display_name": "Sample User"},
                "tracks": {"total": 0},  # not relied on downstream; real total is len(playlist_tracks)
                "images": _image(),
            }
        )
    return playlists


def build_playlist_tracks(playlists: list[dict], tracks: list[dict], owner_id: str) -> list[dict]:
    rows = []
    for playlist in playlists:
        # random playlist size, with overlap across playlists since tracks are drawn from
        # the same shared pool — this is what makes playlist-similarity analysis meaningful
        playlist_tracks = random.sample(tracks, k=random.randint(15, 40))
        for track in playlist_tracks:
            rows.append(
                {
                    "added_at": _random_datetime(400),
                    "added_by": {"id": owner_id},
                    "is_local": False,
                    "track": track,
                    "playlist_id": playlist["id"],
                }
            )
    return rows


def build_saved_tracks(tracks: list[dict], n: int) -> list[dict]:
    return [{"added_at": _random_datetime(600), "track": t} for t in random.sample(tracks, k=n)]


def build_recently_played(tracks: list[dict], n: int) -> list[dict]:
    return [
        {"played_at": _random_datetime(14), "context": None, "track": random.choice(tracks)}
        for _ in range(n)
    ]


def main() -> None:
    profile = build_profile()
    artists = build_artists(18)
    artists_by_id = {a["id"]: a for a in artists}
    albums = build_albums(artists, 55)
    tracks = build_tracks(albums, artists_by_id, 140)
    playlists = build_playlists(8, profile["id"])
    playlist_tracks = build_playlist_tracks(playlists, tracks, profile["id"])
    saved_tracks = build_saved_tracks(tracks, 60)
    recently_played = build_recently_played(tracks, 30)

    data = {
        "profile": profile,
        "playlists": playlists,
        "playlist_tracks": playlist_tracks,
        "saved_tracks": saved_tracks,
        "recently_played": recently_played,
        "tracks": tracks,
        "albums": albums,
        "artists": artists,
    }
    load_all(data)
    print("Sample data loaded into DuckDB raw schema.")


if __name__ == "__main__":
    main()
