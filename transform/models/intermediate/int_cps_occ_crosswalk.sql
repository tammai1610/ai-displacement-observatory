select
    cast(nullif(trim(cast(census_occ2010 as varchar)), '') as integer) as census_occ2010,
    trim(cast(onet_code as varchar)) as onet_code
from {{ ref('census_occ_to_onet_crosswalk') }}
where nullif(trim(cast(census_occ2010 as varchar)), '') is not null
