`census_occ_to_onet_crosswalk.csv` is intentionally committed as a template with headers only.

To get worker-level AI exposure joins that are analytically correct, replace it with the full
Census `OCC2010` to O*NET occupation mapping before running `dbt build`.

The rest of the project is structured so the pipeline still parses and builds cleanly once that
seed is populated and the raw data has been extracted.
