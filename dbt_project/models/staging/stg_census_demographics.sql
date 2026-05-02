with source as (
    select
        state_fips,
        state_name,
        total_population,
        median_household_income,
        median_age,
        bachelors_degree,
        health_insurance_total,
        poverty_count
    from {{ source('raw', 'census_demographics') }}
)

select
    state_fips,
    state_name,
    total_population,
    median_household_income,
    median_age,
    bachelors_degree,
    health_insurance_total,
    poverty_count,
    case
        when total_population > 0
        then round(poverty_count::numeric / total_population * 100, 2)
    end                                     as poverty_rate_pct
from source
where total_population is not null
  and total_population > 0
