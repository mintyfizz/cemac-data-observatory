with obs as (
    select * from {{ ref('fct_observations') }}
),

groups as (
    select * from {{ ref('mart_group_averages_yearly') }}
),

obs_with_rank as (
    select
        *,
        row_number() over (
            partition by country_code, indicator_code
            order by year desc
        ) as recency_rank
    from obs
)

select
    o.country_code,
    o.country_name,
    o.country_group,
    o.indicator_code,
    o.indicator_name,
    o.category,
    o.year,
    o.value as country_value,
    o.unit,
    g.cemac_avg_value,
    g.benchmark_avg_value,
    g.gap_benchmark_minus_cemac,
    o.recency_rank,
    (o.recency_rank = 1) as is_latest_observation
from obs_with_rank o
left join groups g
    on o.indicator_code = g.indicator_code
   and o.year = g.year
