from datetime import datetime, timezone

import pytest

from app.astrology.features.education_learning_synthesis_v1 import analyze_education_learning_synthesis_v1


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "4": {"lord": "Moon"}, "5": {"lord": "Jupiter"}, "8": {"lord": "Saturn"}, "9": {"lord": "Mars"}},
        "planets": {"Mercury": {"house": 5}, "Moon": {"house": 4}, "Jupiter": {"house": 9}, "Saturn": {"house": 8}, "Mars": {"house": 3}, "Venus": {"house": 5}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Mars"},
        ],
    }


def test_synthesis_is_available_and_bounded():
    result = analyze_education_learning_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["component_coverage"] == 1.0
    assert result["strongest_area"] in result["scores"]
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_keeps_learning_dimensions_separate():
    result = analyze_education_learning_synthesis_v1(_chart(), NOW)
    assert set(result["scores"]) == {"study_continuity", "higher_education", "skill_development", "research_depth", "learning_adaptability"}
    assert result["strongest_future_period"] is not None


def test_known_education_reality_overrides_predictions():
    result = analyze_education_learning_synthesis_v1(_chart(), NOW)
    rule = result["historical_validation"]["rule"].lower()
    assert "known education history" in rule
    assert "must never manufacture" in rule


def test_missing_chart_is_unavailable():
    result = analyze_education_learning_synthesis_v1({}, NOW)
    assert result["available"] is False
    assert result["event"] == "education_learning_synthesis"


def test_timezone_required_and_outcome_guarantees_disallowed():
    with pytest.raises(ValueError, match="timezone"):
        analyze_education_learning_synthesis_v1(_chart(), datetime(2026, 8, 21))
    text = analyze_education_learning_synthesis_v1(_chart(), NOW)["limitation"].lower()
    assert "does not guarantee" in text
    assert "admission" in text
    assert "examination success" in text
    assert "employment outcomes" in text
