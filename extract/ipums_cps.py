"""
Fetch IPUMS CPS ASEC person-level microdata via the IPUMS Microdata Extract API.

The IPUMS API uses a job submission pattern:
  1. Submit extract request (samples + variables)
  2. IPUMS processes on their servers (2-10 min)
  3. ipumspy wait_for_extract() polls automatically until done
  4. Download .dat.gz + .xml DDI codebook
  5. Parse into DataFrame with ipumspy readers
  6. Save as Parquet (one file per year + one combined)

Outputs:
  data/raw/ipums_cps/cps_asec_{year}.parquet    (~180K persons/year, 60 cols)
  data/raw/ipums_cps/cps_asec_all.parquet       (~1.8M rows combined)

Register at: https://cps.ipums.org/cps/ -> My Account -> API Keys

Run: uv run python extract/ipums_cps.py
     uv run python extract/ipums_cps.py --sample   (2 years only)
"""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from ipumspy import IpumsApiClient, MicrodataExtract, readers

load_dotenv()

IPUMS_API_KEY = os.getenv("IPUMS_API_KEY")
RAW_DIR = Path(os.getenv("RAW_DATA_DIR", "./data/raw")) / "ipums_cps"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 60 variables per person -- the dimensions that make this highly dimensional
VARIABLES = [
    # Identifiers + weights (ASEC-confirmed)
    "YEAR", "SERIAL", "MONTH", "CPSID", "PERNUM", "CPSIDP",
    "ASECWT", "EARNWT",
    # Demographics
    "AGE", "SEX", "RACE", "HISPAN", "MARST", "NATIVITY", "CITIZEN",
    # Geography
    "STATEFIP", "REGION", "METFIPS",
    # Education
    "EDUC", "SCHLCOLL", "DIFFANY",
    # Occupation + Industry (join key to O*NET AI exposure score)
    "OCC", "OCC2010", "IND", "IND1990", "CLASSWKR", "FIRMSIZE",
    # Employment status
    "EMPSTAT", "LABFORCE", "WKSTAT", "AHRSWORKT", "WKSWORK1", "UHRSWORKLY",
    # Earnings
    "INCWAGE", "EARNWEEK", "HOURWAGE", "PAIDHOUR", "INCTOT", "INCBUS", "INCSS",
    # Benefits
    "UNION",
    # Unemployment details
    "WHYUNEMP", "DURUNEMP", "WKSUNEM1",
    # Work arrangement
    "FULLPART",
    # Household context
    "RELATE", "NCHILD", "FAMSIZE", "POVERTY", "OFFPOV",
]

# ASEC samples: cps{YEAR}_03s = March Annual Social & Economic Supplement
ASEC_SAMPLES_FULL  = [f"cps{y}_03s" for y in range(2015, 2025)]
ASEC_SAMPLES_SMALL = ["cps2022_03s", "cps2023_03s"]


def run(sample: bool = False) -> None:
    if not IPUMS_API_KEY:
        raise ValueError("IPUMS_API_KEY not set. Check your .env file.")

    client = IpumsApiClient(IPUMS_API_KEY)
    samples = ASEC_SAMPLES_SMALL if sample else ASEC_SAMPLES_FULL
    description = (
        f"AI Observatory CPS ASEC "
        f"{"sample" if sample else "full"} "
        f"{samples[0]}-{samples[-1]}, {len(VARIABLES)} variables"
    )

    # Step 1: Submit extract
    print(f"Submitting IPUMS extract...")
    print(f"  Samples: {samples[0]} to {samples[-1]} ({len(samples)} years)")
    print(f"  Variables: {len(VARIABLES)}")

    extract = MicrodataExtract(
        collection="cps",
        description=description,
        samples=samples,
        variables=VARIABLES,
    )
    client.submit_extract(extract)
    print(f"  Extract #{extract.extract_id} submitted.")

    # Step 2: Wait for processing
    print("  Waiting for IPUMS to process (2-10 min is normal)...")
    client.wait_for_extract(extract)
    print("  Extract ready. Downloading...")

    # Step 3: Download
    tmp_dir = RAW_DIR / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    client.download_extract(extract, download_dir=tmp_dir)

    # Step 4: Parse
    ddi_file  = next(tmp_dir.glob("*.xml"))
    data_file = next(tmp_dir.glob("*.dat.gz"))
    print(f"  Parsing {data_file.name}...")

    ddi_codebook = readers.read_ipums_ddi(ddi_file)
    df = readers.read_microdata(ddi_codebook, data_file)
    df.columns = [c.lower() for c in df.columns]
    print(f"  Parsed: {len(df):,} rows x {len(df.columns)} columns")

    # Step 5: Save to Parquet
    combined_path = RAW_DIR / "cps_asec_all.parquet"
    df.to_parquet(combined_path, index=False)
    print(f"  Saved combined: {combined_path}")

    for year, grp in df.groupby("year"):
        p = RAW_DIR / f"cps_asec_{int(year)}.parquet"
        grp.to_parquet(p, index=False)
        print(f"    cps_asec_{int(year)}.parquet  {len(grp):,} persons")

    # Cleanup temp files
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"\nIPUMS CPS extract complete: {len(df):,} total person records")


if __name__ == "__main__":
    import sys
    run(sample="--sample" in sys.argv)
