select
    indicator_code,
    indicator_name,
    category,
    unit,
    is_higher_better
from {{ ref('indicator_metadata') }}
