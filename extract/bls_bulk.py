"""
Convert BLS OEWS flat files to Parquet.

Files must be manually downloaded from:
  https://download.bls.gov/pub/time.series/oe/

Download these 5 files into data/raw/oews/:
  oe.data.1.AllData
  oe.series
  oe.occupation
  oe.area
  oe.industry

Then run: uv run python extract/bls_bulk.py
"""
import duckdb
from pathlib import Path

RAW_DIR = Path("./data/raw/oews")
RAW_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "oe_area":       RAW_DIR / "oe.area",
    "oe_data":       RAW_DIR / "oe.data.1.AllData",
    "oe_industry":   RAW_DIR / "oe.industry",
    "oe_occupation": RAW_DIR / "oe.occupation",
    "oe_series":     RAW_DIR / "oe.series",
}


def run() -> None:
    con = duckdb.connect()

    for name, path in FILES.items():
        parquet = RAW_DIR / f"{name}.parquet"

        if not path.exists():
            print(f"  SKIP {path.name} — not found. Download manually first.")
            continue

        if parquet.exists():
            print(f"  SKIP {name}.parquet — already exists.")
            continue

        print(f"Converting {path.name}...")
        con.execute(f"""
            COPY (
                SELECT * FROM read_csv_auto(
                    '{path}',
                    delim=chr(9),
                    header=True,
                    ignore_errors=True
                )
            ) TO '{parquet}' (FORMAT PARQUET)
        """)
        count = con.execute(f"SELECT COUNT(*) FROM '{parquet}'").fetchone()[0]
        print(f"  -> {parquet.name}  ({count:,} rows)")

    con.close()
    print("\nBLS OEWS conversion complete.")


if __name__ == "__main__":
    run()
