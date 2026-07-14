-- Development x month panel with lag/rolling features for one-step-ahead kWh
-- prediction (see src/models/). Trigonometric month encoding happens in
-- src/models/features.py, not here — this mart just exposes month_of_year.

with development_monthly as (
    select * from {{ ref('int_development_monthly') }}
)

select
    *,
    extract(month from revenue_month) as month_of_year,
    extract(year from revenue_month) as year,
    lag(consumption_kwh, 1) over w as lag_1_kwh,
    lag(consumption_kwh, 12) over w as lag_12_kwh,
    avg(consumption_kwh) over (
        partition by development_name order by revenue_month
        rows between 3 preceding and 1 preceding
    ) as rolling_mean_3_kwh
from development_monthly
window w as (partition by development_name order by revenue_month)
order by development_name, revenue_month
