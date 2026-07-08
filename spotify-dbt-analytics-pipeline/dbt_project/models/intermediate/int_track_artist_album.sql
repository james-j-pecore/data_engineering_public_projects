-- One row per (track, artist): explodes each track's artist list and enriches
-- with album + artist metadata. Feeds the artist-concentration and release-year marts.

with tracks as (
    select * from {{ ref('stg_spotify__tracks') }}
),

track_artists as (
    select
        track_id,
        unnest(cast(artists_json as struct(id varchar, name varchar)[])) as artist
    from tracks
),

albums as (
    select * from {{ ref('stg_spotify__albums') }}
),

artists as (
    select * from {{ ref('stg_spotify__artists') }}
)

select
    t.track_id,
    t.track_name,
    t.duration_ms,
    t.is_explicit,
    t.popularity as track_popularity,
    t.album_id,
    alb.album_name,
    alb.album_type,
    alb.release_date_raw,
    try_cast(split_part(alb.release_date_raw, '-', 1) as integer) as release_year,
    ta.artist.id as artist_id,
    ta.artist.name as artist_name,
    ta.artist.id = t.primary_artist_id as is_primary_artist,
    art.popularity as artist_popularity,
    art.follower_count as artist_follower_count,
    art.primary_genre as artist_primary_genre
from tracks t
join track_artists ta on t.track_id = ta.track_id
left join albums alb on t.album_id = alb.album_id
left join artists art on ta.artist.id = art.artist_id
