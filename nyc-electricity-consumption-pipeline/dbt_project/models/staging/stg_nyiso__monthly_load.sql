with source as (
    select * from {{ source('raw', 'nyiso_monthly_load') }}
)

select
    cast((data ->> 'year_month') || '-01' as date) as revenue_month,
    try_cast(data ->> 'avg_load_mw' as double) as avg_load_mw,
    try_cast(data ->> 'max_load_mw' as double) as max_load_mw,
    loaded_at
from source
