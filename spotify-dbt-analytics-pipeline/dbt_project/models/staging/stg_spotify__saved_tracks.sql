with source as (
    select * from {{ source('raw', 'saved_tracks') }}
)

select
    id as saved_track_id,
    data -> 'track' ->> 'id' as track_id,
    cast(data ->> 'added_at' as timestamp) as added_at,
    loaded_at
from source
