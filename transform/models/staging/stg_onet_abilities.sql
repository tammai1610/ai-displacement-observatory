select
    trim(onet_code) as onet_code,
    trim(ability_id) as ability_id,
    trim(ability_name) as ability_name,
    cast(importance as double) as importance_score
from {{ source('raw', 'onet_abilities') }}
where importance is not null
