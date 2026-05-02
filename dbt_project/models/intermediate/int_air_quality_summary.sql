with epa as (
    select
        observation_date,
        state_abbr,
        reporting_area,
        parameter_name,
        aqi,
        aqi_category
    from {{ ref('stg_epa_air_quality') }}
)

select
    state_abbr,
    reporting_area,
    parameter_name,
    count(*)                                as observation_count,
    round(avg(aqi), 1)                      as avg_aqi,
    max(aqi)                                as max_aqi,
    min(aqi)                                as min_aqi,
    min(observation_date)                   as first_observation,
    max(observation_date)                   as last_observation
from epa
group by state_abbr, reporting_area, parameter_name
