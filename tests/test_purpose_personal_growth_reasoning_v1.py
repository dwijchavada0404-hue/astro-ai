from app.astrology.features.purpose_personal_growth_reasoning_v1 import analyze_purpose_personal_growth_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"},
            "9": {"lord": "Mercury"}, "10": {"lord": "Mars"}, "12": {"lord": "Moon"},
        },
        "planets": {
            "Sun": {"house": 10}, "Jupiter": {"house": 9}, "Saturn": {"house": 6},
            "Mercury": {"house": 5}, "Mars": {"house": 10}, "Moon": {"house": 12},
            "Venus": {"house": 5}, "Ketu": {"house": 12},
        },
    }


def test_purpose_scores_are_bounded_and_ranked():
    result = analyze_purpose_personal_growth_v1(_chart())
    assert result["available"] is True
    assert result["dominant_theme"] in result["theme_scores"]
    assert len(result["ranked_themes"]) == 6
    assert all(0.0 <= score <= 1.0 for score in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_purpose_is_not_declared_as_fixed_destiny():
    result = analyze_purpose_personal_growth_v1(_chart())
    text = (result["known_reality_rule"] + " " + result["limitation"]).lower()
    assert "must not declare a fixed destiny" in text
    assert "singular life purpose" in text
    assert "not proof of destiny" in text


def test_known_values_and_choices_override_astrology():
    result = analyze_purpose_personal_growth_v1(_chart())
    rule = result["known_reality_rule"].lower()
    assert "known values" in rule
    assert "choices" in rule
    assert "lived experience" in rule


def test_missing_house_data_is_unavailable():
    result = analyze_purpose_personal_growth_v1({})
    assert result["available"] is False
    assert result["event"] == "purpose_personal_growth"
