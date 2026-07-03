select *
from {{ ref('int_ai_exposure_score') }}
where ai_exposure_score < 0
   or ai_exposure_score > 10
