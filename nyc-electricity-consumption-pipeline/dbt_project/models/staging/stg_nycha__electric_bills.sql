with source as (
    select * from {{ source('raw', 'nycha_electric_bills') }}
)

select
    id as bill_id,
    nullif(data ->> 'development_name', '') as development_name,
    nullif(data ->> 'borough', '') as borough,
    nullif(data ->> 'account_name', '') as account_name,
    nullif(data ->> 'location', '') as location,
    nullif(data ->> 'meter_amr', '') as meter_amr,
    nullif(data ->> 'meter_scope', '') as meter_scope,
    try_cast(data ->> 'tds' as integer) as tds,
    try_cast(data ->> 'edp' as integer) as edp,
    nullif(data ->> 'rc_code', '') as rc_code,
    nullif(data ->> 'funding_source', '') as funding_source,
    nullif(data ->> 'amp', '') as amp,
    nullif(data ->> 'vendor_name', '') as vendor_name,
    try_cast(data ->> 'umis_bill_id' as bigint) as umis_bill_id,
    cast((data ->> 'revenue_month') || '-01' as date) as revenue_month,
    try_cast(data ->> 'service_start_date' as timestamp)::date as service_start_date,
    try_cast(data ->> 'service_end_date' as timestamp)::date as service_end_date,
    try_cast(data ->> 'days' as integer) as billing_days,
    nullif(data ->> 'meter_number', '') as meter_number,
    (data ->> 'estimated') = 'Y' as is_estimated,
    try_cast(data ->> 'current_charges' as double) as current_charges,
    nullif(data ->> 'rate_class', '') as rate_class,
    (data ->> 'bill_analyzed') = 'Yes' as is_bill_analyzed,
    try_cast(data ->> 'consumption_kwh' as double) as consumption_kwh,
    try_cast(data ->> 'kwh_charges' as double) as kwh_charges,
    try_cast(data ->> 'consumption_kw' as double) as consumption_kw,
    try_cast(data ->> 'kw_charges' as double) as kw_charges,
    try_cast(data ->> 'other_charges' as double) as other_charges,
    loaded_at
from source
