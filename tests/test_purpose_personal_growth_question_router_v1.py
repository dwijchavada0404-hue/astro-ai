from datetime import datetime, timezone

from app.astrology.features.purpose_personal_growth_question_intelligence_v1 import analyze_purpose_personal_growth_question_v1
from app.astrology.features.purpose_personal_growth_router_v1 import route_purpose_personal_growth_question_v1


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


def test_question_intelligence_detects_overview_and_timing():
    result = analyze_purpose_personal_growth_question_v1("When will I understand my life purpose better?")
    assert result["available"] is True
    assert result["primary_intent"] == "purpose_overview"
    assert result["timing_requested"] is True
    assert result["safety"]["fixed_destiny_claim_allowed"] is False


def test_router_routes_overview_to_synthesis():
    result = route_purpose_personal_growth_question_v1(_chart(), "What is my life purpose?", NOW)
    assert result["available"] is True
    assert result["route"] == "purpose_personal_growth_synthesis_v1"


def test_router_routes_specific_growth_theme():
    result = route_purpose_personal_growth_question_v1(_chart(), "Will mentoring others be important for me?", NOW)
    assert result["route"] == "purpose_personal_growth_event_v1"
    assert result["event_key"] == "knowledge_guidance"


def test_unknown_question_is_unsupported():
    result = route_purpose_personal_growth_question_v1(_chart(), "What colour should I paint my room?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"
