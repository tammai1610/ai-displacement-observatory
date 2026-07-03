with series_meta as (
    select * from {{ ref('stg_oews_series') }}
),
data_points as (
    select * from {{ ref('stg_oews_data') }}
),
occupations as (
    select * from {{ ref('stg_oews_occupation') }}
),
areas as (
    select * from {{ ref('stg_oews_area') }}
)
select
    d.year,
    s.area_code,
    a.area_name,
    s.occupation_code,
    o.occupation_name,
    s.industry_code,
    s.datatype_code,
    d.value
from data_points d
left join series_meta s
    on d.series_id = s.series_id
left join occupations o
    on s.occupation_code = o.occupation_code
left join areas a
    on s.area_code = a.area_code
where d.period = 'A01'
