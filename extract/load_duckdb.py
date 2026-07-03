"""
Load all raw Parquet files into DuckDB as views under the raw schema.

Run this after all three extracts are complete:
  uv run python extract/onet_api.py
  uv run python extract/ipums_cps.py
  (BLS OEWS files downloaded manually per data/README.md)

Then run: uv run python extract/load_duckdb.py

Output: warehouse/labor.duckdb with raw.* views ready for dbt
"""
import duckdb
import os
from pathlib import Path

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "warehouse/labor.duckdb")
Path(DUCKDB_PATH).parent.mkdir(exist_ok=True)


VIEWS = {
    # O*NET
    "raw.onet_work_activities": "data/raw/onet/work_activities.parquet",
    "raw.onet_abilities":       "data/raw/onet/abilities.parquet",
    "raw.onet_occupations":     "data/raw/onet/occupations.parquet",
    # OEWS
    "raw.oews_data":            "data/raw/oews/oe_data.parquet",
    "raw.oews_series":          "data/raw/oews/oe_series.parquet",
    "raw.oews_occupation":      "data/raw/oews/oe_occupation.parquet",
    "raw.oews_area":            "data/raw/oews/oe_area.parquet",
    "raw.oews_industry":        "data/raw/oews/oe_industry.parquet",
    # IPUMS CPS
    "raw.cps_persons":          "data/raw/ipums_cps/cps_asec_all.parquet",
}


def run() -> None:
    con = duckdb.connect(DUCKDB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for view_name, parquet_path in VIEWS.items():
        path = Path(parquet_path)
        if not path.exists():
            print(f"  SKIP {view_name} — {parquet_path} not found")
            continue

        con.execute(f"""
            CREATE OR REPLACE VIEW {view_name} AS
            SELECT * FROM read_parquet('{parquet_path}')
        """)
        count = con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
        print(f"  {view_name:<35} {count:>12,} rows")

    print(f"\nLoad complete. {DUCKDB_PATH} is ready for dbt.")
    con.close()


if __name__ == "__main__":
    run()
