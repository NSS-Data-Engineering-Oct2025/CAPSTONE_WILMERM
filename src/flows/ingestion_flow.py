"""Prefect flows for data ingestion from all sources."""

import subprocess
import sys
from pathlib import Path

from prefect import flow, task, get_run_logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"
DBT_BIN = Path(sys.executable).parent / ("dbt.exe" if sys.platform == "win32" else "dbt")


@task(retries=2, retry_delay_seconds=30)
def ingest_epa_task() -> None:
    """Run EPA AirNow ingestion."""
    from src.ingestion.epa_airnow import ingest_epa

    logger = get_run_logger()
    logger.info("Starting EPA AirNow ingestion")
    ingest_epa()
    logger.info("EPA AirNow ingestion complete")


@task(retries=2, retry_delay_seconds=60)
def ingest_cdc_task() -> None:
    """Run CDC Chronic Disease ingestion."""
    from src.ingestion.cdc_chronic import ingest_cdc

    logger = get_run_logger()
    logger.info("Starting CDC ingestion")
    ingest_cdc()
    logger.info("CDC ingestion complete")


@task(retries=2, retry_delay_seconds=60)
def ingest_usda_task() -> None:
    """Run USDA FoodData Central ingestion."""
    from src.ingestion.usda_fooddata import ingest_usda

    logger = get_run_logger()
    logger.info("Starting USDA ingestion")
    ingest_usda()
    logger.info("USDA ingestion complete")


@task(retries=2, retry_delay_seconds=30)
def ingest_census_task() -> None:
    """Run U.S. Census ingestion."""
    from src.ingestion.census import ingest_census

    logger = get_run_logger()
    logger.info("Starting Census ingestion")
    ingest_census()
    logger.info("Census ingestion complete")


@task(retries=1)
def ingest_blue_zones_task() -> None:
    """Run Blue Zones reference data ingestion."""
    from src.ingestion.blue_zones import ingest_blue_zones

    logger = get_run_logger()
    logger.info("Starting Blue Zones ingestion")
    ingest_blue_zones()
    logger.info("Blue Zones ingestion complete")


@task(retries=1, retry_delay_seconds=10)
def run_dbt_task(command: str) -> None:
    """Run a dbt command as a subprocess.

    Parameters
    ----------
    command : str
        The dbt sub-command to run (e.g. 'seed', 'run', 'test').
    """
    logger = get_run_logger()
    if not DBT_BIN.exists():
        raise RuntimeError(f"dbt executable not found at {DBT_BIN}")

    cmd = [str(DBT_BIN), command, "--profiles-dir", "."]
    logger.info(f"Running: dbt {command} (cwd={DBT_PROJECT_DIR})")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(DBT_PROJECT_DIR))

    if result.stdout:
        logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(f"dbt {command} failed with exit code {result.returncode}")

    logger.info(f"dbt {command} completed successfully")


@flow(name="epa-air-quality", log_prints=True)
def epa_flow() -> None:
    """Ingest EPA AirNow data and refresh dbt models."""
    ingest_epa_task()
    run_dbt_task("run")
    run_dbt_task("test")


@flow(name="cdc-chronic-disease", log_prints=True)
def cdc_flow() -> None:
    """Ingest CDC Chronic Disease data and refresh dbt models."""
    ingest_cdc_task()
    run_dbt_task("run")
    run_dbt_task("test")


@flow(name="usda-fooddata", log_prints=True)
def usda_flow() -> None:
    """Ingest USDA FoodData and refresh dbt models."""
    ingest_usda_task()
    run_dbt_task("run")
    run_dbt_task("test")


@flow(name="census-demographics", log_prints=True)
def census_flow() -> None:
    """Ingest Census demographics and refresh dbt models."""
    ingest_census_task()
    run_dbt_task("run")
    run_dbt_task("test")


@flow(name="full-pipeline", log_prints=True)
def full_pipeline_flow() -> None:
    """Run the complete ingestion and transformation pipeline.

    Ingests all 5 sources, then runs dbt seed, run, and test.
    """
    ingest_epa_task()
    ingest_cdc_task()
    ingest_usda_task()
    ingest_census_task()
    ingest_blue_zones_task()

    run_dbt_task("seed")
    run_dbt_task("run")
    run_dbt_task("test")


if __name__ == "__main__":
    full_pipeline_flow()
