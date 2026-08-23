from app.astrology.features.travel_journeys_reasoning_v1 import analyze_travel_journeys_v1


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "6": {"lord": "Saturn"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}, "12": {"lord": "Venus"}},
        "planets": {"Mercury": {"house": 3}, "Saturn": {"house": 6}, "Jupiter": {"house": 9}, "Sun": {"house": 10}, "Venus": {"house": 12}, "Moon": {"house": 9}, "Rahu": {"house": 12}},
    }


def test_foundation_exposes_distinct_bounded_travel_themes():
    result = analyze_travel_journeys_v1(_chart())
    assert result["available"] is True
    assert set(result["theme_scores"]) == {"short_journeys", "long_distance_travel", "international_exposure", "work_study_travel", "recurring_mobility", "travel_adaptability"}
    assert all(0.0 <= value <= 1.0 for value in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_third_ninth_twelfth_axes_are_explicitly_separated():
    result = analyze_travel_journeys_v1(_chart())
    factors = {item["factor"] for item in result["evidence"]}
    assert "third_house_mobility" in factors
    assert "ninth_house_distance" in factors
    assert "twelfth_house_foreign_exposure" in factors
    assert "work_study_context" in factors


def test_travel_is_not_silently_converted_to_settlement():
    result = analyze_travel_journeys_v1(_chart())
    rule = result["known_reality_rule"].lower()
    assert "must not be silently converted" in rule
    assert "immigration" in rule
    assert "permanent settlement" in rule


def test_unsafe_or_guaranteed_travel_claims_are_disallowed():
    text = analyze_travel_journeys_v1(_chart())["limitation"].lower()
    assert "does not guarantee" in text
    assert "exact destination" in text
    assert "travel safety or accidents" in text
    assert "visa/immigration" in text
    assert "permanent relocation" in text


def test_missing_inputs_are_unavailable():
    result = analyze_travel_journeys_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
