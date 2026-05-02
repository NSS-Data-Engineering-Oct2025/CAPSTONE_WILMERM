Environmental Health & Nutrition Data Platform

Data Engineering Capstone — Wilmer Saenz

A data platform that integrates air quality (EPA), nutrition (USDA), chronic disease (CDC), demographics (Census), and longevity benchmarks (Blue Zones) into a unified analytical layer. The pipeline ingests from multiple government APIs on different schedules, transforms through a medallion architecture (dbt), exports to DuckDB/Parquet, and delivers clean data through interactive Metabase dashboards.


Architecture

```
                    ┌──────────────────────────────────────────────────────────────────┐
                    │                     Prefect Orchestration                        │
                    │          (EPA hourly, CDC weekly, USDA/Census monthly)           │
                    └──────────┬───────────────────────────────────────────┬────────────┘
                               │                                           │
                    ┌──────────▼──────────┐                    ┌───────────▼──────────┐
                    │   Data Ingestion    │                    │    Transformation     │
                    │   Python + HTTPX    │                    │        dbt            │
                    │                     │                    │                       │
                    │ EPA AirNow API      │                    │ Staging (5 views)     │
                    │ USDA FoodData API   │──> PostgreSQL ───> │ Intermediate (3)      │
                    │ CDC Socrata API     │      (raw)         │ Marts (2 tables)      │
                    │ Census API          │                    │ Tests (16)            │
                    │ Blue Zones (static) │                    │                       │
                    └─────────────────────┘                    └───────────┬────────────┘
                                                                          │
                                                               ┌──────────▼──────────┐
                                                               │   Presentation      │
                                                               │                     │
                                                               │ DuckDB + Parquet    │
                                                               │ Metabase dashboards │
                                                               └─────────────────────┘
```


Pipeline Flowchart

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────────┐     ┌──────────────┐
│  API Sources│────>│  Python Ingest   │────>│  PostgreSQL raw   │────>│  dbt staging │
│  (5 sources)│     │  (HTTPX + retry) │     │  (UPSERT/DELETE+  │     │  (5 views)   │
└─────────────┘     └──────────────────┘     │   INSERT)         │     └──────┬───────┘
                                              └───────────────────┘            │
                                                                               ▼
┌─────────────┐     ┌──────────────────┐     ┌───────────────────┐     ┌──────────────┐
│  Metabase   │<────│  DuckDB/Parquet  │<────│  dbt marts        │<────│  dbt inter-  │
│  dashboards │     │  (export)        │     │  (2 tables)       │     │  mediate (3) │
└─────────────┘     └──────────────────┘     └───────────────────┘     └──────────────┘
                                                      │
                                              ┌───────▼───────┐
                                              │  dbt tests    │
                                              │  (16 checks)  │
                                              └───────────────┘
```


Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| Language | Python 3.12+ | Ingestion scripts, orchestration |
| HTTP Client | HTTPX | API calls with retry + exponential backoff |
| Raw Storage | PostgreSQL 16 | Stores ingested data in its original form |
| Transformation | dbt-postgres | Staging, intermediate, and mart layers |
| Analytical Engine | DuckDB | Parquet-backed tables for fast analytics |
| Orchestration | Prefect | Scheduled flows with failure alerts |
| Dashboards | Metabase | Interactive visualizations |
| Infrastructure | Docker Compose | PostgreSQL + Metabase containers |
| CI/CD | GitHub Actions | Lint (ruff) + dbt test on push, scheduled pipeline |
| Package Manager | uv | Fast Python dependency management |


Data Sources

| Source | API | Update Frequency | Records |
| :--- | :--- | :--- | :--- |
| EPA AirNow | REST (JSON) | Hourly | ~14 observations/run |
| USDA FoodData Central | REST (JSON) | Monthly | ~8,000 foods |
| CDC Chronic Disease | Socrata API | Periodic | ~150,000 indicators |
| U.S. Census ACS | REST (JSON) | Annual | 52 states/territories |
| Blue Zones | Static dataset | One-time load | 5 zones |


dbt Model Lineage

```
raw.cdc_chronic_disease ──> stg_cdc_chronic_disease ──> int_disease_by_state ──┐
raw.epa_air_quality ──────> stg_epa_air_quality ──────> int_air_quality_summary─┼──> mart_health_overview
raw.census_demographics ──> stg_census_demographics ─────────────────────────────┘
raw.usda_foods ───────────> stg_usda_foods ───────────> int_nutrition_summary ──┐
raw.blue_zones ───────────> stg_blue_zones ─────────────────────────────────────┼──> mart_blue_zone_comparison
                                                                                 └
