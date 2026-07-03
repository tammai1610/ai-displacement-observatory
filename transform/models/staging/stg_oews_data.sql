select
    trim(series_id) as series_id,
    cast(year as integer) as year,
    trim(period) as period,
    try_cast(nullif(trim(cast(value as varchar)), '-') as double) as value,
    footnote_codes
from {{ source('raw', 'oews_data') }}
