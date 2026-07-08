with source as (
    select * from {{ source('raw', 'playlists') }}
)

select
    data ->> 'id' as playlist_id,
    data ->> 'name' as playlist_name,
    nullif(data ->> 'description', '') as description,
    cast(data ->> 'public' as boolean) as is_public,
    cast(data ->> 'collaborative' as boolean) as is_collaborative,
    data -> 'owner' ->> 'id' as owner_id,
    data -> 'images' -> 0 ->> 'url' as image_url,
    loaded_at
from source
