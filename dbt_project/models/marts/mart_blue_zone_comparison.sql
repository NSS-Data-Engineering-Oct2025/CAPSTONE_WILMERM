with blue_zones as (
    select
        zone_name,
        country,
        avg_life_expectancy,
        diet_description,
        key_foods,
        plant_based_pct
    from {{ ref('stg_blue_zones') }}
),

us_nutrition as (
    select
        food_category,
        nutrient_name,
        unit,
        food_count,
        avg_amount
    from {{ ref('int_nutrition_summary') }}
    where nutrient_name in (
        'Total lipid (fat)',
        'Fiber, total dietary',
        'Protein',
        'Sugars, Total',
        'Energy'
    )
)

select
    bz.zone_name,
    bz.country,
    bz.avg_life_expectancy,
    bz.diet_description,
    bz.key_foods,
    bz.plant_based_pct,
    un.food_category,
    un.nutrient_name,
    un.avg_amount,
    un.unit
from blue_zones bz
cross join us_nutrition un
