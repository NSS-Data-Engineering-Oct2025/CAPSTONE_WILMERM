"""Ingest U.S. Census ACS 5-year demographic data into PostgreSQL."""

import httpx
from loguru import logger

from src.config import api_keys
from src.db import get_connection, ensure_raw_schema

CENSUS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5"

VARIABLES = {
    "NAME": "name",
    "B01001_001E": "total_population",
    "B19013_001E": "median_household_income",
    "B01002_001E": "median_age",
    "B15003_022E": "bachelors_degree",
    "B27001_001E": "health_insurance_total",
    "B17001_002E": "poverty_count",
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw.census_demographics (
    state_fips        TEXT,
    state_name        TEXT,
    total_population  INTEGER,
    median_household_income INTEGER,
    median_age        DOUBLE PRECISION,
    bachelors_degree  INTEGER,
    health_insurance_total INTEGER,
    poverty_count     INTEGER,
    ingested_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (state_fips)
);
"""

UPSERT_SQL = """
INSERT INTO raw.census_demographics (
    state_fips, state_name, total_population, median_household_income,
    median_age, bachelors_degree, health_insurance_total, poverty_count
) VALUES (
    %(state_fips)s, %(state_name)s, %(total_population)s, %(median_household_income)s,
    %(median_age)s, %(bachelors_degree)s, %(health_insurance_total)s, %(poverty_count)s
)
ON CONFLICT (state_fips) DO UPDATE SET
    state_name = EXCLUDED.state_name,
    total_population = EXCLUDED.total_population,
    median_household_income = EXCLUDED.median_household_income,
    median_age = EXCLUDED.median_age,
    bachelors_degree = EXCLUDED.bachelors_degree,
    health_insurance_total = EXCLUDED.health_insurance_total,
    poverty_count = EXCLUDED.poverty_count,
    ingested_at = NOW();
"""


def safe_int(val: str | None) -> int | None:
    """Convert Census string value to int, handling nulls and negatives."""
    if val is None or val == "" or val == "-666666666":
        return None
    return int(val)


def safe_float(val: str | None) -> float | None:
    """Convert Census string value to float, handling nulls."""
    if val is None or val == "" or val == "-666666666.0":
        return None
    return float(val)


def ingest_census() -> None:
    """Pull ACS 5-year data for all states and load into raw.census_demographics.

    Uses UPSERT on state_fips for idempotency.
    """
    ensure_raw_schema()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()

    var_codes = ",".join(VARIABLES.keys())
    params: dict[str, str] = {
        "get": var_codes,
        "for": "state:*",
    }
    if api_keys.census:
        params["key"] = api_keys.census

    response = httpx.get(CENSUS_BASE_URL, params=params, timeout=60, follow_redirects=True)
    response.raise_for_status()

    data = response.json()
    headers = data[0]
    rows_raw = data[1:]

    total_inserted = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for row_values in rows_raw:
                row_dict = dict(zip(headers, row_values))
                row = {
                    "state_fips": row_dict.get("state"),
                    "state_name": row_dict.get("NAME"),
                    "total_population": safe_int(row_dict.get("B01001_001E")),
                    "median_household_income": safe_int(row_dict.get("B19013_001E")),
                    "median_age": safe_float(row_dict.get("B01002_001E")),
                    "bachelors_degree": safe_int(row_dict.get("B15003_022E")),
                    "health_insurance_total": safe_int(row_dict.get("B27001_001E")),
                    "poverty_count": safe_int(row_dict.get("B17001_002E")),
                }
                cur.execute(UPSERT_SQL, row)
                total_inserted += 1
            conn.commit()

    logger.info(f"Census ingestion complete: {total_inserted} states/territories loaded")


if __name__ == "__main__":
    ingest_census()
