Project Title: Environmental Health & Nutrition Data Platform

Executive Summary

This project builds a data platform that integrates air quality, nutrition, and chronic disease data to provide a unified view of environmental and dietary health factors across the United States, with a focus on Tennessee. The pipeline ingests data from multiple government APIs at different frequencies, transforms it through a medallion architecture, and delivers clean, joined datasets ready for analysis through an interactive dashboard.

Data Sources

- EPA AirNow API — Real-time air quality index (AQI), PM2.5, and ozone readings by geographic area.
- USDA FoodData Central API — Nutritional composition of foods (calories, macros, micronutrients).
- CDC Chronic Disease Indicators (Socrata API) — 115 indicators including diabetes, asthma, and obesity rates by state.
- U.S. Census API — Population, income, and demographics by county/state for normalization.
- Blue Zones Reference Data — Longevity and dietary patterns from the world's longest-lived populations (static/Kaggle).

Technical Architecture

| Technology | Role | Purpose |
| :--- | :--- | :--- |
| Python (HTTPX) | Data Ingestion | Fetch data from APIs and download CSV/JSON files on schedule |
| PostgreSQL | Raw Storage | Stores ingested data in its original form |
| dbt | Data Transformation | Cleans, joins, and models data through staging, intermediate, and marts layers |
| DuckDB / Duck Lake | Analytical Engine | High-performance query engine for the presentation layer |
| Prefect | Orchestration | Automates and schedules the pipeline at different intervals per source |
| Metabase | BI & Visualization | Interactive dashboards showing health factors by geography |

Project Workflow

1. Ingestion — Prefect orchestrates Python scripts that pull data from EPA (hourly), USDA (monthly), CDC (periodic), and Census APIs into PostgreSQL.
2. Transformation — dbt models clean, standardize, and join the datasets by geography (state/county), creating staging, intermediate, and marts layers.
3. Presentation — Mart tables are available in DuckDB/Duck Lake. Metabase connects to provide dashboards showing air quality, disease rates, and nutrition data side by side.
4. Monitoring — Pipeline includes dbt tests, alerts on failure, and logging through Prefect.

Stakeholder Value

- Public Health Analysts — Access integrated environmental and health data by region without writing SQL.
- Researchers — Compare U.S. regional health factors against Blue Zone benchmarks.
- Policy Makers — Explore relationships between air quality, dietary patterns, and chronic disease prevalence across states.
