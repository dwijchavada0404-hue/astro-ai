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
        "Mars": {"house": 8, "sign": "Scorpio"},
        "Mercury": {"house": 6, "sign": "Virgo"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Venus": {"house": 7, "sign": "Libra"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
        "Ketu": {"house": 5, "sign": "Leo"},
    }
    return {"houses": houses, "planets": planets}


def _route(question: str) -> tuple[dict, dict]:
    understanding = analyze_marriage_question_v3(question)
    result = route_marriage_question_v3(_chart(), understanding, REFERENCE)
    return understanding, result


def test_financial_profile_question_uses_existing_spouse_wealth_event():
    understanding, result = _route("Describe my future spouse's financial profile.")

    assert understanding["primary_event"] == "spouse_wealth"
    assert result["event"] == "spouse_wealth"
    assert result["target"] == "general"
    assert result["analysis"]["reasoning_engine"] == "spouse_financial_profile_reasoning_v2"
    assert result["analysis"]["financial_profile_analysis"]["event"] == "spouse_financial_profile"


def test_financial_stability_uses_financial_profile_engine_and_legacy_target():
    _, result = _route("Will my spouse be financially stable?")

    assert result["target"] == "financially_stable"
    assert result["analysis"]["reasoning_engine"] == "spouse_financial_profile_reasoning_v2"
    assert result["support_score"] is not None
    assert result["answer"]


def test_standalone_entrepreneurial_question_remains_profession():
    _, result = _route("Could my future spouse be entrepreneurial?")

    # A standalone entrepreneurial question is about career orientation rather
    # than financial condition. Financial-profile routing should only take over
    # when the question explicitly asks about money, income, wealth, stability,
    # assets, or an overall financial profile.
    assert result["event"] == "spouse_profession"


def test_variable_income_maps_to_speculative_income():
    _, result = _route("Could my spouse have variable income?")

    assert result["target"] == "speculative_income"
    assert result["analysis"]["financial_profile_analysis"]["target"] == "variable"


def test_property_question_stays_on_legacy_wealth_reasoning():
    _, result = _route("Will my spouse own property?")

    assert result["target"] == "property_assets"
    assert result["analysis"]["reasoning_engine"] == "spouse_wealth_reasoning_v2"
    assert "financial_profile_analysis" not in result["analysis"]
