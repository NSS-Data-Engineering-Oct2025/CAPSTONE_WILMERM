with source as (
    select
        date_observed,
        hour_observed,
        local_time_zone,
        reporting_area,
        state_code,
        latitude,
        longitude,
        parameter_name,
        aqi,
        category_number,
        category_name
    from {{ source('raw', 'epa_air_quality') }}
)

select
    date_observed::date                     as observation_date,
    hour_observed,
    local_time_zone                         as timezone,
    reporting_area,
    state_code                              as state_abbr,
    latitude,
    longitude,
    parameter_name,
    aqi,
    category_number                         as aqi_category_num,
    category_name                           as aqi_category
from source
where aqi is not null
