from datetime import datetime, timezone

from app.astrology.features.siblings_communication_event_intelligence_v1 import analyze_siblings_communication_event_intelligence_v1

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


def test_event_intelligence_exposes_distinct_themes():
    result = analyze_siblings_communication_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {"sibling_peer_connection", "communication_expression", "initiative_skill_building", "collaboration_exchange", "boundary_assertiveness"}
    assert result["strongest_future_event"] is not None


def test_event_activation_scores_are_bounded():
    result = analyze_siblings_communication_event_intelligence_v1(_chart(), NOW)
    for event in result["events"].values():
        for phase in ("past", "present", "future"):
            activation = event[phase]["activation"]
            if activation:
                assert 0.0 <= activation["activation_score"] <= 1.0


def test_historical_events_remain_unconfirmed():
    result = analyze_siblings_communication_event_intelligence_v1(_chart(), NOW)
    assert all(event["past"]["historical_status"] == "unconfirmed" for event in result["events"].values())
    assert "not evidence" in result["historical_validation"]["rule"].lower()


def test_specific_sibling_predictions_are_disallowed():
    text = analyze_siblings_communication_event_intelligence_v1(_chart(), NOW)["limitation"].lower()
    assert "not probabilities" in text
    assert "whether a sibling exists" in text
    assert "intentions or loyalty" in text
    assert "estrangement" in text
