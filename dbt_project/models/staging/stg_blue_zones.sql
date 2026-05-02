with source as (
    select
        zone_name,
        country,
        region,
        avg_life_expectancy,
        diet_description,
        key_foods,
        plant_based_pct,
        physical_activity,
        social_factors
    from {{ source('raw', 'blue_zones') }}
)

select
    zone_name,
    country,
    region,
    avg_life_expectancy,
    diet_description,
    key_foods,
    plant_based_pct,
    physical_activity,
    social_factors
from source
