select distinct
    state_fips,
    region,
    metro_fips
from {{ ref('stg_cps_persons') }}
where state_fips is not null
