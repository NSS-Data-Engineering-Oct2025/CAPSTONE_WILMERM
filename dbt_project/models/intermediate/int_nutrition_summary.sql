with foods as (
    select
        fdc_id,
        food_name,
        food_category,
        nutrients
    from {{ ref('stg_usda_foods') }}
    where food_category is not null
),

nutrients_flat as (
    select
        f.food_category,
        n.elem ->> 'name'                  as nutrient_name,
        (n.elem ->> 'amount')::numeric     as amount,
        n.elem ->> 'unit'                  as unit
    from foods f,
         jsonb_array_elements(f.nutrients) as n(elem)
    where n.elem ->> 'amount' is not null
)

select
    food_category,
    nutrient_name,
    unit,
    count(*)                                as food_count,
    round(avg(amount), 2)                   as avg_amount,
    round(min(amount), 2)                   as min_amount,
    round(max(amount), 2)                   as max_amount
from nutrients_flat
group by food_category, nutrient_name, unit
