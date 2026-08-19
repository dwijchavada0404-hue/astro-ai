from datetime import datetime

from app.astrology.features.marriage_forecast_router_v3 import route_marriage_question_v3
from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3


REFERENCE = datetime.fromisoformat("2026-08-15T12:00:00+05:30")


def _chart() -> dict:
    houses = {
        str(i): {"sign": sign, "lord": lord}
        for i, (sign, lord) in enumerate(
            [
                ("Aries", "Mars"),
                ("Taurus", "Venus"),
                ("Gemini", "Mercury"),
                ("Cancer", "Moon"),
                ("Leo", "Sun"),
                ("Virgo", "Mercury"),
                ("Libra", "Venus"),
                ("Scorpio", "Mars"),
                ("Sagittarius", "Jupiter"),
                ("Capricorn", "Saturn"),
                ("Aquarius", "Saturn"),
                ("Pisces", "Jupiter"),
            ],
            start=1,
        )
    }
    planets = {
        "Sun": {"house": 5, "sign": "Leo"},
        "Moon": {"house": 4, "sign": "Cancer"},
        "Mars": {"house": 3, "sign": "Scorpio"},
        "Mercury": {"house": 7, "sign": "Libra"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Venus": {"house": 1, "sign": "Aries"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
        "Ketu": {"house": 5, "sign": "Leo"},
    }
    return {"houses": houses, "planets": planets}


def _route(question: str) -> tuple[dict, dict]:
    understanding = analyze_marriage_question_v3(question)
    result = route_marriage_question_v3(_chart(), understanding, REFERENCE)
    return understanding, result


def test_compatibility_question_routes_to_dedicated_engine():
    understanding, result = _route("What does my marriage compatibility look like?")
    assert understanding["primary_event"] == "marriage_compatibility_dynamics"
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["target"] == "general"
    assert result["evidence_engine"] == "marriage_compatibility_dynamics_reasoning_v2"


def test_communication_question_routes_to_compatibility():
    _, result = _route("How will communication in my marriage be?")
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["target"] == "communication_flow"


def test_shared_values_question_routes_to_compatibility():
    _, result = _route("Will we have shared values in our relationship?")
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["target"] == "shared_values"


def test_emotional_connection_question_routes_to_compatibility():
    _, result = _route("Will there be emotional connection in my marriage?")
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["target"] == "emotional_attunement"


def test_space_independence_question_routes_to_compatibility():
    _, result = _route("Will we need space and independence in the relationship?")
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["target"] == "independence"


def test_conflict_stays_with_relationship_challenges():
    understanding = analyze_marriage_question_v3("Will there be conflict in my marriage?")
    assert understanding["primary_event"] == "relationship_challenges"


def test_harmonious_marriage_stays_with_married_life_quality():
    understanding = analyze_marriage_question_v3("Will my marriage be harmonious?")
    assert understanding["primary_event"] == "married_life_quality"


def test_limitation_preserves_one_chart_boundary():
    _, result = _route("What does my relationship compatibility look like?")
    limitation = result["limitation"].lower()
    assert "one natal chart" in limitation
    assert "synastry" in limitation
    assert "real-world" in limitation
