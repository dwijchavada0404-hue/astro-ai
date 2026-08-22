from datetime import datetime, timezone

import pytest

from app.astrology.features.siblings_communication_synthesis_v1 import analyze_siblings_communication_synthesis_v1

NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"}, "7": {"lord": "Venus"}, "11": {"lord": "Moon"}},
        "planets": {"Mercury": {"house": 3}, "Mars": {"house": 6}, "Jupiter": {"house": 5}, "Venus": {"house": 7}, "Moon": {"house": 11}, "Saturn": {"house": 3}, "Sun": {"house": 10}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Venus", "sub_lord": "Moon"},
        ],
    }


def test_synthesis_scores_confidence_and_coverage_are_bounded():
    result = analyze_siblings_communication_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["component_coverage"] <= 1.0
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_exposes_outlook_and_future_context():
    result = analyze_siblings_communication_synthesis_v1(_chart(), NOW)
    assert result["outlook"]
    assert result["strongest_area"] in result["scores"]
    assert result["strongest_future_period"] is not None
    assert result["strongest_future_event"] is not None


def test_reality_override_prevents_manufactured_sibling_events():
    rule = analyze_siblings_communication_synthesis_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known sibling" in rule
    assert "must never manufacture" in rule
    assert "reconciliation" in rule


def test_specific_person_and_outcome_claims_are_disallowed():
    text = analyze_siblings_communication_synthesis_v1(_chart(), NOW)["limitation"].lower()
    assert "whether a sibling exists" in text
    assert "intentions or loyalty" in text
    assert "estrangement" in text
    assert "guarantee communication" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone"):
        analyze_siblings_communication_synthesis_v1(_chart(), datetime(2026, 8, 21))
