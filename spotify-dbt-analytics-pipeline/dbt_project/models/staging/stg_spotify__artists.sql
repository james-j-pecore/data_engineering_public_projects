with source as (
    select * from {{ source('raw', 'artists') }}
)

select
    data ->> 'id' as artist_id,
    data ->> 'name' as artist_name,
    cast(data ->> 'popularity' as integer) as popularity,
    cast(data -> 'followers' ->> 'total' as bigint) as follower_count,
    data -> 'genres' ->> 0 as primary_genre,
    data -> 'genres' as genres_json,
    loaded_at
from source
