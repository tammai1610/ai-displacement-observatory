select
    trim(area_code) as area_code,
    trim(area_name) as area_name
from {{ source('raw', 'oews_area') }}
