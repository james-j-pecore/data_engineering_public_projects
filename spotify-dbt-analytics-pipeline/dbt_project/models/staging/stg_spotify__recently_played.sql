with source as (
    select * from {{ source('raw', 'recently_played') }}
)

select
    id as recently_played_id,
    data -> 'track' ->> 'id' as track_id,
    cast(data ->> 'played_at' as timestamp) as played_at,
    loaded_at
from source
