with oews as (
    select * from {{ ref('int_oews_employment_trend') }}
),
ai as (
    select * from {{ ref('int_ai_exposure_score') }}
)
select
    o.year,
    o.area_code,
    o.area_name,
    o.occupation_code,
    coalesce(o.occupation_name, ai.occupation_title) as occupation_title,
    o.industry_code,
    o.datatype_code,
    o.value,
    ai.ai_exposure_score,
    ai.ai_exposure_tier
from oews o
left join ai
    on o.occupation_code = ai.soc_code
