select
    trim(occupation_code) as occupation_code,
    trim(occupation_name) as occupation_name
from {{ source('raw', 'oews_occupation') }}
