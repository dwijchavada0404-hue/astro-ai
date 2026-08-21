from datetime import datetime, timezone

import pytest

from app.astrology.features.property_home_timing_v1 import analyze_property_home_timing_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "4": {"lord": "Venus"},
            "9": {"lord": "Jupiter"},
            "11": {"lord": "Saturn"},
            "12": {"lord": "Rahu"},
        },
        "planets": {
            "Mercury": {"house": 2},
            "Mars": {"house": 3},
            "Venus": {"house": 4},
            "Jupiter": {"house": 9},
            "Saturn": {"house": 11},
            "Rahu": {"house": 12},
            "Moon": {"house": 4},
        },
        "dashas": {
            "mahadashas": [
                {
                    "planet": "Venus",
                    "start": "2021-01-01T00:00:00+00:00",
                    "end": "2028-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Mercury", "start": "2021-01-01T00:00:00+00:00", "end": "2024-12-31T23:59:59+00:00"},
                        {"planet": "Rahu", "start": "2025-01-01T00:00:00+00:00", "end": "2028-12-31T23:59:59+00:00"},
                    ],
                },
                {
                    "planet": "Jupiter",
                    "start": "2029-01-01T00:00:00+00:00",
                    "end": "2034-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Venus", "start": "2029-01-01T00:00:00+00:00", "end": "2032-12-31T23:59:59+00:00"}
                    ],
                },
            ]
        },
    }


def _now():
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_property_timing_supports_nested_vimshottari():
    result = analyze_property_home_timing_v1(_chart(), _now())
    assert result["available"] is True
    assert result["event"] == "property_home_timing"
    assert result["past"]["available"] is True
    assert result["present"]["available"] is True
    assert result["future"]["available"] is True


def test_property_timing_scores_are_bounded():
    result = analyze_property_home_timing_v1(_chart(), _now())
    periods = [
        result["past"]["strongest_period"],
        result["present"]["active_period"],
        result["future"]["strongest_period"],
    ]
    for period in periods:
        assert 0.0 <= period["home_property_support_score"] <= 1.0
        assert 0.0 <= period["relocation_activation_score"] <= 1.0


def test_past_window_remains_unconfirmed():
    result = analyze_property_home_timing_v1(_chart(), _now())
    assert result["past"]["historical_status"] == "unconfirmed"
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert historical["reality_override"] is True
    assert "unless the user confirms" in historical["rule"].lower()


def test_timing_does_not_claim_purchase_or_move():
    result = analyze_property_home_timing_v1(_chart(), _now())
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "not proof or probability" in text
    assert "does not predict or guarantee property purchase" in text


def test_timing_requires_timezone():
    with pytest.raises(ValueError):
        analyze_property_home_timing_v1(_chart(), datetime(2026, 8, 21))


def test_timing_rejects_invalid_horizon():
    with pytest.raises(ValueError):
        analyze_property_home_timing_v1(_chart(), _now(), lookback_years=0)


def test_timing_handles_missing_periods():
    chart = _chart()
    chart.pop("dashas")
    result = analyze_property_home_timing_v1(chart, _now())
    assert result["available"] is False
    assert "no usable dasha periods" in result["reason"].lower()
