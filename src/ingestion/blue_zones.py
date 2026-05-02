"""Ingest Blue Zones reference data into PostgreSQL.

This is a static dataset loaded once for comparison purposes.
Source: curated from Blue Zones research (Buettner, 2008).
"""

import json

from loguru import logger

from src.db import get_connection, ensure_raw_schema

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw.blue_zones (
    zone_name         TEXT PRIMARY KEY,
    country           TEXT,
    region            TEXT,
    avg_life_expectancy DOUBLE PRECISION,
    diet_description  TEXT,
    key_foods         JSONB,
    plant_based_pct   INTEGER,
    physical_activity TEXT,
    social_factors    TEXT,
    ingested_at       TIMESTAMPTZ DEFAULT NOW()
);
"""

UPSERT_SQL = """
INSERT INTO raw.blue_zones (
    zone_name, country, region, avg_life_expectancy, diet_description,
    key_foods, plant_based_pct, physical_activity, social_factors
) VALUES (
    %(zone_name)s, %(country)s, %(region)s, %(avg_life_expectancy)s, %(diet_description)s,
    %(key_foods)s, %(plant_based_pct)s, %(physical_activity)s, %(social_factors)s
)
ON CONFLICT (zone_name) DO UPDATE SET
    country = EXCLUDED.country,
    region = EXCLUDED.region,
    avg_life_expectancy = EXCLUDED.avg_life_expectancy,
    diet_description = EXCLUDED.diet_description,
    key_foods = EXCLUDED.key_foods,
    plant_based_pct = EXCLUDED.plant_based_pct,
    physical_activity = EXCLUDED.physical_activity,
    social_factors = EXCLUDED.social_factors,
    ingested_at = NOW();
"""

BLUE_ZONES_DATA = [
    {
        "zone_name": "Okinawa",
        "country": "Japan",
        "region": "East Asia",
        "avg_life_expectancy": 84.0,
        "diet_description": "Plant-based with tofu, sweet potatoes, and green vegetables. Very low calorie intake following hara hachi bu (eat until 80% full).",
        "key_foods": json.dumps(["sweet potatoes", "tofu", "bitter melon", "turmeric", "green tea", "seaweed"]),
        "plant_based_pct": 96,
        "physical_activity": "Daily gardening, walking, and martial arts",
        "social_factors": "Strong community bonds (moai), sense of purpose (ikigai)",
    },
    {
        "zone_name": "Sardinia",
        "country": "Italy",
        "region": "Mediterranean",
        "avg_life_expectancy": 83.0,
        "diet_description": "Mediterranean diet heavy on whole grains, beans, garden vegetables, and local cheese. Moderate red wine (Cannonau).",
        "key_foods": json.dumps(["fava beans", "whole grain bread", "tomatoes", "almonds", "goat milk", "red wine"]),
        "plant_based_pct": 85,
        "physical_activity": "Shepherding, walking hilly terrain daily",
        "social_factors": "Multigenerational households, strong family ties, community laughter",
    },
    {
        "zone_name": "Nicoya Peninsula",
        "country": "Costa Rica",
        "region": "Central America",
        "avg_life_expectancy": 82.5,
        "diet_description": "Traditional Mesoamerican diet based on beans, corn, squash, and tropical fruits.",
        "key_foods": json.dumps(["black beans", "corn tortillas", "squash", "papaya", "eggs", "rice"]),
        "plant_based_pct": 80,
        "physical_activity": "Physical labor, farming, daily walking",
        "social_factors": "Plan de vida (sense of purpose), faith-based community, strong family networks",
    },
    {
        "zone_name": "Ikaria",
        "country": "Greece",
        "region": "Mediterranean",
        "avg_life_expectancy": 83.0,
        "diet_description": "Mediterranean diet with wild greens, legumes, potatoes, and herbal teas. Very low refined sugar.",
        "key_foods": json.dumps(["wild greens", "lentils", "potatoes", "feta cheese", "herbal tea", "honey"]),
        "plant_based_pct": 90,
        "physical_activity": "Farming, gardening, walking steep terrain",
        "social_factors": "Afternoon naps, communal meals, no sense of time pressure",
    },
    {
        "zone_name": "Loma Linda",
        "country": "United States",
        "region": "North America",
        "avg_life_expectancy": 83.0,
        "diet_description": "Seventh-day Adventist vegetarian diet. Emphasis on nuts, legumes, whole grains, and fresh produce. No alcohol or tobacco.",
        "key_foods": json.dumps(["nuts", "oats", "avocados", "beans", "soy milk", "whole wheat bread"]),
        "plant_based_pct": 95,
        "physical_activity": "Regular moderate exercise, hiking, community sports",
        "social_factors": "Sabbath rest, faith community, volunteerism, no smoking or alcohol",
    },
]


def ingest_blue_zones() -> None:
    """Load Blue Zones reference data into raw.blue_zones.

    Uses UPSERT on zone_name for idempotency.
    """
    ensure_raw_schema()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT_SQL, BLUE_ZONES_DATA)
            conn.commit()

    logger.info(f"Blue Zones ingestion complete: {len(BLUE_ZONES_DATA)} zones loaded")


if __name__ == "__main__":
    ingest_blue_zones()
