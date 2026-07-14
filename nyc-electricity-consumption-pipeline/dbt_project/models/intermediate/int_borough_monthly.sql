with development_monthly as (
    select * from {{ ref('int_development_monthly') }}
)

select
    borough,
    revenue_month,
    sum(consumption_kwh) as consumption_kwh,
    sum(consumption_kw) as consumption_kw,
    sum(current_charges) as current_charges,
    sum(kwh_charges) as kwh_charges,
    sum(kw_charges) as kw_charges,
    sum(other_charges) as other_charges,
    count(distinct development_name) as development_count
from development_monthly
group by 1, 2
