-- Rolls meter/location-level bills up to one row per (development, month).

with bills as (
    select * from {{ ref('stg_nycha__electric_bills') }}
    where development_name is not null
)

select
    development_name,
    borough,
    revenue_month,
    sum(consumption_kwh) as consumption_kwh,
    sum(consumption_kw) as consumption_kw,
    sum(current_charges) as current_charges,
    sum(kwh_charges) as kwh_charges,
    sum(kw_charges) as kw_charges,
    sum(other_charges) as other_charges,
    count(*) as bill_count,
    mode(rate_class) as dominant_rate_class,
    avg(billing_days) as avg_billing_days
from bills
group by 1, 2, 3
