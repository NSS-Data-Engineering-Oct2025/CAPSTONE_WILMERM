"""Export dbt mart tables from PostgreSQL to DuckDB as Parquet-backed tables.

Usage:
    uv run python -m src.export_to_duckdb

This creates a local DuckDB file (health_platform.duckdb) with the mart tables
exported from PostgreSQL, stored as Parquet files in the data/parquet/ directory.
"""

from pathlib import Path

import duckdb
from loguru import logger

from src.config import DatabaseConfig

PARQUET_DIR = Path(__file__).resolve().parent.parent / "data" / "parquet"
DUCKDB_PATH = Path(__file__).resolve().parent.parent / "health_platform.duckdb"

MART_TABLES = [
    "public_marts.mart_health_overview",
    "public_marts.mart_blue_zone_comparison",
]

STAGING_VIEWS = [
    "public_staging.stg_cdc_chronic_disease",
    "public_staging.stg_usda_foods",
    "public_staging.stg_epa_air_quality",
    "public_staging.stg_census_demographics",
    "public_staging.stg_blue_zones",
]


def export_to_duckdb() -> None:
    """Read mart tables from Postgres and write them to DuckDB + Parquet."""
    cfg = DatabaseConfig()

    PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DUCKDB_PATH))
    try:
        con.execute("INSTALL postgres; LOAD postgres;")
        con.execute(f"ATTACH 'dbname={cfg.dbname} host={cfg.host} port={cfg.port} user={cfg.user} password={cfg.password}' AS pg (TYPE POSTGRES, READ_ONLY);")

        for table in MART_TABLES + STAGING_VIEWS:
            safe_name = table.replace(".", "_")
            parquet_path = PARQUET_DIR / f"{safe_name}.parquet"

            con.execute(f"COPY (SELECT * FROM pg.{table}) TO '{parquet_path}' (FORMAT PARQUET);")
            con.execute(f"CREATE OR REPLACE TABLE {safe_name} AS SELECT * FROM '{parquet_path}';")

            row_count = con.execute(f"SELECT count(*) FROM {safe_name}").fetchone()[0]
            logger.info(f"  {table} -> {safe_name}: {row_count} rows")

        con.execute("DETACH pg;")
        logger.info(f"Export complete. DuckDB file: {DUCKDB_PATH}")
        logger.info(f"Parquet files: {PARQUET_DIR}")

    finally:
        con.close()


if __name__ == "__main__":
    export_to_duckdb()
