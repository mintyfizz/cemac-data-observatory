"""Idempotent loader for raw.observations."""

from __future__ import annotations

import logging
from typing import Iterable

import psycopg

log = logging.getLogger(__name__)

UPSERT_SQL = """
INSERT INTO raw.observations
    (country_code, indicator_code, year, value, unit, obs_status, decimal_places, loaded_at)
VALUES
    (%(country_code)s, %(indicator_code)s, %(year)s, %(value)s,
     %(unit)s, %(obs_status)s, %(decimal_places)s, now())
ON CONFLICT (country_code, indicator_code, year) DO UPDATE SET
    value          = EXCLUDED.value,
    unit           = EXCLUDED.unit,
    obs_status     = EXCLUDED.obs_status,
    decimal_places = EXCLUDED.decimal_places,
    loaded_at      = EXCLUDED.loaded_at;
"""


def load_observations(conn_str: str, rows: Iterable[dict], batch_size: int = 500) -> int:
    """Upsert rows in batches. Returns total rows processed."""
    total = 0
    batch: list[dict] = []
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            for row in rows:
                batch.append(row)
                if len(batch) >= batch_size:
                    cur.executemany(UPSERT_SQL, batch)
                    total += len(batch)
                    log.info("Upserted %d rows (total %d)", len(batch), total)
                    batch.clear()
            if batch:
                cur.executemany(UPSERT_SQL, batch)
                total += len(batch)
                log.info("Upserted final %d rows (total %d)", len(batch), total)
        conn.commit()
    return total
