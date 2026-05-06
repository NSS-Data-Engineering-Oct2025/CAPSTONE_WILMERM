with state_map as (
    select
        state_abbr,
        state_name,
        state_fips
    from {{ ref('state_lookup') }}
),

census as (
    select
        state_fips,
        state_name,
        total_population,
        median_household_income,
        median_age,
        poverty_rate_pct
    from {{ ref('stg_census_demographics') }}
),

disease as (
    select
        state_abbr,
        topic,
        question,
        data_value,
        value_type,
        year_start,
        row_number() over (
            partition by state_abbr, topic, question
            order by year_start desc
        ) as rn
    from {{ ref('int_disease_by_state') }}
    where value_type = 'Crude Prevalence'
),

diabetes as (
    select state_abbr, data_value as diabetes_prevalence
    from disease
    where topic = 'Diabetes'
      and question like '%Diabetes among adults%'
      and rn = 1
),

asthma as (
    select state_abbr, data_value as asthma_prevalence
    from disease
    where topic = 'Asthma'
      and question like '%Current asthma among adults%'
      and rn = 1
),

obesity as (
    select state_abbr, data_value as obesity_prevalence
    from disease
    where topic = 'Nutrition, Physical Activity, and Weight Status'
      and question like '%Obesity among adults%'
      and rn = 1
),

air as (
    select
        state_abbr,
        round(avg(avg_aqi), 1) as avg_aqi
    from {{ ref('int_air_quality_summary') }}
    group by state_abbr
)

select
    sm.state_abbr,
    c.state_name,
    c.total_population,
    c.median_household_income,
    c.median_age,
    c.poverty_rate_pct,
    d.diabetes_prevalence,
    a.asthma_prevalence,
    o.obesity_prevalence,
    aq.avg_aqi
from census c
inner join state_map sm on c.state_name = sm.state_name
left join diabetes d on sm.state_abbr = d.state_abbr
left join asthma a on sm.state_abbr = a.state_abbr
left join obesity o on sm.state_abbr = o.state_abbr
left join air aq on sm.state_abbr = aq.state_abbr
