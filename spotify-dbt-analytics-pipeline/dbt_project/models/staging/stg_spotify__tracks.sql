with source as (
    select * from {{ source('raw', 'tracks') }}
)

select
    data ->> 'id' as track_id,
    data ->> 'name' as track_name,
    data -> 'album' ->> 'id' as album_id,
    cast(data ->> 'duration_ms' as bigint) as duration_ms,
    cast(data ->> 'explicit' as boolean) as is_explicit,
    cast(data ->> 'popularity' as integer) as popularity,
    cast(data ->> 'track_number' as integer) as track_number,
    data -> 'artists' -> 0 ->> 'id' as primary_artist_id,
    data -> 'artists' as artists_json,
    loaded_at
from source
