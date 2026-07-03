.PHONY: install extract extract-sample load transform seed build build-sample test validate validate-pipeline clean

install:
	uv sync
	uv sync --project transform

extract:
	uv run python -m extract.run_all

extract-sample:
	uv run python -m extract.run_all --sample

load:
	uv run python extract/load_duckdb.py

transform:
	uv run --project transform dbt run --project-dir transform --profiles-dir transform

seed:
	uv run --project transform dbt seed --project-dir transform --profiles-dir transform

build:
	uv run --project transform dbt build --project-dir transform --profiles-dir transform

build-sample:
	uv run --project transform dbt seed --project-dir transform --profiles-dir transform
	uv run --project transform dbt build --project-dir transform --profiles-dir transform --select +fct_worker_risk

test:
	uv run --project transform dbt test --project-dir transform --profiles-dir transform

validate:
	python -m py_compile extract/*.py
	uv run --project transform dbt parse --project-dir transform --profiles-dir transform

validate-pipeline:
	uv run python -m extract.run_all --sample
	uv run python extract/load_duckdb.py
	uv run --project transform dbt seed --project-dir transform --profiles-dir transform
	uv run --project transform dbt build --project-dir transform --profiles-dir transform --select +fct_worker_risk

clean:
	rm -f warehouse/*.duckdb
	rm -rf transform/target transform/logs
