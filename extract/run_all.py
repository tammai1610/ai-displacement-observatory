"""
Entry point: runs all three extract scripts in sequence.

Usage:
  uv run python extract/run_all.py             # full extract (~20 min)
  uv run python extract/run_all.py --sample    # small subset for testing
"""
import sys
import asyncio
from extract import onet_api, ipums_cps, bls_bulk

sample = "--sample" in sys.argv


def header(n, title):
    print(f"\n{"="*60}")
    print(f"  {n}  {title}")
    print(f"{"="*60}")


header("1/3", "O*NET API  (occupation task + ability ratings)")
asyncio.run(onet_api.run(sample=sample))

header("2/3", "IPUMS CPS ASEC  (person-level microdata, ~60 dimensions)")
if not sample:
    print("  NOTE: IPUMS processes server-side, expect 2-10 min wait.")
ipums_cps.run(sample=sample)

header("3/3", "BLS OEWS Bulk  (employment counts by occupation x geography)")
if sample:
    print("  Skipping in sample mode.")
else:
    bls_bulk.run()

print("\nAll extracts complete.")
