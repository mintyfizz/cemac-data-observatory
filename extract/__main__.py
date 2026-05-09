"""Run with: python -m extract"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

from .config import ALL_COUNTRIES, INDICATORS
from .load import load_observations
from .world_bank import fetch_indicator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("extract")


def main() -> None:
    load_dotenv()
    conn_str = (
        f"host={os.environ['POSTGRES_HOST']} "
        f"port={os.environ['POSTGRES_PORT']} "
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']}"
    )

    country_codes = list(ALL_COUNTRIES)
    grand_total = 0

    for indicator_code, indicator_name in INDICATORS.items():
        log.info("=" * 60)
        log.info("Indicator: %s — %s", indicator_code, indicator_name)
        rows = fetch_indicator(country_codes, indicator_code)
        n = load_observations(conn_str, rows)
        log.info("Loaded %d rows for %s", n, indicator_code)
        grand_total += n

    log.info("=" * 60)
    log.info("Done. Total rows processed: %d", grand_total)


if __name__ == "__main__":
    main()
