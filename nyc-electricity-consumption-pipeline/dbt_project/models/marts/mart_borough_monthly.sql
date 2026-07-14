with borough_monthly as (
    select * from {{ ref('int_borough_monthly') }}
)

select
    *,
    lag(consumption_kwh, 12) over (partition by borough order by revenue_month) as consumption_kwh_prior_year,
    round(
        (consumption_kwh / nullif(lag(consumption_kwh, 12) over (partition by borough order by revenue_month), 0) - 1) * 100,
        2
    ) as consumption_yoy_pct
from borough_monthly
order by borough, revenue_month
