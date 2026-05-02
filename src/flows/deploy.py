"""Serve all Prefect flow deployments with their schedules.

Usage:
    uv run python -m src.flows.deploy

This starts a long-running process that schedules and executes flows locally.
Press Ctrl+C to stop.
"""

from prefect.runner import serve

from src.flows.ingestion_flow import (
    epa_flow,
    cdc_flow,
    usda_flow,
    census_flow,
    full_pipeline_flow,
)


def main() -> None:
    """Register and serve all flow deployments."""
    epa_deploy = epa_flow.to_deployment(
        name="epa-hourly",
        cron="0 * * * *",
        tags=["ingestion", "epa"],
    )
    cdc_deploy = cdc_flow.to_deployment(
        name="cdc-weekly",
        cron="0 6 * * 1",
        tags=["ingestion", "cdc"],
    )
    usda_deploy = usda_flow.to_deployment(
        name="usda-monthly",
        cron="0 6 1 * *",
        tags=["ingestion", "usda"],
    )
    census_deploy = census_flow.to_deployment(
        name="census-monthly",
        cron="0 6 15 * *",
        tags=["ingestion", "census"],
    )
    full_deploy = full_pipeline_flow.to_deployment(
        name="full-pipeline-daily",
        cron="0 5 * * *",
        tags=["ingestion", "full"],
    )

    serve(epa_deploy, cdc_deploy, usda_deploy, census_deploy, full_deploy)


if __name__ == "__main__":
    main()
