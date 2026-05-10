"""Prefect orchestration for the digital readiness pipeline."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from prefect import flow, get_run_logger, task
from prefect.tasks import exponential_backoff

from extract.config import ALL_COUNTRIES, INDICATORS
from extract.load import load_observations
from extract.world_bank import fetch_indicator

PROJECT_ROOT = Path(__file__).parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"


def _conn_str() -> str:
    return (
        f"host={os.environ['POSTGRES_HOST']} "
        f"port={os.environ['POSTGRES_PORT']} "
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']}"
    )


def _dbt_command() -> list[str]:
    dbt_on_path = shutil.which("dbt")
    if dbt_on_path:
        return [dbt_on_path, "build"]

    dbt_next_to_python = Path(sys.executable).with_name("dbt")
    if dbt_next_to_python.exists():
        return [str(dbt_next_to_python), "build"]

    return ["dbt", "build"]


@task(
    name="extract-indicator",
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    retry_jitter_factor=0.5,
    timeout_seconds=120,
    tags=["world-bank"],
)
def extract_one_indicator(
    indicator_code: str,
    indicator_name: str,
    country_codes: list[str],
) -> int:
    """Fetch one indicator across all countries and upsert into raw."""
    log = get_run_logger()
    log.info("Fetching %s - %s", indicator_code, indicator_name)
    rows = list(fetch_indicator(country_codes, indicator_code))
    n = load_observations(_conn_str(), rows)
    log.info("Upserted %d rows for %s", n, indicator_code)
    return n


@task(name="dbt-build", retries=1, timeout_seconds=600)
def run_dbt_build() -> None:
    """Run dbt build as a subprocess, streaming output to Prefect logs."""
    log = get_run_logger()
    log.info("Running dbt build in %s", DBT_PROJECT_DIR)
    result = subprocess.run(
        _dbt_command(),
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    log.info(result.stdout)
    if result.returncode != 0:
        log.error(result.stderr)
        raise RuntimeError(f"dbt build failed with exit code {result.returncode}")


@flow(name="digital-readiness-pipeline", log_prints=True)
def digital_readiness_pipeline() -> dict:
    """End-to-end: parallel extraction across indicators, then dbt build."""
    load_dotenv(PROJECT_ROOT / ".env")
    log = get_run_logger()

    country_codes = list(ALL_COUNTRIES)
    log.info(
        "Pipeline starting: %d countries x %d indicators",
        len(country_codes),
        len(INDICATORS),
    )

    futures = [
        extract_one_indicator.submit(code, name, country_codes)
        for code, name in INDICATORS.items()
    ]
    totals = [f.result() for f in futures]
    grand_total = sum(totals)
    log.info("Extraction complete. %d total rows processed.", grand_total)

    run_dbt_build()

    log.info("Pipeline complete.")
    return {"rows_processed": grand_total, "indicators_processed": len(totals)}


if __name__ == "__main__":
    digital_readiness_pipeline()
