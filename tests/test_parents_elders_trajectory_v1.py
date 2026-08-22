from datetime import datetime, timezone

import pytest

from app.astrology.features.parents_elders_trajectory_v1 import analyze_parents_elders_trajectory_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"4": {"lord": "Moon"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}}, "planets": {"Moon": {"house": 4}, "Jupiter": {"house": 9}, "Sun": {"house": 10}, "Saturn": {"house": 6}, "Mars": {"house": 3}, "Venus": {"house": 4}}, "dasha_periods": [{"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Jupiter"}, {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"}]}


def test_trajectory_scores_are_bounded():
    result = analyze_parents_elders_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in ("support_continuity_score", "guidance_development_score", "responsibility_score", "independence_boundary_score", "family_continuity_score", "adaptability_score"):
        assert 0.0 <= result[key] <= 1.0
    assert result["trajectory_pattern"] and result["near_term_direction"]


def test_trajectory_uses_lower_layers():
    result = analyze_parents_elders_trajectory_v1(_chart(), NOW)
    assert result["timing_available"] is True and result["events_available"] is True
    assert set(result["components"]) == {"natal", "timing", "events"}


def test_reality_override_blocks_manufactured_family_events():
    rule = analyze_parents_elders_trajectory_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known parent/elder relationships" in rule
    assert "must not manufacture" in rule
    assert "illness" in rule and "loss" in rule


def test_health_lifespan_and_relationship_outcomes_are_disallowed():
    text = analyze_parents_elders_trajectory_v1(_chart(), NOW)["limitation"].lower()
    assert "health" in text and "illness" in text
    assert "lifespan" in text and "death" in text
    assert "reconciliation" in text and "caregiving" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_parents_elders_trajectory_v1(_chart(), datetime(2026, 8, 22))
