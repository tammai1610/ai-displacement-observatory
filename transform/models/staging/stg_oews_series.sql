select
    trim(series_id) as series_id,
    trim(seasonal) as seasonal,
    trim(areatype_code) as areatype_code,
    trim(area_code) as area_code,
    trim(industry_code) as industry_code,
    trim(occupation_code) as occupation_code,
    trim(datatype_code) as datatype_code,
    cast(state_code as integer) as state_code,
    trim(sector_code) as sector_code,
    trim(series_title) as series_title,
    cast(begin_year as integer) as begin_year,
    trim(begin_period) as begin_period,
    cast(end_year as integer) as end_year,
    trim(end_period) as end_period
from {{ source('raw', 'oews_series') }}
