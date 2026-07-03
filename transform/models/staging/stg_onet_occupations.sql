select
    trim(code) as onet_code,
    trim(title) as occupation_title
from {{ source('raw', 'onet_occupations') }}
