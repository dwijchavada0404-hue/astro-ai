from datetime import datetime, timezone

import pytest

from app.astrology.features.purpose_personal_growth_trajectory_v1 import analyze_purpose_personal_growth_trajectory_v1

NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"1": {"lord": "Sun"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"}, "9": {"lord": "Mercury"}, "10": {"lord": "Mars"}, "11": {"lord": "Venus"}, "12": {"lord": "Moon"}},
        "planets": {"Sun": {"house": 10}, "Jupiter": {"house": 9}, "Saturn": {"house": 6}, "Mercury": {"house": 5}, "Mars": {"house": 10}, "Venus": {"house": 11}, "Moon": {"house": 12}, "Ketu": {"house": 9}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
        ],
    }


def test_trajectory_scores_are_bounded():
    result = analyze_purpose_personal_growth_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in ("self_authorship_score", "contribution_orientation_score", "meaning_guidance_score", "creative_expression_score", "inner_development_score", "integration_score"):
        assert 0.0 <= result[key] <= 1.0


def test_trajectory_pattern_and_direction_are_explicit():
    result = analyze_purpose_personal_growth_trajectory_v1(_chart(), NOW)
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]
    assert result["timing_available"] is True
    assert result["events_available"] is True


def test_reality_overrides_symbolic_trajectory():
    result = analyze_purpose_personal_growth_trajectory_v1(_chart(), NOW)
    rule = result["historical_validation"]["rule"].lower()
    assert "known values" in rule
    assert "must not manufacture" in rule


def test_timezone_is_required():
    with pytest.raises(ValueError, match="timezone"):
        analyze_purpose_personal_growth_trajectory_v1(_chart(), datetime(2026, 8, 21))


def test_fixed_destiny_and_spiritual_claims_are_disallowed():
    text = analyze_purpose_personal_growth_trajectory_v1(_chart(), NOW)["limitation"].lower()
    assert "fixed destiny" in text
    assert "singular life purpose" in text
    assert "spiritual attainment" in text
    assert "mandatory vocation" in text
