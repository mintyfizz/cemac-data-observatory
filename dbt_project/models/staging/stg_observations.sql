with source as (
    select * from {{ source('raw', 'observations') }}
),

cleaned as (
    select
        country_code,
        indicator_code,
        year,
        value::numeric as value,
        unit,
        obs_status,
        decimal_places,
        loaded_at
    from source
    where value is not null
)

select * from cleaned
