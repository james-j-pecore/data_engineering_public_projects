with source as (
    select * from {{ source('raw', 'playlist_tracks') }}
)

select
    id as playlist_track_id,
    data ->> 'playlist_id' as playlist_id,
    data -> 'track' ->> 'id' as track_id,
    cast(data ->> 'added_at' as timestamp) as added_at,
    data -> 'added_by' ->> 'id' as added_by_id,
    loaded_at
from source
