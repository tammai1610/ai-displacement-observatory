select
    onet_code,
    soc_code,
    occupation_title,
    ai_exposure_score,
    ai_exposure_tier
from {{ ref('int_ai_exposure_score') }}
