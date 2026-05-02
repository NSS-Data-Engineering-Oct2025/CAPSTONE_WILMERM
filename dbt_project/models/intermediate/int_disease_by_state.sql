with cdc as (
    select
        state_abbr,
        state_name,
        topic,
        question,
        year_start,
        data_value,
        value_unit,
        value_type
    from {{ ref('stg_cdc_chronic_disease') }}
    where stratification_category = 'Overall'
      and stratification = 'Overall'
),

latest_year as (
    select
        state_abbr,
        topic,
        question,
        max(year_start) as max_year
    from cdc
    group by state_abbr, topic, question
)

select
    c.state_abbr,
    c.state_name,
    c.topic,
    c.question,
    c.year_start,
    c.data_value,
    c.value_unit,
    c.value_type
from cdc c
inner join latest_year ly
    on c.state_abbr = ly.state_abbr
   and c.topic = ly.topic
   and c.question = ly.question
   and c.year_start = ly.max_year
