from datetime import datetime, timezone

import pytest

from app.astrology.features.friends_social_community_timing_v1 import analyze_friends_social_community_timing_v1

NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "5": {"lord": "Venus"}, "6": {"lord": "Saturn"}, "7": {"lord": "Moon"}, "8": {"lord": "Mars"}, "9": {"lord": "Jupiter"}, "11": {"lord": "Sun"}, "12": {"lord": "Ketu"}},
        "planets": {"Mercury": {"house": 11}, "Venus": {"house": 7}, "Saturn": {"house": 6}, "Moon": {"house": 5}, "Mars": {"house": 8}, "Jupiter": {"house": 9}, "Sun": {"house": 11}, "Rahu": {"house": 3}, "Ketu": {"house": 12}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Venus"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Saturn"},
        ],
    }


def test_timing_has_past_present_future_without_claiming_social_events():
    result = analyze_friends_social_community_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["available"] and result["present"]["available"] and result["future"]["available"]
    assert result["past"]["historical_status"] == "unconfirmed"
    assert "not proof" in result["historical_validation"]["rule"].lower()


def test_timing_dimensions_are_separate_and_bounded():
    future = analyze_friends_social_community_timing_v1(_chart(), NOW)["future"]["strongest_period"]
    for key in ("friendship_support_score", "networking_support_score", "community_support_score", "boundary_selectivity_score"):
        assert 0.0 <= future[key] <= 1.0


def test_no_dashas_is_unavailable():
    chart = _chart(); chart.pop("dasha_periods")
    result = analyze_friends_social_community_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()


def test_timezone_and_bounds_are_enforced():
    with pytest.raises(ValueError, match="timezone"):
        analyze_friends_social_community_timing_v1(_chart(), datetime(2026, 8, 21))
    with pytest.raises(ValueError):
        analyze_friends_social_community_timing_v1(_chart(), NOW, lookahead_years=11)


def test_specific_person_and_betrayal_claims_are_disallowed():
    text = analyze_friends_social_community_timing_v1(_chart(), NOW)["limitation"].lower()
    assert "specific person" in text
    assert "trustworthy" in text
    assert "betrayal" in text
    assert "not a probability or guarantee" in text