```


Quick Start

1. Clone the repo and copy the env file:

```bash
git clone <repo-url>
cd CAPSTONE_WILMERM
cp .env.example .env
```

2. Edit `.env` with your API keys and database credentials.

3. Start infrastructure (PostgreSQL + Metabase):

```bash
docker compose up -d
```

4. Install dependencies:

```bash
uv sync
```

5. Run the full ingestion pipeline:

```bash
uv run python -m src.flows.ingestion_flow
```

6. Or run individual sources:

```bash
uv run python -m src.ingestion.epa_airnow
uv run python -m src.ingestion.cdc_chronic
uv run python -m src.ingestion.usda_fooddata
uv run python -m src.ingestion.census
uv run python -m src.ingestion.blue_zones
```

7. Run dbt transformations:

```bash
cd dbt_project
uv run dbt seed --profiles-dir .
uv run dbt run --profiles-dir .
uv run dbt test --profiles-dir .
```

8. Export marts to DuckDB/Parquet:

```bash
uv run python -m src.export_to_duckdb
```

9. Access Metabase at http://localhost:3000 and connect to PostgreSQL (`postgres:5432`, database `health_platform`).


Project Structure

```
CAPSTONE_WILMERM/
├── .github/workflows/       CI/CD pipelines (lint, test, scheduled runs)
├── dbt_project/
│   ├── models/
│   │   ├── staging/         5 staging views (one per source)
│   │   ├── intermediate/    3 intermediate views (joins, aggregations)
│   │   └── marts/           2 mart tables (health overview, blue zones)
│   ├── seeds/               state_lookup.csv for geographic joins
│   ├── profiles.yml         PostgreSQL connection config
│   └── dbt_project.yml      dbt project config
├── src/
│   ├── ingestion/           One script per data source
│   │   ├── http_client.py   Shared HTTP client with retry logic
│   │   ├── epa_airnow.py
│   │   ├── cdc_chronic.py
│   │   ├── usda_fooddata.py
│   │   ├── census.py
│   │   └── blue_zones.py
│   ├── flows/               Prefect orchestration
│   │   ├── ingestion_flow.py  Flow definitions + tasks
│   │   └── deploy.py         Deployment with schedules
│   ├── config.py            Centralized env-var configuration
│   ├── db.py                PostgreSQL connection utilities
│   └── export_to_duckdb.py  Export marts to DuckDB + Parquet
├── docker-compose.yml       PostgreSQL + Metabase
├── pyproject.toml           Dependencies (managed with uv)
└── .env.example             Template for environment variables
```


Requirements Coverage

| Requirement | Implementation |
| :--- | :--- |
| Changing data | EPA updates hourly, USDA monthly, CDC periodically |
| Automated scheduled pipeline | Prefect flows with cron schedules + GitHub Actions |
| Multiple datasets with cleaning | 5 sources joined by geography through dbt |
| Transformation layers | dbt staging, intermediate, marts (medallion) |
| Testing and monitoring | 16 dbt tests + Prefect retries and failure logging |
| Organized GitHub | Structured repo, regular commits, CI/CD |
| Pipeline flowchart | Architecture and lineage diagrams above |
| Informative README | This document |
| No PII | All data is public/government sourced |
| GitHub Actions | CI (lint + test) + scheduled pipeline workflows |
| Presentation | Slide deck + Metabase dashboard |
