from app.astrology.features.parents_elders_reasoning_v1 import analyze_parents_elders_v1


def _chart():
    return {
        "houses": {"4": {"lord": "Moon"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}},
        "planets": {"Moon": {"house": 4}, "Jupiter": {"house": 9}, "Sun": {"house": 10}, "Saturn": {"house": 6}, "Mars": {"house": 3}, "Venus": {"house": 5}, "Rahu": {"house": 11}},
    }


def test_foundation_exposes_bounded_parent_elder_themes():
    result = analyze_parents_elders_v1(_chart())
    assert result["available"] is True
    assert set(result["theme_scores"]) == {"emotional_support", "guidance_mentorship", "authority_structure", "duty_responsibility", "independence_boundaries", "family_continuity"}
    assert all(0.0 <= score <= 1.0 for score in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_foundation_uses_multiple_axes_and_significators():
    result = analyze_parents_elders_v1(_chart())
    factors = {item["factor"] for item in result["evidence"]}
    assert "fourth_house_axis" in factors
    assert "ninth_house_axis" in factors
    assert "sun_moon_context" in factors


def test_reality_override_prevents_manufactured_family_history():
    rule = analyze_parents_elders_v1(_chart())["historical_validation"]["rule"].lower()
    assert "known parent/elder relationships" in rule
    assert "must not manufacture" in rule
    assert "illness or loss" in rule


def test_health_death_and_specific_person_claims_are_disallowed():
    text = analyze_parents_elders_v1(_chart())["limitation"].lower()
    assert "health, lifespan or death" in text
    assert "intentions or character" in text
    assert "parent is present or absent" in text


def test_missing_inputs_are_unavailable():
    assert analyze_parents_elders_v1({"houses": {}, "planets": {}})["available"] is False
