from datetime import datetime

from app.astrology.features.marriage_forecast_router_v3 import route_marriage_question_v3
from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3


REFERENCE = datetime.fromisoformat("2026-08-15T12:00:00+05:30")


def _chart() -> dict:
    houses = {
        "1": {"sign": "Aries", "lord": "Mars"},
        "2": {"sign": "Taurus", "lord": "Venus"},
        "3": {"sign": "Gemini", "lord": "Mercury"},
        "4": {"sign": "Cancer", "lord": "Moon"},
        "5": {"sign": "Leo", "lord": "Sun"},
        "6": {"sign": "Virgo", "lord": "Mercury"},
        "7": {"sign": "Libra", "lord": "Venus"},
        "8": {"sign": "Scorpio", "lord": "Mars"},
        "9": {"sign": "Sagittarius", "lord": "Jupiter"},
        "10": {"sign": "Capricorn", "lord": "Saturn"},
        "11": {"sign": "Aquarius", "lord": "Saturn"},
        "12": {"sign": "Pisces", "lord": "Jupiter"},
    }
    planets = {
        "Sun": {"house": 5, "sign": "Leo"},
        "Moon": {"house": 7, "sign": "Libra"},
        "Mars": {"house": 7, "sign": "Libra"},
        "Mercury": {"house": 10, "sign": "Capricorn"},
        "Jupiter": {"house": 12, "sign": "Pisces"},
        "Venus": {"house": 12, "sign": "Pisces"},
        "Saturn": {"house": 7, "sign": "Libra"},
        "Rahu": {"house": 9, "sign": "Sagittarius"},
        "Ketu": {"house": 3, "sign": "Gemini"},
    }
    return {"houses": houses, "planets": planets}


def _route(question: str) -> tuple[dict, dict]:
    understanding = analyze_marriage_question_v3(question)
    result = route_marriage_question_v3(_chart(), understanding, REFERENCE)
    return understanding, result


def test_general_post_marriage_change_routes_to_dedicated_engine():
    understanding, result = _route("How could my life change after marriage?")
    assert understanding["primary_event"] == "post_marriage_life_changes"
    assert result["event"] == "post_marriage_life_changes"
    assert result["target"] == "general"
    assert result["evidence_engine"] == "post_marriage_life_changes_reasoning_v2"


def test_relocation_after_marriage_routes_correctly():
    _, result = _route("Will I relocate after marriage?")
    assert result["event"] == "post_marriage_life_changes"
    assert result["target"] == "relocation"


def test_abroad_after_marriage_routes_correctly():
    _, result = _route("Could I move abroad after marriage?")
    assert result["event"] == "post_marriage_life_changes"
    assert result["target"] == "international_exposure"


def test_career_change_after_marriage_routes_correctly():
    _, result = _route("Will there be a career change after marriage?")
    assert result["event"] == "post_marriage_life_changes"
    assert result["target"] == "career_shift"


def test_financial_change_after_marriage_routes_correctly():
    _, result = _route("Will my finances change after marriage?")
    assert result["event"] == "post_marriage_life_changes"
    assert result["target"] == "financial_change"


def test_harmonious_marriage_still_uses_quality_engine():
    understanding = analyze_marriage_question_v3("Will my marriage be harmonious?")
    assert understanding["primary_event"] == "married_life_quality"


def test_conflict_still_uses_challenges_engine():
    understanding = analyze_marriage_question_v3("Will there be conflict in my marriage?")
    assert understanding["primary_event"] == "relationship_challenges"


def test_limitation_remains_non_deterministic():
    _, result = _route("Will I definitely move abroad after marriage?")
    limitation = result["limitation"].lower()
    assert "cannot guarantee" in limitation
    assert "timeline" in limitation
