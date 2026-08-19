from datetime import datetime

import app.astrology.features.marriage_forecast_router_v3 as router


REFERENCE = datetime.fromisoformat("2026-08-15T12:00:00+05:30")


def test_router_dispatches_spouse_wealth(monkeypatch):
    expected = {"available": True, "event": "spouse_wealth"}
    monkeypatch.setattr(
        router,
        "_route_spouse_wealth",
        lambda chart, analysis, reference: expected,
    )
    question_analysis = {
        "primary_event": "spouse_wealth",
        "query_mode": "single_event",
        "intent": {},
    }
    assert router.route_marriage_question_v3({}, question_analysis, REFERENCE) == expected


def test_spouse_wealth_route_contract():
    chart = {
        "houses": {
            "1": {"sign": "Aries", "lord": "Mars"},
            "2": {"sign": "Taurus", "lord": "Venus"},
            "4": {"sign": "Cancer", "lord": "Moon"},
            "7": {"sign": "Libra", "lord": "Venus"},
            "8": {"sign": "Scorpio", "lord": "Mars"},
            "10": {"sign": "Capricorn", "lord": "Saturn"},
            "11": {"sign": "Aquarius", "lord": "Saturn"},
        },
        "planets": {
            "Venus": {"house": 11, "sign": "Aquarius"},
            "Jupiter": {"house": 2, "sign": "Taurus"},
            "Mercury": {"house": 10, "sign": "Capricorn"},
            "Saturn": {"house": 11, "sign": "Aquarius"},
            "Rahu": {"house": 8, "sign": "Scorpio"},
        },
    }
    qa = {
        "original_question": "Will my spouse be wealthy?",
        "normalised_question": "will my spouse be wealthy?",
        "primary_event": "spouse_wealth",
        "query_mode": "single_event",
        "intent": {"question_type": "probability", "direction": "neutral", "confidence": 0.82},
    }
    result = router.route_marriage_question_v3(chart, qa, REFERENCE)
    assert result["event"] == "spouse_wealth"
    assert result["evidence_engine"] == "spouse_wealth_reasoning_v2"
    assert 0.0 <= result["support_score"] <= 1.0
