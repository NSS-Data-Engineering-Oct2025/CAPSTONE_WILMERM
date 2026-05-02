"""Ingest USDA FoodData Central nutrient data via REST API into PostgreSQL."""

import json

from loguru import logger

from src.config import api_keys
from src.db import get_connection, ensure_raw_schema
from src.ingestion.http_client import fetch_json

USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
PAGE_SIZE = 200

FOOD_CATEGORIES = [
    "Vegetables and Vegetable Products",
    "Fruits and Fruit Juices",
    "Legumes and Legume Products",
    "Cereal Grains and Pasta",
    "Dairy and Egg Products",
    "Fats and Oils",
    "Poultry Products",
    "Beef Products",
    "Pork Products",
    "Finfish and Shellfish Products",
    "Nut and Seed Products",
    "Sweets",
    "Beverages",
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw.usda_foods (
    fdc_id            INTEGER PRIMARY KEY,
    description       TEXT,
    data_type         TEXT,
    food_category     TEXT,
    publication_date  TEXT,
    nutrients         JSONB,
    ingested_at       TIMESTAMPTZ DEFAULT NOW()
);
"""

UPSERT_SQL = """
INSERT INTO raw.usda_foods (fdc_id, description, data_type, food_category, publication_date, nutrients)
VALUES (%(fdc_id)s, %(description)s, %(data_type)s, %(food_category)s, %(publication_date)s, %(nutrients)s)
ON CONFLICT (fdc_id) DO UPDATE SET
    description = EXCLUDED.description,
    data_type = EXCLUDED.data_type,
    food_category = EXCLUDED.food_category,
    publication_date = EXCLUDED.publication_date,
    nutrients = EXCLUDED.nutrients,
    ingested_at = NOW();
"""

TARGET_NUTRIENTS = {
    "Energy", "Protein", "Total lipid (fat)", "Carbohydrate, by difference",
    "Fiber, total dietary", "Sugars, Total", "Calcium, Ca", "Iron, Fe",
    "Sodium, Na", "Vitamin C, total ascorbic acid", "Vitamin A, RAE",
    "Cholesterol", "Fatty acids, total saturated",
}


def extract_nutrients(food: dict) -> str:
    """Pull only target nutrients from the food's nutrient list and return as JSON string."""
    raw_nutrients = food.get("foodNutrients", [])
    filtered = [
        {
            "name": n.get("nutrientName"),
            "amount": n.get("value"),
            "unit": n.get("unitName"),
        }
        for n in raw_nutrients
        if n.get("nutrientName") in TARGET_NUTRIENTS
    ]
    return json.dumps(filtered)


def build_row(food: dict) -> dict:
    """Transform a USDA food record into a row for insertion."""
    return {
        "fdc_id": food["fdcId"],
        "description": food.get("description"),
        "data_type": food.get("dataType"),
        "food_category": food.get("foodCategory"),
        "publication_date": food.get("publishedDate"),
        "nutrients": extract_nutrients(food),
    }


def fetch_foods_page(page: int) -> dict:
    """Fetch one page from the USDA foods/list endpoint."""
    url = f"{USDA_BASE_URL}/foods/search"
    params = {
        "api_key": api_keys.usda,
        "dataType": "Foundation,SR Legacy",
        "pageSize": PAGE_SIZE,
        "pageNumber": page,
        "sortBy": "fdcId",
        "sortOrder": "asc",
    }
    return fetch_json(url, params=params)


def ingest_usda() -> None:
    """Pull USDA FoodData Central foods and load into raw.usda_foods.

    Uses UPSERT on fdc_id for idempotency.
    """
    ensure_raw_schema()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()

    page = 1
    total_inserted = 0
    more_pages = True

    while more_pages:
        logger.info(f"Fetching USDA page {page}...")
        response = fetch_foods_page(page)

        foods = response.get("foods", [])
        if not foods:
            more_pages = False
            continue

        rows = [build_row(f) for f in foods]

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(UPSERT_SQL, rows)
                conn.commit()

        total_inserted += len(rows)
        total_pages = response.get("totalPages", 1)
        logger.info(f"  Page {page}/{total_pages}: {len(rows)} rows upserted")

        if page >= total_pages:
            more_pages = False
        page += 1

    logger.info(f"USDA ingestion complete: {total_inserted} total rows")


if __name__ == "__main__":
    ingest_usda()
