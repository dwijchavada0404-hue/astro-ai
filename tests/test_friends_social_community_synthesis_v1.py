from datetime import datetime, timezone

import pytest

from app.astrology.features.friends_social_community_synthesis_v1 import analyze_friends_social_community_synthesis_v1

NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "5": {"lord": "Venus"}, "7": {"lord": "Moon"}, "9": {"lord": "Jupiter"}, "11": {"lord": "Saturn"}},
        "planets": {"Mercury": {"house": 3}, "Venus": {"house": 5}, "Moon": {"house": 7}, "Jupiter": {"house": 9}, "Saturn": {"house": 11}, "Rahu": {"house": 11}, "Sun": {"house": 9}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Venus"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Rahu"},
        ],
    }


def test_synthesis_scores_confidence_and_coverage_are_bounded():
    result = analyze_friends_social_community_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["component_coverage"] <= 1.0
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_exposes_outlook_and_strongest_area():
    result = analyze_friends_social_community_synthesis_v1(_chart(), NOW)
    assert result["outlook"]
    assert result["strongest_area"] in result["scores"]
    assert result["strongest_future_period"] is not None


def test_reality_override_prevents_manufactured_social_events():
    result = analyze_friends_social_community_synthesis_v1(_chart(), NOW)
    rule = result["historical_validation"]["rule"].lower()
    assert "known friendships" in rule
    assert "must never manufacture" in rule
    assert "betrayal" in rule


def test_specific_person_and_social_outcome_claims_are_disallowed():
    text = analyze_friends_social_community_synthesis_v1(_chart(), NOW)["limitation"].lower()
    assert "future friends or enemies" in text
    assert "trustworthiness" in text
    assert "betrayal" in text
    assert "guarantee popularity" in text


def test_timezone_is_required():
    with pytest.raises(ValueError, match="timezone"):
        analyze_friends_social_community_synthesis_v1(_chart(), datetime(2026, 8, 21))
