# Seeds

## `census_occ_to_onet_crosswalk.csv`

Maps IPUMS/Census `OCC2010` codes to O*NET-SOC 2019 codes (1,044 rows, 538 census
codes, 1,012 O*NET codes). Built by [scripts/build_crosswalk.py](../../scripts/build_crosswalk.py) from:

- Census 2010 Occupation Code List with 2010 SOC codes —
  https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2010-occ-codes-with-crosswalk-from-2002-2011.xls
- O*NET-SOC 2010 to O*NET-SOC 2019 crosswalk —
  https://www.onetcenter.org/taxonomy/2019/walk/2010_to_2019_Crosswalk.csv?fmt=csv

Census SOC values that are broad groups (`53-1000`) or residual wildcards (`47-50XX`)
are expanded by prefix; wildcard rows only take SOC codes no specific census code claimed.

The mapping is one-to-many: a census occupation can cover several O*NET occupations
(max 38, for `2200` Postsecondary teachers). Joining it to worker rows fans them out
(764k CPS persons -> 2.3M rows in `fct_worker_risk`), so aggregate exposure per
`census_occ2010` before weighting counts.

`occ2010 = 9999` (IPUMS unknown/NIU) has no mapping by design.

## `ai_activity_weights.csv`

All 41 O*NET 4.A work activities, each tagged `high` (LLM-substitutable cognitive
and information work) or `low` (physical, in-person, or relational work) with a
0-1 weight. Regenerate with [scripts/build_weights.py](../../scripts/build_weights.py); `activity_id`
and `activity_name` come from `data/raw/onet/work_activities.parquet`, so the ids
always match the raw data the score model joins against.

The weight/category assignment is a judgment call, not an official source — edit
`SCORES` in the build script to change the exposure definition.
