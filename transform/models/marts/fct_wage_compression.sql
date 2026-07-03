select
    year,
    ai_exposure_tier,
    count(*) as person_count,
    round(avg(usual_weekly_earnings), 2) as avg_weekly_earnings,
    round(avg(hourly_wage), 2) as avg_hourly_wage
from {{ ref('fct_worker_risk') }}
where usual_weekly_earnings is not null
group by 1, 2
