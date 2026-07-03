# AI Displacement Observatory

An ETL pipeline to extract, load, and analyze labor market exposure to AI disruption across US occupations and demographics.

## Project Overview

This project builds a data warehouse combining three authoritative labor market datasets:
- **O*NET**: Occupation taxonomies, work activities, and ability requirements
- **BLS OEWS**: Employment levels and wages by occupation, industry, and geography
- **IPUMS CPS**: Individual worker demographics, earnings, and employment status

The data enables analysis of which occupations, industries, and demographics are most exposed to AI-driven displacement.

## Architecture

```
extract/          → Fetches raw data from APIs and bulk downloads
  ├── onet_api.py      (O*NET API)
  ├── bls_bulk.py      (BLS OEWS manual downloads)
  ├── ipums_cps.py     (IPUMS API)
  ├── run_all.py       (Orchestrator)
  └── load_duckdb.py   (Loads into warehouse)

transform/        → dbt project for data transformation
  ├── models/          (SQL transformation layer)
  ├── seeds/           (Reference data)
  └── tests/           (dbt data quality tests)

warehouse/        → DuckDB database (gitignored)
  └── labor.duckdb

data/             → Raw Parquet files (gitignored)
  └── raw/
      ├── onet/        (occupations, work_activities, abilities)
      ├── oews/        (employment, wage, area, industry, occupation)
      └── ipums_cps/   (annual + year-specific worker extracts)
```

## Setup

### Install Dependencies

```bash
uv sync
uv sync --project transform
```

### Configure API Keys

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# O*NET (choose one auth method)
ONET_API_KEY=your_key_here              # OR
ONET_USERNAME=username
ONET_PASSWORD=password

# IPUMS (required for automated extract)
IPUMS_API_KEY=your_key_here

# Optional
RAW_DATA_DIR=./data/raw                 # Default path for raw Parquet files
DUCKDB_PATH=warehouse/labor.duckdb      # Default warehouse location
```

**API Key Registration:**
- O*NET: https://api.onetcenter.org/ (free, no key for basic access)
- IPUMS: https://cps.ipums.org/cps/ → My Account → API Keys
- BLS: No automation available; manual download required

## Data Pipeline

### 1. Extract Raw Data

```bash
# Extract all sources (O*NET + IPUMS; BLS requires manual download)
make extract

# Sample mode (first 50 occupations, 2 years of IPUMS)
make extract-sample
```

**Full Extract Details:**
See [data/README.md](data/README.md) for instructions on:
- Automatic O*NET API fetch
- Manual BLS OEWS bulk download
- Automatic IPUMS CPS extract (with wait time)

### 2. Load into Data Warehouse

```bash
make load
```

Creates DuckDB database with raw.* views:
- `raw.onet_occupations`
- `raw.onet_work_activities`
- `raw.onet_abilities`
- `raw.oews_area`
- `raw.oews_data`
- `raw.oews_industry`
- `raw.oews_occupation`
- `raw.oews_series`
- `raw.ipums_cps_all`
- `raw.ipums_cps_<year>`

### 3. Transform with dbt

```bash
# Run all transformations
make build

# Quick test with sample data
make build-sample

# Run data quality tests
make test

# Seed reference data
make seed
```

### 4. Validate Pipeline

Test the complete pipeline end-to-end:

```bash
make validate-pipeline
```

## Development

### Format & Lint

Pre-commit hooks automatically format code:

```bash
uv run ruff check extract/ --fix
uv run ruff format extract/
```

### Type Check & Parse

```bash
make validate
```

### Clean Up

Remove generated artifacts:

```bash
make clean
```

## Pipeline Outputs

The warehouse produces several key fact and dimension tables. See `transform/models/` for full documentation.

### Key Dimensions
- Worker demographics and education
- Occupation and industry hierarchies
- Geographic areas

### Key Facts
- Worker earnings and employment
- Occupation-industry employment levels
- Worker risk scores (output of analysis)

## Data Notes

- **All data is gitignored** — raw files must be regenerated locally
- **BLS data requires manual download** — see `data/README.md`
- **IPUMS is time-gated** — expect 2–10 min wait for server processing
- **File sizes** — Full extract ~1.8GB; sample mode uses 2 IPUMS years + 50 O*NET occupations

## Project Structure

- `extract/` — Extraction scripts for each data source
- `transform/` — dbt project with transformation layer
- `data/raw/` — Raw Parquet files (excluded from git)
- `warehouse/` — DuckDB database files (excluded from git)
- `Makefile` — Common task shortcuts
- `.env.example` — Template for environment configuration

## License

See repository for license details.
