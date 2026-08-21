from datetime import datetime, timezone

import pytest

from app.astrology.features.friends_social_community_trajectory_v1 import analyze_friends_social_community_trajectory_v1

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


def test_trajectory_scores_are_bounded():
    result = analyze_friends_social_community_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in ("friendship_depth_score", "social_breadth_score", "community_orientation_score", "collaboration_score", "selectivity_boundary_score", "social_adaptability_score"):
        assert 0.0 <= result[key] <= 1.0


def test_trajectory_pattern_and_direction_are_explicit():
    result = analyze_friends_social_community_trajectory_v1(_chart(), NOW)
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]
    assert result["timing_available"] is True
    assert result["events_available"] is True


def test_known_social_history_overrides_symbolic_trajectory():
    result = analyze_friends_social_community_trajectory_v1(_chart(), NOW)
    rule = result["historical_validation"]["rule"].lower()
    assert "known friendships" in rule
    assert "must not manufacture" in rule


def test_specific_people_and_social_outcomes_are_not_predicted():
    text = analyze_friends_social_community_trajectory_v1(_chart(), NOW)["limitation"].lower()
    assert "who will become a friend" in text
    assert "loyal or trustworthy" in text
    assert "betrayal/conflict" in text
    assert "popular" in text


def test_timezone_is_required():
    with pytest.raises(ValueError, match="timezone"):
        analyze_friends_social_community_trajectory_v1(_chart(), datetime(2026, 8, 21))
