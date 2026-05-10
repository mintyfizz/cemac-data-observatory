select
    country_code,
    country_name,
    country_group,
    is_cemac,
    is_benchmark,
    region,
    capital
from {{ ref('stg_countries') }}
