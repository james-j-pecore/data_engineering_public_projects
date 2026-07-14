-- Compares NYCHA-wide monthly consumption against NYISO's "N.Y.C." zone grid
-- load, both indexed to their first available month = 100. NYCHA is a small,
-- non-representative slice of total NYC load (public housing only), so read
-- any divergence between the two series as contextual, not causal, evidence
-- of broader demand shifts (e.g. data-center buildout) — not proof of it.

with nycha as (
    select revenue_month, consumption_kwh as nycha_kwh
    from {{ ref('int_citywide_monthly') }}
),

grid as (
    select revenue_month, avg_load_mw as grid_avg_load_mw
    from {{ ref('stg_nyiso__monthly_load') }}
),

joined as (
    select
        coalesce(nycha.revenue_month, grid.revenue_month) as revenue_month,
        nycha.nycha_kwh,
        grid.grid_avg_load_mw
    from nycha
    full outer join grid using (revenue_month)
),

baselines as (
    select
        (select nycha_kwh from joined where nycha_kwh is not null order by revenue_month limit 1) as nycha_base,
        (select grid_avg_load_mw from joined where grid_avg_load_mw is not null order by revenue_month limit 1) as grid_base
)

select
    joined.revenue_month,
    joined.nycha_kwh,
    joined.grid_avg_load_mw,
    round(joined.nycha_kwh / baselines.nycha_base * 100, 2) as nycha_index,
    round(joined.grid_avg_load_mw / baselines.grid_base * 100, 2) as grid_index,
    round(
        (joined.nycha_kwh / nullif(lag(joined.nycha_kwh, 12) over (order by joined.revenue_month), 0) - 1) * 100,
        2
    ) as nycha_yoy_pct,
    round(
        (joined.grid_avg_load_mw / nullif(lag(joined.grid_avg_load_mw, 12) over (order by joined.revenue_month), 0) - 1) * 100,
        2
    ) as grid_yoy_pct
from joined
cross join baselines
order by joined.revenue_month
