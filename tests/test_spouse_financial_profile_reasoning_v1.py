from app.astrology.features.spouse_financial_profile_reasoning_v1 import (
    analyze_spouse_financial_profile_v1,
)


def _chart(seventh_lord="Jupiter", eighth_lord="Venus", occupants=None):
    occupants = occupants or []
    planets = {
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Venus": {"house": 5, "sign": "Taurus"},
        "Mercury": {"house": 3, "sign": "Gemini"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
    }
    for planet in occupants:
        planets.setdefault(planet, {"sign": "Libra"})
        planets[planet]["house"] = 7
    return {
        "houses": {
            "7": {"sign": "Libra", "lord": seventh_lord},
            "8": {"sign": "Scorpio", "lord": eighth_lord},
        },
        "planets": planets,
    }


def test_spouse_financial_profile_basic_contract():
    result = analyze_spouse_financial_profile_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "spouse_financial_profile"
    assert result["model_version"] == "v1"
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["dominant_profile"] in {
        "affluent",
        "stable",
        "entrepreneurial",
        "variable",
        "mixed",
    }
    assert result["evidence"]
    assert result["limitation"]


def test_jupiter_signature_supports_affluence():
    result = analyze_spouse_financial_profile_v1(_chart(seventh_lord="Jupiter"))
    assert result["profile"]["profile_scores"].get("affluent", 0) > 0


def test_saturn_signature_supports_stability():
    result = analyze_spouse_financial_profile_v1(
        _chart(seventh_lord="Saturn", occupants=["Saturn"])
    )
    assert result["profile"]["profile_scores"].get("stable", 0) > 0


def test_mercury_signature_supports_entrepreneurial_pattern():
    result = analyze_spouse_financial_profile_v1(
        _chart(seventh_lord="Mercury", occupants=["Mercury"])
    )
    assert result["profile"]["profile_scores"].get("entrepreneurial", 0) > 0


def test_rahu_signature_supports_variable_pattern():
    result = analyze_spouse_financial_profile_v1(
        _chart(seventh_lord="Rahu", occupants=["Rahu"])
    )
    assert result["profile"]["profile_scores"].get("variable", 0) > 0


def test_missing_seventh_house_is_unavailable():
    result = analyze_spouse_financial_profile_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
    assert result["event"] == "spouse_financial_profile"


def test_exact_financial_claims_are_not_made():
    result = analyze_spouse_financial_profile_v1(_chart())
    limitation = result["limitation"].lower()
    assert "exact salary" in limitation
    assert "net worth" in limitation


def test_non_dict_chart_rejected():
    try:
        analyze_spouse_financial_profile_v1([])
    except ValueError as exc:
        assert "dictionary" in str(exc)
    else:
        raise AssertionError("ValueError expected")
