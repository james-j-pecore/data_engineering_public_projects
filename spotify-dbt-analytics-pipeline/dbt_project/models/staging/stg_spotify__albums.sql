with source as (
    select * from {{ source('raw', 'albums') }}
)

select
    data ->> 'id' as album_id,
    data ->> 'name' as album_name,
    data ->> 'album_type' as album_type,
    data ->> 'release_date' as release_date_raw,
    data ->> 'release_date_precision' as release_date_precision,
    cast(data ->> 'total_tracks' as integer) as total_tracks,
    data -> 'artists' -> 0 ->> 'id' as primary_artist_id,
    loaded_at
from source
