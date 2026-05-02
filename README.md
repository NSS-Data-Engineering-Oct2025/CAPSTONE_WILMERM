Environmental Health & Nutrition Data Platform

Data Engineering Capstone — Wilmer Saenz

A data platform that integrates air quality (EPA), nutrition (USDA), chronic disease (CDC), demographics (Census), and longevity benchmarks (Blue Zones) into a unified analytical layer. The pipeline ingests from multiple government APIs, transforms through a medallion architecture (dbt), and delivers clean data through interactive dashboards (Metabase).

Architecture

```
EPA AirNow API ──┐
USDA FoodData ───┤
CDC Indicators ──┼──> Python (HTTPX) ──> PostgreSQL ──> dbt ──> DuckDB/Duck Lake ──> Metabase
Census API ──────┤                        (raw)      (staging/   (presentation)    (dashboards)
Blue Zones ──────┘                                  intermediate/
                                                      marts)
```

Orchestration: Prefect
CI/CD: GitHub Actions

Tech Stack

- Python 3.12+ (HTTPX, psycopg2, loguru)
- PostgreSQL 16 (raw storage)
- dbt (transformations, testing)
- DuckDB / Duck Lake (analytical engine)
- Prefect (orchestration, scheduling, alerts)
- Metabase (BI dashboards)
- Docker Compose (local infrastructure)
- GitHub Actions (CI/CD, scheduled runs)

Quick Start

1. Clone the repo and copy the env file:
   ```
   git clone <repo-url>
   cd CAPSTONE_WILMERM
   cp .env.example .env
   ```
2. Edit .env with your API keys and database credentials.
3. Start PostgreSQL:
   ```
   docker compose up -d
   ```
4. Install dependencies:
   ```
   uv sync
   ```
5. Run the ingestion pipeline:
   ```
   uv run python -m src.ingestion.epa_airnow
   ```

Data Sources

- EPA AirNow API — air quality index, PM2.5, ozone (updates hourly)
- USDA FoodData Central — food nutrient composition (updates monthly)
- CDC Chronic Disease Indicators — diabetes, asthma, obesity rates by state (periodic)
- U.S. Census API — population and demographics by county/state
- Blue Zones — longevity and dietary reference data (static)
