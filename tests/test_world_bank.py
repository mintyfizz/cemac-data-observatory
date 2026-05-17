from extract.world_bank import _normalize_observation


def test_normalize_observation_maps_world_bank_payload() -> None:
    row = _normalize_observation(
        {
            "countryiso3code": "CMR",
            "date": "2022",
            "value": 45.9,
            "indicator": {"id": "IT.NET.USER.ZS"},
            "unit": "",
            "obs_status": "",
            "decimal": 1,
        },
        fallback_indicator_code="FALLBACK",
    )

    assert row == {
        "country_code": "CMR",
        "indicator_code": "IT.NET.USER.ZS",
        "year": 2022,
        "value": 45.9,
        "unit": None,
        "obs_status": None,
        "decimal_places": 1,
    }


def test_normalize_observation_uses_fallback_indicator_code() -> None:
    row = _normalize_observation(
        {
            "countryiso3code": "GAB",
            "date": "2021",
            "value": 31.5,
            "indicator": {},
            "decimal": 0,
        },
        fallback_indicator_code="IT.CEL.SETS.P2",
    )

    assert row is not None
    assert row["indicator_code"] == "IT.CEL.SETS.P2"


def test_normalize_observation_skips_missing_required_fields() -> None:
    assert (
        _normalize_observation(
            {
                "countryiso3code": "TCD",
                "date": "2020",
                "value": None,
            },
            fallback_indicator_code="IT.NET.USER.ZS",
        )
        is None
    )
