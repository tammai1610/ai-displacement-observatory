select *
from {{ ref('fct_worker_risk') }}
where ai_exposure_tier is null
  and onet_code is not null
