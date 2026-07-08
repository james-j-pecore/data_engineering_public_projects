-- One row per (playlist, track), joined to playlist metadata and the track's
-- primary artist/album info. Filters to is_primary_artist so the join stays 1:1
-- (a track with 2 artists would otherwise fan out playlist-track rows).

with playlist_tracks as (
    select * from {{ ref('stg_spotify__playlist_tracks') }}
),

playlists as (
    select * from {{ ref('stg_spotify__playlists') }}
),

primary_track_info as (
    select * from {{ ref('int_track_artist_album') }}
    where is_primary_artist
)

select
    pt.playlist_track_id,
    pt.playlist_id,
    pl.playlist_name,
    pt.track_id,
    pt.added_at,
    ti.track_name,
    ti.duration_ms,
    ti.is_explicit,
    ti.track_popularity,
    ti.album_id,
    ti.album_name,
    ti.release_year,
    ti.artist_id,
    ti.artist_name,
    ti.artist_primary_genre
from playlist_tracks pt
join playlists pl on pt.playlist_id = pl.playlist_id
left join primary_track_info ti on pt.track_id = ti.track_id
