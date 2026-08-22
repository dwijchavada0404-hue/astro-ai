from datetime import datetime, timezone

from app.astrology.features.friends_social_community_event_intelligence_v1 import analyze_friends_social_community_event_intelligence_v1

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


def test_event_intelligence_exposes_distinct_social_event_themes():
    result = analyze_friends_social_community_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {"friendship_connection", "network_collaboration", "community_participation", "social_boundary_reset"}
    assert result["strongest_future_event"] is not None


def test_event_activation_scores_are_bounded():
    result = analyze_friends_social_community_event_intelligence_v1(_chart(), NOW)
    for event in result["events"].values():
        for phase in ("past", "present", "future"):
            activation = event[phase]["activation"]
            if activation:
                assert 0.0 <= activation["activation_score"] <= 1.0


def test_past_activation_does_not_claim_social_history():
    result = analyze_friends_social_community_event_intelligence_v1(_chart(), NOW)
    assert all(event["past"]["historical_status"] == "unconfirmed" for event in result["events"].values())
    rule = result["historical_validation"]["rule"].lower()
    assert "not evidence" in rule
    assert "known social history overrides astrology" in rule


def test_specific_people_and_betrayal_predictions_are_disallowed():
    text = result_text = analyze_friends_social_community_event_intelligence_v1(_chart(), NOW)["limitation"].lower()
    assert "not probabilities" in text
    assert "future friend or enemy" in text
    assert "trustworthiness" in text
    assert "betrayal" in text
    assert result_text
