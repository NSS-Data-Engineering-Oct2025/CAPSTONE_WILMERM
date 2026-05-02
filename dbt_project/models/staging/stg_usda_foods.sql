with source as (
    select
        fdc_id,
        description,
        data_type,
        food_category,
        publication_date,
        nutrients
    from {{ source('raw', 'usda_foods') }}
)

select
    fdc_id,
    initcap(description)                    as food_name,
    data_type,
    food_category,
    publication_date::date                  as published_date,
    nutrients
from source
where description is not null
