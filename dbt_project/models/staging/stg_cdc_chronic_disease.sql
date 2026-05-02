with source as (
    select
        yearstart,
        yearend,
        locationabbr,
        locationdesc,
        topic,
        question,
        datavalueunit,
        datavaluetype,
        datavalue,
        datavaluealt,
        lowconfidencelimit,
        highconfidencelimit,
        stratificationcategory1,
        stratification1,
        locationid,
        topicid,
        questionid
    from {{ source('raw', 'cdc_chronic_disease') }}
)

select
    yearstart::int                          as year_start,
    yearend::int                            as year_end,
    locationabbr                            as state_abbr,
    locationdesc                            as state_name,
    topic,
    question,
    datavalueunit                           as value_unit,
    datavaluetype                           as value_type,
    datavaluealt::numeric                   as data_value,
    lowconfidencelimit::numeric             as confidence_low,
    highconfidencelimit::numeric            as confidence_high,
    stratificationcategory1                 as stratification_category,
    stratification1                         as stratification,
    locationid                              as location_id,
    topicid                                 as topic_id,
    questionid                              as question_id
from source
where locationabbr not in ('US', 'GU', 'PR', 'VI', 'DC')
  and datavaluealt is not null
