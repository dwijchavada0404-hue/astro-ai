from app.astrology.features.married_life_quality_reasoning_v2 import analyze_married_life_quality_v2


def _chart(seventh_lord="Venus"):
    return {
        "houses": {"7": {"sign": "Libra", "lord": seventh_lord}},
        "planets": {
            "Venus": {"house": 5, "sign": "Taurus"},
            "Jupiter": {"house": 9, "sign": "Sagittarius"},
            "Moon": {"house": 4, "sign": "Cancer"},
            "Saturn": {"house": 10, "sign": "Capricorn"},
            "Mars": {"house": 3, "sign": "Aries"},
        },
    }


def test_general_married_life_quality_contract():
    result = analyze_married_life_quality_v2(_chart(), "How will my married life be?")
    assert result["available"] is True
    assert result["event"] == "married_life_quality"
    assert result["model_version"] == "v2"
    assert result["target"] == "general_quality"
    assert 0.0 <= result["support_score"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["answer"]
    assert result["limitation"]


def test_harmony_target_detection():
    result = analyze_married_life_quality_v2(_chart(), "Will I have a harmonious marriage?")
    assert result["target"] == "harmony"
    assert result["requested_profile"] == "harmonious"
    assert result["matched_keywords"]


def test_stability_target_detection():
    result = analyze_married_life_quality_v2(_chart("Saturn"), "Will my marriage be stable?")
    assert result["target"] == "stability"
    assert result["requested_profile"] == "stable"


def test_passion_target_detection():
    result = analyze_married_life_quality_v2(_chart("Mars"), "Will I have a passionate marriage?")
    assert result["target"] == "passion"
    assert result["requested_profile"] == "passionate"


def test_variability_target_detection():
    result = analyze_married_life_quality_v2(_chart(), "Will my marriage have ups and downs?")
    assert result["target"] == "variability"
    assert result["requested_profile"] == "variable"


def test_empty_question_rejected():
    try:
        analyze_married_life_quality_v2(_chart(), "   ")
    except ValueError as exc:
        assert "non-empty" in str(exc)
    else:
        raise AssertionError("ValueError expected")


def test_missing_seventh_house_preserves_target_metadata():
    result = analyze_married_life_quality_v2({"houses": {}, "planets": {}}, "Will my marriage be stable?")
    assert result["available"] is False
    assert result["target"] == "stability"
    assert result["matched_keywords"]
