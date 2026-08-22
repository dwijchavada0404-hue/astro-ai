from app.astrology.features.siblings_communication_reasoning_v1 import analyze_siblings_communication_v1


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"}, "7": {"lord": "Venus"}, "11": {"lord": "Moon"}},
        "planets": {"Mercury": {"house": 3}, "Mars": {"house": 6}, "Jupiter": {"house": 5}, "Venus": {"house": 7}, "Moon": {"house": 11}, "Saturn": {"house": 3}, "Sun": {"house": 10}},
    }


def test_foundation_exposes_distinct_bounded_themes():
    result = analyze_siblings_communication_v1(_chart())
    assert result["available"] is True
    assert set(result["theme_scores"]) == {"sibling_bond", "communication_expression", "initiative_courage", "learning_skills", "collaboration", "boundaries_competition"}
    assert all(0.0 <= value <= 1.0 for value in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_third_house_is_primary_axis_with_multi_factor_evidence():
    result = analyze_siblings_communication_v1(_chart())
    factors = {item["factor"] for item in result["evidence"]}
    assert "third_house_axis" in factors
    assert "mercury" in factors
    assert "mars" in factors
    assert "peer_network_context" in factors


def test_reality_override_does_not_manufacture_sibling_history():
    result = analyze_siblings_communication_v1(_chart())
    rule = result["historical_validation"]["rule"].lower()
    assert "known sibling relationships" in rule
    assert "must not manufacture" in rule
    assert "estrangement" in rule


def test_specific_sibling_and_conflict_predictions_are_disallowed():
    text = analyze_siblings_communication_v1(_chart())["limitation"].lower()
    assert "cannot determine whether a sibling exists" in text
    assert "specific sibling" in text
    assert "judge loyalty" in text
    assert "estrangement" in text


def test_missing_chart_inputs_are_unavailable():
    result = analyze_siblings_communication_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
