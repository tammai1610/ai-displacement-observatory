# Data Directory

Raw data files live here. They are gitignored and must be regenerated locally.

---

## How to regenerate all data

### Step 1: O*NET (automatic)
Run the extract script — no manual steps needed:
Outputs: `data/raw/onet/`

---

### Step 2: BLS OEWS (manual download required)

BLS blocks automated downloads. You must download these 5 files manually in your browser.

Open each URL and press Cmd+S to save into `data/raw/oews/`:

- https://download.bls.gov/pub/time.series/oe/oe.data.1.AllData  (~316MB, takes a few min)
- https://download.bls.gov/pub/time.series/oe/oe.series
- https://download.bls.gov/pub/time.series/oe/oe.occupation
- https://download.bls.gov/pub/time.series/oe/oe.area
- https://download.bls.gov/pub/time.series/oe/oe.industry

Important: if your browser saves oe.area as oe.area.txt, rename it:
Then convert to Parquet:
Outputs: `data/raw/oews/`

---

### Step 3: IPUMS CPS (automatic, but requires API key + wait time)

Make sure IPUMS_API_KEY is set in your .env file.
Register at: https://cps.ipums.org/cps/ -> My Account -> API Keys

Run:
Note: IPUMS processes the extract on their servers. Expect 2-10 min wait
before the download starts. This is normal — do not cancel the script.

Outputs: `data/raw/ipums_cps/`

---

## Folder structure after full extract
data/raw/
onet/
occupations.parquet        (~1,016 rows)
work_activities.parquet    (~41,000 rows)
abilities.parquet          (~52,000 rows)
oews/
oe_area.parquet            (~583 rows)
oe_data.parquet            (~6M rows)
oe_industry.parquet        (~444 rows)
oe_occupation.parquet      (~1,104 rows)
oe_series.parquet          (~6M rows)
ipums_cps/
cps_asec_all.parquet       (~1.8M rows, 49 columns)
cps_asec_2015.parquet
cps_asec_2016.parquet
...
cps_asec_2024.parquet
