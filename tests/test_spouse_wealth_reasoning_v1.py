from app.astrology.features.spouse_wealth_reasoning_v1 import analyze_spouse_wealth_v1


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


def test_v1_available():
    result = analyze_spouse_wealth_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "spouse_wealth"
    assert result["model_version"] == "v1"


def test_v1_has_profile_and_rankings():
    result = analyze_spouse_wealth_v1(_chart())
    assert result["profile"]["wealth_themes"]
    assert result["ranked_themes"]
    assert result["strongest_themes"]


def test_v1_confidence_bounded():
    confidence = analyze_spouse_wealth_v1(_chart())["confidence"]
    assert 0.50 <= confidence <= 0.88


def test_v1_relative_strength_bounded():
    result = analyze_spouse_wealth_v1(_chart())
    for item in result["ranked_themes"]:
        assert 0.0 <= item["relative_strength"] <= 1.0


def test_v1_context_uses_derived_houses():
    context = analyze_spouse_wealth_v1(_chart())["profile"]["chart_context"]
    assert context["resources_house"]["natal_house"] == 8
    assert context["gains_house"]["natal_house"] == 5
    assert context["stability_house"]["natal_house"] == 4


def test_v1_evidence_present():
    result = analyze_spouse_wealth_v1(_chart())
    assert len(result["evidence"]) >= 7


def test_v1_summary_is_nonempty():
    result = analyze_spouse_wealth_v1(_chart())
    assert isinstance(result["summary"], str)
    assert result["summary"]


def test_v1_missing_seventh_house():
    chart = _chart()
    del chart["houses"]["7"]
    result = analyze_spouse_wealth_v1(chart)
    assert result["available"] is False


def test_v1_missing_derived_house():
    chart = _chart()
    del chart["houses"]["8"]
    result = analyze_spouse_wealth_v1(chart)
    assert result["available"] is False


def test_v1_invalid_chart():
    try:
        analyze_spouse_wealth_v1([])
    except ValueError as exc:
        assert "dictionary" in str(exc)
    else:
        raise AssertionError("ValueError expected")
