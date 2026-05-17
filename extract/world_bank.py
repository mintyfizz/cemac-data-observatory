"""World Bank API extraction helpers."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator
from typing import Any

import requests

from .config import WB_BASE_URL

log = logging.getLogger(__name__)

PER_PAGE = 20_000
REQUEST_TIMEOUT = 30


def fetch_indicator(country_codes: Iterable[str], indicator_code: str) -> Iterator[dict[str, Any]]:
    """Yield normalized observations for one World Bank indicator.

    The World Bank API returns metadata and data as a two-element JSON array.
    This function hides pagination and maps the API fields into the
    raw.observations table shape.
    """
    countries = ";".join(country_codes)
    if not countries:
        return

    page = 1
    pages = 1
    session = requests.Session()

    while page <= pages:
        url = f"{WB_BASE_URL}/country/{countries}/indicator/{indicator_code}"
        params = {
            "format": "json",
            "per_page": PER_PAGE,
            "page": page,
        }
        response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, list) or len(payload) != 2:
            raise ValueError(f"Unexpected World Bank response for {indicator_code}: {payload!r}")

        metadata, observations = payload
        if isinstance(metadata, dict):
            pages = int(metadata.get("pages") or 1)

        if not observations:
            log.warning("No observations returned for %s on page %d", indicator_code, page)
            break

        for observation in observations:
            row = _normalize_observation(observation, indicator_code)
            if row is not None:
                yield row

        page += 1


def _normalize_observation(
    observation: dict[str, Any],
    fallback_indicator_code: str,
) -> dict[str, Any] | None:
    value = observation.get("value")
    year = observation.get("date")
    country_code = observation.get("countryiso3code")

    if value is None or year in (None, "") or country_code in (None, ""):
        return None

    indicator = observation.get("indicator") or {}

    return {
        "country_code": country_code,
        "indicator_code": indicator.get("id") or fallback_indicator_code,
        "year": int(year),
        "value": value,
        "unit": observation.get("unit") or None,
        "obs_status": observation.get("obs_status") or None,
        "decimal_places": observation.get("decimal"),
    }
