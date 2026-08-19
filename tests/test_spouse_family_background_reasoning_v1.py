import pytest

from app.astrology.features.spouse_family_background_reasoning_v1 import (
    analyze_spouse_family_background_v1,
)


def _chart() -> dict:
    houses = {
        str(i): {"sign": sign, "lord": lord}
        for i, (sign, lord) in enumerate(
            [
                ("Aries", "Mars"), ("Taurus", "Venus"), ("Gemini", "Mercury"),
                ("Cancer", "Moon"), ("Leo", "Sun"), ("Virgo", "Mercury"),
                ("Libra", "Venus"), ("Scorpio", "Mars"), ("Sagittarius", "Jupiter"),
                ("Capricorn", "Saturn"), ("Aquarius", "Saturn"), ("Pisces", "Jupiter"),
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


def test_v1_contract():
    result = analyze_spouse_family_background_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "spouse_family_background"
    assert result["model_version"] == "v1"
    assert result["summary"]
    assert result["ranked_themes"]
    assert result["strongest_themes"]


def test_v1_derived_house_context():
    context = analyze_spouse_family_background_v1(_chart())["profile"]["chart_context"]
    assert context["family_house"]["natal_house"] == 8
    assert context["home_culture_house"]["natal_house"] == 10


def test_v1_confidence_bounded():
    value = analyze_spouse_family_background_v1(_chart())["confidence"]
    assert 0.50 <= value <= 0.88


def test_v1_relative_strength_bounded():
    for item in analyze_spouse_family_background_v1(_chart())["ranked_themes"]:
        assert 0.0 <= item["relative_strength"] <= 1.0


def test_v1_evidence_present():
    assert len(analyze_spouse_family_background_v1(_chart())["evidence"]) >= 5


def test_v1_missing_seventh_house():
    chart = _chart()
    del chart["houses"]["7"]
    assert analyze_spouse_family_background_v1(chart)["available"] is False


def test_v1_missing_family_house():
    chart = _chart()
    del chart["houses"]["8"]
    assert analyze_spouse_family_background_v1(chart)["available"] is False


def test_v1_invalid_chart():
    with pytest.raises(ValueError):
        analyze_spouse_family_background_v1([])
