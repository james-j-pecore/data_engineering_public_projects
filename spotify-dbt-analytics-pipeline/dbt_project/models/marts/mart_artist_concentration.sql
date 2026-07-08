-- One row per artist: how much of the library and how many playlists they show up in.

with track_artist as (
    select * from {{ ref('int_track_artist_album') }}
    where is_primary_artist
),

playlist_tracks as (
    select * from {{ ref('int_playlist_tracks_enriched') }}
),

artist_track_counts as (
    select artist_id, artist_name, count(distinct track_id) as track_count
    from track_artist
    group by 1, 2
),

artist_playlist_counts as (
    select artist_id, count(distinct playlist_id) as playlist_count
    from playlist_tracks
    group by 1
),

artist_meta as (
    select artist_id, popularity as artist_popularity, follower_count, primary_genre
    from {{ ref('stg_spotify__artists') }}
)

select
    atc.artist_id,
    atc.artist_name,
    atc.track_count,
    coalesce(apc.playlist_count, 0) as playlist_count,
    am.artist_popularity,
    am.follower_count,
    am.primary_genre,
    round(atc.track_count * 1.0 / sum(atc.track_count) over (), 4) as pct_of_library_tracks
from artist_track_counts atc
left join artist_playlist_counts apc on atc.artist_id = apc.artist_id
left join artist_meta am on atc.artist_id = am.artist_id
order by atc.track_count desc
