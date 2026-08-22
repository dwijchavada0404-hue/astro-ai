from datetime import datetime, timezone

from app.astrology.features.friends_social_community_question_intelligence_v1 import analyze_friends_social_community_question_v1
from app.astrology.features.friends_social_community_router_v1 import route_friends_social_community_question_v1

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


def test_question_intelligence_detects_friendship_and_timing():
    result = analyze_friends_social_community_question_v1("When is a strong period to make new friends?")
    assert result["available"] is True
    assert result["primary_intent"] == "friendship_connection"
    assert result["timing_requested"] is True
    assert result["safety"]["trustworthiness_inference_allowed"] is False


def test_router_routes_social_overview_to_synthesis():
    result = route_friends_social_community_question_v1(_chart(), "Give me a social life overview", NOW)
    assert result["available"] is True
    assert result["route"] == "friends_social_community_synthesis_v1"


def test_router_routes_specific_social_theme_to_event_intelligence():
    result = route_friends_social_community_question_v1(_chart(), "Will networking become important for me?", NOW)
    assert result["route"] == "friends_social_community_event_v1"
    assert result["event_key"] == "network_collaboration"


def test_specific_person_trust_question_stays_bounded():
    result = analyze_friends_social_community_question_v1("Can I trust my friends?")
    assert result["available"] is True
    assert result["safety"]["specific_person_loyalty_inference_allowed"] is False
    assert result["safety"]["trustworthiness_inference_allowed"] is False


def test_unknown_question_is_unsupported():
    result = route_friends_social_community_question_v1(_chart(), "What colour should I paint my room?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"
