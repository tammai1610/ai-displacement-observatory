select
    trim(onet_code) as onet_code,
    trim(activity_id) as activity_id,
    trim(activity_name) as activity_name,
    cast(importance as double) as importance_score
from {{ source('raw', 'onet_work_activities') }}
where importance is not null
