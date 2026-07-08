-- One row per release year across the whole (deduplicated) track library.

with tracks as (
    select * from {{ ref('stg_spotify__tracks') }}
),

albums as (
    select * from {{ ref('stg_spotify__albums') }}
),

track_years as (
    select
        t.track_id,
        try_cast(split_part(a.release_date_raw, '-', 1) as integer) as release_year
    from tracks t
    left join albums a on t.album_id = a.album_id
)

select
    release_year,
    count(*) as track_count,
    round(count(*) * 1.0 / sum(count(*)) over (), 4) as pct_of_library
from track_years
where release_year is not null
group by 1
order by release_year
