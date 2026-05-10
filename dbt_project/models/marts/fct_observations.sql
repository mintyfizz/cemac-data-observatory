with obs as (
    select * from {{ ref('stg_observations') }}
),

countries as (
    select * from {{ ref('dim_countries') }}
),

indicators as (
    select * from {{ ref('dim_indicators') }}
)

select
    obs.country_code,
    countries.country_name,
    countries.country_group,
    obs.indicator_code,
    indicators.indicator_name,
    indicators.category,
    obs.year,
    obs.value,
    indicators.unit,
    obs.loaded_at
from obs
inner join countries on obs.country_code = countries.country_code
inner join indicators on obs.indicator_code = indicators.indicator_code
