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
        "Mars": {"house": 7, "sign": "Libra"},
        "Mercury": {"house": 6, "sign": "Virgo"},
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


def test_conflict_question_routes_to_relationship_challenges():
    understanding, result = _route("Will there be conflict in my marriage?")
    assert understanding["primary_event"] == "relationship_challenges"
    assert result["event"] == "relationship_challenges"
    assert result["target"] == "conflict"
    assert result["evidence_engine"] == "relationship_challenges_reasoning_v2"


def test_emotional_distance_question_routes_to_relationship_challenges():
    _, result = _route("Could there be emotional distance in my relationship?")
    assert result["event"] == "relationship_challenges"
    assert result["target"] == "emotional_distance"


def test_instability_question_routes_to_relationship_challenges():
    _, result = _route("Could my marriage be unstable?")
    assert result["event"] == "relationship_challenges"
    assert result["target"] == "instability"


def test_repair_question_routes_to_relationship_challenges():
    _, result = _route("Can my relationship recover and reconcile after conflict?")
    assert result["event"] == "relationship_challenges"
    assert result["target"] == "repair"


def test_married_life_quality_stays_separate():
    understanding = analyze_marriage_question_v3("Will my marriage be harmonious?")
    assert understanding["primary_event"] == "married_life_quality"


def test_relationship_challenges_safety_limitation_present():
    _, result = _route("Will there be conflict in my marriage?")
    limitation = result["limitation"].lower()
    assert "divorce" in limitation
    assert "abuse" in limitation
    assert "guaranteed" in limitation
