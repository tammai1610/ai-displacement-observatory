with activities as (
    select * from {{ ref('stg_onet_work_activities') }}
),
weights as (
    select * from {{ ref('ai_activity_weights') }}
),
scored as (
    select
        a.onet_code,
        sum(case when w.ai_exposure_category = 'high' then a.importance_score * w.weight else 0 end) as high_score,
        sum(case when w.ai_exposure_category = 'low' then a.importance_score * w.weight else 0 end) as low_score
    from activities a
    left join weights w
        on a.activity_id = w.activity_id
    group by a.onet_code
),
normalized as (
    select
        onet_code,
        high_score,
        low_score,
        high_score - low_score as raw_score,
        round(
            10 * (
                (high_score - low_score - min(high_score - low_score) over ())
                / nullif(
                    max(high_score - low_score) over () - min(high_score - low_score) over (),
                    0
                )
            ),
            2
        ) as ai_exposure_score
    from scored
)
select
    n.onet_code,
    regexp_replace(n.onet_code, '\\..*$', '') as soc_code,
    o.occupation_title,
    n.high_score,
    n.low_score,
    n.raw_score,
    n.ai_exposure_score,
    case
        when n.ai_exposure_score >= 7 then 'high'
        when n.ai_exposure_score >= 4 then 'medium'
        else 'low'
    end as ai_exposure_tier
from normalized n
left join {{ ref('stg_onet_occupations') }} o
    on n.onet_code = o.onet_code
