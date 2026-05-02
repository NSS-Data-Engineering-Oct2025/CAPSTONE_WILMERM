"""Ingest EPA AirNow current air quality observations into PostgreSQL."""

from loguru import logger

from src.config import api_keys
from src.db import get_connection, ensure_raw_schema
from src.ingestion.http_client import fetch_json

EPA_BASE_URL = "https://www.airnowapi.org/aq/observation/zipCode/current/"

TN_ZIP_CODES = [
    "37201",  # Nashville
    "37902",  # Knoxville
    "38103",  # Memphis
    "37402",  # Chattanooga
    "37604",  # Johnson City
    "37040",  # Clarksville
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw.epa_air_quality (
    date_observed     TEXT,
    hour_observed     INTEGER,
    local_time_zone   TEXT,
    reporting_area    TEXT,
    state_code        TEXT,
    latitude          DOUBLE PRECISION,
    longitude         DOUBLE PRECISION,
    parameter_name    TEXT,
    aqi               INTEGER,
    category_number   INTEGER,
    category_name     TEXT,
    source_zip        TEXT,
    ingested_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (date_observed, hour_observed, reporting_area, parameter_name)
);
"""

UPSERT_SQL = """
INSERT INTO raw.epa_air_quality (
    date_observed, hour_observed, local_time_zone, reporting_area,
    state_code, latitude, longitude, parameter_name, aqi,
    category_number, category_name, source_zip
) VALUES (
    %(date_observed)s, %(hour_observed)s, %(local_time_zone)s, %(reporting_area)s,
    %(state_code)s, %(latitude)s, %(longitude)s, %(parameter_name)s, %(aqi)s,
    %(category_number)s, %(category_name)s, %(source_zip)s
)
ON CONFLICT (date_observed, hour_observed, reporting_area, parameter_name) DO UPDATE SET
    aqi = EXCLUDED.aqi,
    category_number = EXCLUDED.category_number,
    category_name = EXCLUDED.category_name,
    ingested_at = NOW();
"""


def build_row(obs: dict, zip_code: str) -> dict:
    """Transform an EPA observation into a row for insertion."""
    category = obs.get("Category", {})
    return {
        "date_observed": obs.get("DateObserved", "").strip(),
        "hour_observed": obs.get("HourObserved"),
        "local_time_zone": obs.get("LocalTimeZone"),
        "reporting_area": obs.get("ReportingArea"),
        "state_code": obs.get("StateCode"),
        "latitude": obs.get("Latitude"),
        "longitude": obs.get("Longitude"),
        "parameter_name": obs.get("ParameterName"),
        "aqi": obs.get("AQI"),
        "category_number": category.get("Number"),
        "category_name": category.get("Name"),
        "source_zip": zip_code,
    }


def ingest_epa() -> None:
    """Pull current AQI observations for Tennessee zip codes and load into raw.epa_air_quality.

    Uses UPSERT on (date, hour, area, parameter) for idempotency.
    """
    ensure_raw_schema()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()

    total_inserted = 0

    for zip_code in TN_ZIP_CODES:
        params = {
            "format": "application/json",
            "zipCode": zip_code,
            "API_KEY": api_keys.epa_airnow,
        }
        observations = fetch_json(EPA_BASE_URL, params=params)

        if not observations:
            logger.info(f"  ZIP {zip_code}: no observations")
            continue

        rows = [build_row(obs, zip_code) for obs in observations]

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(UPSERT_SQL, rows)
                conn.commit()

        total_inserted += len(rows)
        areas = {r["reporting_area"] for r in rows}
        logger.info(f"  ZIP {zip_code}: {len(rows)} observations ({', '.join(areas)})")

    logger.info(f"EPA ingestion complete: {total_inserted} total observations")


if __name__ == "__main__":
    ingest_epa()
