-- One row per playlist pair with shared tracks, plus Jaccard similarity.

with pt as (
    select distinct playlist_id, track_id
    from {{ ref('int_playlist_tracks_enriched') }}
),

playlists as (
    select playlist_id, playlist_name from {{ ref('stg_spotify__playlists') }}
),

playlist_sizes as (
    select playlist_id, count(*) as track_count from pt group by 1
),

pairs as (
    select
        a.playlist_id as playlist_id_a,
        b.playlist_id as playlist_id_b,
        count(*) as shared_track_count
    from pt a
    join pt b
        on a.track_id = b.track_id
        and a.playlist_id < b.playlist_id
    group by 1, 2
)

select
    p.playlist_id_a,
    pa.playlist_name as playlist_name_a,
    p.playlist_id_b,
    pb.playlist_name as playlist_name_b,
    p.shared_track_count,
    sa.track_count as track_count_a,
    sb.track_count as track_count_b,
    round(
        p.shared_track_count * 1.0 / (sa.track_count + sb.track_count - p.shared_track_count),
        4
    ) as jaccard_similarity
from pairs p
join playlists pa on p.playlist_id_a = pa.playlist_id
join playlists pb on p.playlist_id_b = pb.playlist_id
join playlist_sizes sa on p.playlist_id_a = sa.playlist_id
join playlist_sizes sb on p.playlist_id_b = sb.playlist_id
order by jaccard_similarity desc
