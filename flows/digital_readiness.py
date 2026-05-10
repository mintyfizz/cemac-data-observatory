"""Prefect orchestration for the digital readiness pipeline."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from prefect import flow, get_run_logger, task
from prefect.tasks import exponential_backoff

from extract.config import ALL_COUNTRIES, INDICATORS
from extract.load import load_observations
from extract.world_bank import fetch_indicator

PROJECT_ROOT = Path(__file__).parent.parent


def _conn_str() -> str:
    return (
        f"host={os.environ['POSTGRES_HOST']} "
        f"port={os.environ['POSTGRES_PORT']} "
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']}"
    )


@task(
    name="extract-indicator",
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    retry_jitter_factor=0.5,
    timeout_seconds=120,
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


@flow(name="digital-readiness-pipeline", log_prints=True)
def digital_readiness_pipeline() -> dict:
    """Extract World Bank indicators into the raw warehouse schema."""
    load_dotenv(PROJECT_ROOT / ".env")
    log = get_run_logger()

    country_codes = list(ALL_COUNTRIES)
    log.info(
        "Pipeline starting: %d countries x %d indicators",
        len(country_codes),
        len(INDICATORS),
    )

    totals = [
        extract_one_indicator(code, name, country_codes)
        for code, name in INDICATORS.items()
    ]
    grand_total = sum(totals)
    log.info("Extraction complete. %d total rows processed.", grand_total)

    log.info("Pipeline complete.")
    return {"rows_processed": grand_total, "indicators_processed": len(totals)}


if __name__ == "__main__":
    digital_readiness_pipeline()
