from datetime import datetime, timezone

import pytest

from app.astrology.features.family_children_timing_v1 import analyze_family_children_timing_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Venus"},
            "4": {"lord": "Moon"},
            "5": {"lord": "Jupiter"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Mars"},
            "11": {"lord": "Mercury"},
            "12": {"lord": "Sun"},
        },
        "planets": {
            "Venus": {"house": 4},
            "Moon": {"house": 5},
            "Jupiter": {"house": 9},
            "Saturn": {"house": 8},
            "Mars": {"house": 11},
            "Mercury": {"house": 2},
            "Sun": {"house": 12},
        },
        "dashas": {
            "mahadashas": [
                {
                    "planet": "Jupiter",
                    "start": "2022-01-01T00:00:00+00:00",
                    "end": "2028-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Moon", "start": "2022-01-01T00:00:00+00:00", "end": "2025-12-31T23:59:59+00:00"},
                        {"planet": "Saturn", "start": "2026-01-01T00:00:00+00:00", "end": "2028-12-31T23:59:59+00:00"},
                    ],
                },
                {
                    "planet": "Venus",
                    "start": "2029-01-01T00:00:00+00:00",
                    "end": "2033-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Jupiter", "start": "2029-01-01T00:00:00+00:00", "end": "2033-12-31T23:59:59+00:00"}
                    ],
                },
            ]
        },
    }


def _now():
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_nested_vimshottari_produces_past_present_future_windows():
    result = analyze_family_children_timing_v1(_chart(), _now())
    assert result["available"] is True
    assert result["past"]["available"] is True
    assert result["present"]["available"] is True
    assert result["future"]["available"] is True
    for bucket, key in (("past", "strongest_period"), ("present", "active_period"), ("future", "strongest_period")):
        period = result[bucket][key]
        assert 0.0 <= period["family_support_score"] <= 1.0
        assert 0.0 <= period["family_change_score"] <= 1.0


def test_historical_window_never_confirms_family_event():
    result = analyze_family_children_timing_v1(_chart(), _now())
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert historical["reality_override"] is True
    text = historical["rule"].lower()
    assert "must not be presented as proof" in text
    assert "pregnancy" in text
    assert "childbirth" in text


def test_language_retains_medical_and_fertility_boundary():
    result = analyze_family_children_timing_v1(_chart(), _now())
    text = result["limitation"].lower()
    assert "not fertility or medical advice" in text
    assert "does not predict or guarantee" in text


def test_requires_timezone_aware_reference_moment():
    with pytest.raises(ValueError):
        analyze_family_children_timing_v1(_chart(), datetime(2026, 8, 21))


def test_no_dasha_data_is_unavailable():
    chart = _chart()
    chart.pop("dashas")
    result = analyze_family_children_timing_v1(chart, _now())
    assert result["available"] is False
    assert "no usable dasha" in result["reason"].lower()
