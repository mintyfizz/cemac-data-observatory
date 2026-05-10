with obs as (
    select * from {{ ref('stg_observations') }}
)

select
    max(loaded_at)                 as last_refresh_at,
    now() - max(loaded_at)         as time_since_refresh,
    count(*)                       as total_observations,
    count(distinct country_code)   as countries_present,
    count(distinct indicator_code) as indicators_present,
    min(year)                      as earliest_year,
    max(year)                      as latest_year
from obs
