from datetime import datetime, timezone

import pytest

from app.astrology.features.siblings_communication_trajectory_v1 import analyze_siblings_communication_trajectory_v1

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


def test_trajectory_scores_are_bounded_and_patterned():
    result = analyze_siblings_communication_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in ("relationship_continuity_score", "communication_development_score", "initiative_skill_growth_score", "collaboration_score", "assertiveness_boundary_score", "adaptability_score"):
        assert 0.0 <= result[key] <= 1.0
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]


def test_trajectory_uses_all_lower_layers():
    result = analyze_siblings_communication_trajectory_v1(_chart(), NOW)
    assert result["timing_available"] is True
    assert result["events_available"] is True
    assert set(result["components"]) == {"natal", "timing", "events"}


def test_reality_override_prevents_manufactured_relationship_history():
    rule = analyze_siblings_communication_trajectory_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known sibling" in rule
    assert "must not manufacture" in rule
    assert "estrangement" in rule


def test_specific_person_outcomes_are_disallowed():
    text = analyze_siblings_communication_trajectory_v1(_chart(), NOW)["limitation"].lower()
    assert "whether a sibling exists" in text
    assert "intentions or loyalty" in text
    assert "reconciliation" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone"):
        analyze_siblings_communication_trajectory_v1(_chart(), datetime(2026, 8, 21))
