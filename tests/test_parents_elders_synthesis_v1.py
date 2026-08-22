from datetime import datetime, timezone

import pytest

from app.astrology.features.parents_elders_synthesis_v1 import analyze_parents_elders_synthesis_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"4": {"lord": "Moon"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}}, "planets": {"Moon": {"house": 4}, "Jupiter": {"house": 9}, "Sun": {"house": 10}, "Saturn": {"house": 6}, "Mars": {"house": 3}, "Venus": {"house": 4}}, "dasha_periods": [{"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Jupiter"}, {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"}]}


def test_synthesis_scores_confidence_and_coverage_are_bounded():
    result = analyze_parents_elders_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["component_coverage"] <= 1.0
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_exposes_outlook_and_future_context():
    result = analyze_parents_elders_synthesis_v1(_chart(), NOW)
    assert result["outlook"]
    assert result["strongest_area"] in result["scores"]
    assert result["strongest_future_period"] is not None
    assert result["strongest_future_event"] is not None


def test_reality_override_prevents_manufactured_family_events():
    rule = analyze_parents_elders_synthesis_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known parent/elder relationships" in rule
    assert "must never manufacture" in rule
    assert "illness" in rule and "loss" in rule


def test_health_death_and_specific_person_claims_are_disallowed():
    text = analyze_parents_elders_synthesis_v1(_chart(), NOW)["limitation"].lower()
    assert "health" in text and "illness" in text
    assert "lifespan" in text and "death" in text
    assert "intentions or character" in text
    assert "reconciliation" in text and "caregiving" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_parents_elders_synthesis_v1(_chart(), datetime(2026, 8, 22))
