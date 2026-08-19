from app.astrology.features.married_life_quality_reasoning_v1 import analyze_married_life_quality_v1


def _chart(seventh_lord="Venus", occupants=None):
    occupants = occupants or []
    planets = {
        "Venus": {"house": 5, "sign": "Taurus"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Moon": {"house": 4, "sign": "Cancer"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Mars": {"house": 3, "sign": "Aries"},
    }
    for planet in occupants:
        planets.setdefault(planet, {"sign": "Libra"})
        planets[planet]["house"] = 7
    return {
        "houses": {"7": {"sign": "Libra", "lord": seventh_lord}},
        "planets": planets,
    }


def test_married_life_quality_basic_contract():
    result = analyze_married_life_quality_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "married_life_quality"
    assert result["model_version"] == "v1"
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["dominant_profile"] in {"harmonious", "passionate", "stable", "variable", "mixed"}
    assert result["evidence"]
    assert result["limitation"]


def test_venus_signature_supports_harmony():
    result = analyze_married_life_quality_v1(_chart(seventh_lord="Venus"))
    assert result["profile"]["profile_scores"].get("harmonious", 0) > 0


def test_saturn_signature_supports_stability():
    result = analyze_married_life_quality_v1(_chart(seventh_lord="Saturn", occupants=["Saturn"]))
    assert result["profile"]["profile_scores"].get("stable", 0) > 0


def test_mars_signature_supports_intensity():
    result = analyze_married_life_quality_v1(_chart(seventh_lord="Mars", occupants=["Mars"]))
    assert result["profile"]["profile_scores"].get("passionate", 0) > 0


def test_missing_seventh_house_is_unavailable():
    result = analyze_married_life_quality_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
    assert result["event"] == "married_life_quality"


def test_non_dict_chart_rejected():
    try:
        analyze_married_life_quality_v1([])
    except ValueError as exc:
        assert "dictionary" in str(exc)
    else:
        raise AssertionError("ValueError expected")
