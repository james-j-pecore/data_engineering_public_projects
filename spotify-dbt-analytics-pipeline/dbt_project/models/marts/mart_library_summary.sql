-- Single-row snapshot of the whole library: counts, hours, explicit share.

with tracks as (select * from {{ ref('stg_spotify__tracks') }}),
playlists as (select * from {{ ref('stg_spotify__playlists') }}),
playlist_tracks as (select * from {{ ref('stg_spotify__playlist_tracks') }}),
saved_tracks as (select * from {{ ref('stg_spotify__saved_tracks') }}),
artists as (select * from {{ ref('stg_spotify__artists') }}),
albums as (select * from {{ ref('stg_spotify__albums') }}),
recently_played as (select * from {{ ref('stg_spotify__recently_played') }}),

singleton_albums as (
    select album_id from tracks group by album_id having count(*) = 1
)

select
    (select count(*) from playlists) as playlist_count,
    (select count(*) from tracks) as unique_track_count,
    (select count(*) from artists) as unique_artist_count,
    (select count(*) from albums) as unique_album_count,
    (select count(*) from saved_tracks) as saved_track_count,
    (select count(*) from recently_played) as recently_played_count,
    (select count(*) from playlist_tracks) as total_playlist_track_rows,
    (select round(sum(duration_ms) / 1000.0 / 60 / 60, 1) from tracks) as total_library_hours,
    (select round(avg(case when is_explicit then 1.0 else 0.0 end), 3) from tracks) as explicit_track_share,
    (select count(*) from singleton_albums) as singleton_album_count
