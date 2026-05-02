"""Ingest CDC Chronic Disease Indicators via Socrata API into PostgreSQL."""

from loguru import logger

from src.db import get_connection, ensure_raw_schema
from src.ingestion.http_client import fetch_json

CDC_BASE_URL = "https://data.cdc.gov/resource/hksd-2xuw.json"
PAGE_SIZE = 10_000

TOPICS_OF_INTEREST = [
    "Asthma",
    "Cancer",
    "Cardiovascular Disease",
    "Chronic Kidney Disease",
    "Chronic Obstructive Pulmonary Disease",
    "Diabetes",
    "Nutrition, Physical Activity, and Weight Status",
    "Tobacco",
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw.cdc_chronic_disease (
    yearstart         TEXT,
    yearend           TEXT,
    locationabbr      TEXT,
    locationdesc      TEXT,
    datasource        TEXT,
    topic             TEXT,
    question          TEXT,
    datavalueunit     TEXT,
    datavaluetype     TEXT,
    datavalue         TEXT,
    datavaluealt      TEXT,
    lowconfidencelimit  TEXT,
    highconfidencelimit TEXT,
    stratificationcategory1 TEXT,
    stratification1   TEXT,
    locationid        TEXT,
    topicid           TEXT,
    questionid        TEXT,
    datavaluetypeid   TEXT,
    stratificationcategoryid1 TEXT,
    stratificationid1 TEXT,
    ingested_at       TIMESTAMPTZ DEFAULT NOW()
);
"""

INSERT_SQL = """
INSERT INTO raw.cdc_chronic_disease (
    yearstart, yearend, locationabbr, locationdesc, datasource,
    topic, question, datavalueunit, datavaluetype, datavalue,
    datavaluealt, lowconfidencelimit, highconfidencelimit,
    stratificationcategory1, stratification1, locationid,
    topicid, questionid, datavaluetypeid,
    stratificationcategoryid1, stratificationid1
) VALUES (
    %(yearstart)s, %(yearend)s, %(locationabbr)s, %(locationdesc)s, %(datasource)s,
    %(topic)s, %(question)s, %(datavalueunit)s, %(datavaluetype)s, %(datavalue)s,
    %(datavaluealt)s, %(lowconfidencelimit)s, %(highconfidencelimit)s,
    %(stratificationcategory1)s, %(stratification1)s, %(locationid)s,
    %(topicid)s, %(questionid)s, %(datavaluetypeid)s,
    %(stratificationcategoryid1)s, %(stratificationid1)s
);
"""

COLUMNS = [
    "yearstart", "yearend", "locationabbr", "locationdesc", "datasource",
    "topic", "question", "datavalueunit", "datavaluetype", "datavalue",
    "datavaluealt", "lowconfidencelimit", "highconfidencelimit",
    "stratificationcategory1", "stratification1", "locationid",
    "topicid", "questionid", "datavaluetypeid",
    "stratificationcategoryid1", "stratificationid1",
]


def fetch_cdc_page(topic: str, offset: int) -> list[dict]:
    """Fetch a single page of CDC data for a given topic."""
    params = {
        "$limit": PAGE_SIZE,
        "$offset": offset,
        "$where": f"topic='{topic}'",
        "$order": "yearstart,locationabbr",
    }
    return fetch_json(CDC_BASE_URL, params=params)


def safe_row(record: dict) -> dict:
    """Extract only known columns, defaulting missing fields to None."""
    return {col: record.get(col) for col in COLUMNS}


def ingest_cdc() -> None:
    """Pull CDC Chronic Disease Indicators and load into raw.cdc_chronic_disease.

    Uses DELETE + INSERT strategy per topic to ensure idempotency.
    """
    ensure_raw_schema()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()

    total_inserted = 0

    for topic in TOPICS_OF_INTEREST:
        logger.info(f"Fetching topic: {topic}")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM raw.cdc_chronic_disease WHERE topic = %s;",
                    (topic,),
                )
                conn.commit()

        offset = 0
        topic_rows = 0
        more_pages = True

        while more_pages:
            batch = fetch_cdc_page(topic, offset)
            if not batch:
                more_pages = False
                continue

            rows = [safe_row(r) for r in batch]

            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.executemany(INSERT_SQL, rows)
                    conn.commit()

            topic_rows += len(rows)
            offset += PAGE_SIZE

            if len(batch) < PAGE_SIZE:
                more_pages = False

        logger.info(f"  {topic}: {topic_rows} rows inserted")
        total_inserted += topic_rows

    logger.info(f"CDC ingestion complete: {total_inserted} total rows")


if __name__ == "__main__":
    ingest_cdc()
