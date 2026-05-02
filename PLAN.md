Project Plan — Environmental Health & Nutrition Data Platform

Timeline: May 2 - May 29, 2026 (4 weeks)


Week 1 — Foundation (May 2-8)
Goal: Repo setup + all data sources confirmed + first ingestion scripts working.
Deadline: Walkthrough with instructor on 5/9.

- Set up repo structure, pyproject.toml, .env.example, .gitignore, docker-compose (Postgres)
- Register for API keys: EPA AirNow, USDA FoodData Central, Census (data.gov key)
- Write ingestion scripts (one per source):
  - EPA AirNow — fetch current AQI observations by state/zip
  - USDA FoodData Central — search and fetch food nutrient data
  - CDC Chronic Disease Indicators — pull via Socrata API
  - Census — population and demographics by county/state
  - Blue Zones — download static dataset from Kaggle
- Each script lands raw data into PostgreSQL (bronze/raw schema)
- Confirm all 5 sources return data and load into Postgres
- Commit after each source is working

Walkthrough deliverable (5/9): Show the instructor raw data from all 5 sources in Postgres. Walk through the architecture diagram. Does not need to be polished.


Week 2 — Transformation + Orchestration (May 9-15)
Goal: dbt models running + Prefect orchestrating the pipeline end-to-end.
Deadline: Practice presentation on 5/16.

- Set up dbt project with Postgres adapter
- Build dbt models:
  - Staging — one model per source, light cleaning, rename columns, cast types
  - Intermediate — join datasets by geography (state/county FIPS codes), normalize with Census population data
  - Marts — final tables grouped by use case:
    - mart_air_quality — AQI trends by geography and time
    - mart_disease_rates — chronic disease prevalence by state
    - mart_nutrition_profile — food nutrient summaries
    - mart_health_overview — combined view joining air, disease, and nutrition by state
- Add dbt tests (not null, unique, accepted values, relationships)
- Set up Prefect:
  - Create flows that run each ingestion script
  - Schedule EPA flow (hourly or daily for demo purposes)
  - Schedule USDA/CDC/Census flows (weekly/monthly)
  - Add failure alerts (Prefect notifications)
- Commit after dbt models pass tests and Prefect runs successfully

Practice presentation deliverable (5/16): Have a slide deck ready. Show pipeline running end-to-end. 85-87% complete.


Week 3 — Presentation Layer + Polish (May 16-22)
Goal: DuckDB/Duck Lake serving data + Metabase dashboard + GitHub Actions.

- Set up DuckDB / Duck Lake:
  - Move mart tables from Postgres into Duck Lake (Parquet storage)
  - Catalog in Postgres to avoid DuckDB file concurrency issues (lesson from P4)
- Set up Metabase:
  - Connect to DuckDB/Duck Lake or Postgres marts
  - Build dashboard with 4-6 visualizations:
    - Map or bar chart of AQI by state
    - Disease rates by state (diabetes, asthma, obesity)
    - Nutrition data summary
    - Combined health factors view
- GitHub Actions:
  - CI workflow: lint (ruff) + dbt test on every push
  - Scheduled workflow: run ingestion pipeline on a cron
- Write README with architecture diagram, setup instructions, tech choices
- Create pipeline flowchart (requirement)
- Commit frequently

Deliverable: Working dashboard, automated CI/CD, clean repo.


Week 4 — Presentation + Demo Day (May 23-29)
Goal: Slide deck polished, rehearsed, and ready for 10 minutes.

- Build slide deck (10 slides max, following reference structure):
  1. Title + name
  2. Project motivation — why this data, why it matters
  3. Data sources — the 5 sources with volume/frequency details
  4. Architecture diagram — full pipeline flow
  5. Tech stack — what was used and why each was chosen
  6. Demo/screenshots — dashboard, Prefect runs, dbt lineage
  7. Challenges and solutions — what broke and how it was fixed
  8. Key features — what the platform offers
  9. What I learned / future improvements
  10. Questions
- Take screenshots of everything working (Prefect dashboard, dbt runs, Metabase charts)
- Rehearse to stay under 10 minutes
- 5/27 — Graduation
- 5/29 — Demo Day

Deliverable: Polished presentation, all screenshots captured, pipeline running.


Requirements Checklist

| Requirement | How it's covered |
| :--- | :--- |
| Data that changes | EPA updates hourly, USDA monthly, CDC periodically |
| Automated pipeline on schedule | Prefect flows with scheduled runs |
| Multiple datasets with cleaning/integration | 5 sources joined by geography |
| Data cleaning, transformation, presentation layers | dbt staging/intermediate/marts |
| Testing and monitoring with alerts | dbt tests + Prefect failure notifications |
| Organized GitHub with regular commits | Commit after each milestone |
| Pipeline flowchart | Architecture diagram in README |
| Informative README | Setup instructions, tech choices, architecture |
| No PII | All data is public/government sourced |
| GitHub Actions deployment | CI (lint + test) + scheduled pipeline runs |
| Presentation in approved medium | Slide deck + Metabase dashboard |


Stretch Goals (if time permits)

- Add MotherDuck as cloud option for Duck Lake
- Add FastAPI endpoint to query mart tables programmatically
- Add Soda or Great Expectations for additional data quality checks
- Blue Zones comparison dashboard page
- Historical trend analysis (air quality over months)
