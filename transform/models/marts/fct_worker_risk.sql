with persons as (
    select *
    from {{ ref('stg_cps_persons') }}
    where in_labor_force = 2
      and age between 18 and 65
),
crosswalk as (
    select * from {{ ref('int_cps_occ_crosswalk') }}
),
ai as (
    select * from {{ ref('int_ai_exposure_score') }}
)
select
    p.year,
    p.serial,
    p.pernum,
    p.cpsid,
    p.cpsidp,
    p.person_weight,
    p.earnings_weight,
    p.age,
    case
        when p.age between 18 and 24 then '18-24'
        when p.age between 25 and 34 then '25-34'
        when p.age between 35 and 44 then '35-44'
        when p.age between 45 and 54 then '45-54'
        else '55-65'
    end as age_group,
    p.sex,
    p.race,
    p.hispanic,
    p.marital_status,
    p.nativity,
    p.citizenship,
    p.education,
    p.school_college_status,
    p.disability_any,
    p.state_fips,
    p.region,
    p.metro_fips,
    p.occ_code,
    p.occ2010,
    p.ind_code,
    p.ind1990,
    p.class_worker,
    p.firm_size,
    p.emp_status,
    p.work_status,
    p.actual_hours_this_week,
    p.weeks_worked_last_year,
    p.usual_hours_per_week,
    p.wage_income_last_year,
    p.usual_weekly_earnings,
    p.hourly_wage,
    p.paid_hourly,
    p.total_income,
    p.business_income,
    p.social_security_income,
    p.union_status,
    p.reason_unemployed,
    p.weeks_unemployed_current,
    p.weeks_unemployed_last_year,
    p.full_part_time,
    p.relationship_to_household_head,
    p.num_children,
    p.family_size,
    p.poverty_ratio,
    p.below_poverty_line,
    c.onet_code,
    ai.occupation_title,
    ai.ai_exposure_score,
    ai.ai_exposure_tier,
    case
        when ai.ai_exposure_tier = 'high' and coalesce(p.emp_status, 0) != 1 then 'at_risk_unemployed'
        when ai.ai_exposure_tier = 'high' and coalesce(p.wage_income_last_year, 0) = 0 then 'at_risk_no_income'
        when ai.ai_exposure_tier = 'high' then 'high_exposure_employed'
        when ai.ai_exposure_tier = 'low' then 'low_exposure'
        else 'unknown'
    end as worker_risk_status
from persons p
left join crosswalk c
    on p.occ2010 = c.census_occ2010
left join ai
    on c.onet_code = ai.onet_code
