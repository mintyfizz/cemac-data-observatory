with obs as (
    select * from {{ ref('fct_observations') }}
),

cemac_avg as (
    select
        indicator_code,
        year,
        avg(value) as cemac_avg_value,
        count(*) as cemac_country_count
    from obs
    where country_group = 'CEMAC'
    group by indicator_code, year
),

benchmark_avg as (
    select
        indicator_code,
        year,
        avg(value) as benchmark_avg_value,
        count(*) as benchmark_country_count
    from obs
    where country_group = 'Benchmark'
    group by indicator_code, year
)

select
    coalesce(c.indicator_code, b.indicator_code) as indicator_code,
    coalesce(c.year, b.year) as year,
    c.cemac_avg_value,
    c.cemac_country_count,
    b.benchmark_avg_value,
    b.benchmark_country_count,
    b.benchmark_avg_value - c.cemac_avg_value as gap_benchmark_minus_cemac
from cemac_avg c
full outer join benchmark_avg b
    on c.indicator_code = b.indicator_code
   and c.year = b.year
