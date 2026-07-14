with borough_monthly as (
    select * from {{ ref('int_borough_monthly') }}
)

select
    revenue_month,
    sum(consumption_kwh) as consumption_kwh,
    sum(consumption_kw) as consumption_kw,
    sum(current_charges) as current_charges,
    sum(kwh_charges) as kwh_charges,
    sum(kw_charges) as kw_charges,
    sum(other_charges) as other_charges,
    sum(development_count) as development_count
from borough_monthly
group by 1
