from datetime import datetime

import app.astrology.features.marriage_forecast_router_v3 as router


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
        "Mars": {"house": 8, "sign": "Scorpio"},
        "Mercury": {"house": 6, "sign": "Virgo"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Venus": {"house": 7, "sign": "Libra"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
        "Ketu": {"house": 5, "sign": "Leo"},
    }
    return {"houses": houses, "planets": planets}


def test_router_dispatches_family_background(monkeypatch):
    expected = {"available": True, "event": "spouse_family_background"}
    monkeypatch.setattr(
        router,
        "_route_spouse_family_background",
        lambda chart, analysis, reference: expected,
    )
    analysis = {
        "primary_event": "spouse_family_background",
        "query_mode": "single_event",
        "intent": {},
    }
    assert router.route_marriage_question_v3({}, analysis, REFERENCE) == expected


def test_family_background_route_contract():
    analysis = {
        "original_question": "Will my spouse come from a traditional family?",
        "normalised_question": "will my spouse come from a traditional family?",
        "primary_event": "spouse_family_background",
        "query_mode": "single_event",
        "intent": {
            "question_type": "probability",
            "direction": "neutral",
            "confidence": 0.82,
        },
    }
    result = router.route_marriage_question_v3(_chart(), analysis, REFERENCE)
    assert result["available"] is True
    assert result["event"] == "spouse_family_background"
    assert result["evidence_engine"] == "spouse_family_background_reasoning_v2"
    assert result["target"] == "traditional"
    assert 0.0 <= result["support_score"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
