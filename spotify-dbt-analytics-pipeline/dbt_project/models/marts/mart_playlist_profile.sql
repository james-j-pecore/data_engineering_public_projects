-- One row per playlist: size, artist diversity, popularity/era profile, and dominant artist.

with pte as (
    select * from {{ ref('int_playlist_tracks_enriched') }}
),

playlists as (
    select * from {{ ref('stg_spotify__playlists') }}
),

playlist_artist_counts as (
    select playlist_id, artist_id, artist_name, count(*) as artist_track_count
    from pte
    group by 1, 2, 3
),

top_artist as (
    select playlist_id, artist_name, artist_track_count
    from (
        select
            playlist_id,
            artist_name,
            artist_track_count,
            row_number() over (partition by playlist_id order by artist_track_count desc) as rn
        from playlist_artist_counts
    )
    where rn = 1
),

playlist_stats as (
    select
        playlist_id,
        count(*) as track_count,
        count(distinct artist_id) as unique_artist_count,
        round(avg(track_popularity), 1) as avg_track_popularity,
        round(avg(release_year), 0) as avg_release_year,
        round(avg(case when is_explicit then 1.0 else 0.0 end), 3) as explicit_share
    from pte
    group by 1
)

select
    p.playlist_id,
    p.playlist_name,
    p.is_public,
    ps.track_count,
    ps.unique_artist_count,
    round(ps.unique_artist_count * 1.0 / nullif(ps.track_count, 0), 4) as artist_diversity_ratio,
    ps.avg_track_popularity,
    ps.avg_release_year,
    ps.explicit_share,
    ta.artist_name as top_artist_name,
    ta.artist_track_count as top_artist_track_count,
    round(ta.artist_track_count * 1.0 / nullif(ps.track_count, 0), 4) as top_artist_share
from playlists p
join playlist_stats ps on p.playlist_id = ps.playlist_id
left join top_artist ta on p.playlist_id = ta.playlist_id
order by ps.track_count desc
