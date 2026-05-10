select
    country_code,
    country_name,
    is_cemac,
    is_benchmark,
    case
        when is_cemac then 'CEMAC'
        when is_benchmark then 'Benchmark'
        else 'Other'
    end as country_group,
    region,
    capital
from {{ ref('country_metadata') }}
