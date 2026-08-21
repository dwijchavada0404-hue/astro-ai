from app.astrology.features.property_home_direction_v1 import analyze_property_home_direction_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"},
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "4": {"lord": "Venus"},
            "9": {"lord": "Jupiter"},
            "11": {"lord": "Mercury"},
            "12": {"lord": "Jupiter"},
        },
        "planets": {
            "Sun": {"house": 1},
            "Mercury": {"house": 11},
            "Mars": {"house": 3},
            "Venus": {"house": 4},
            "Jupiter": {"house": 9},
            "Moon": {"house": 4},
            "Saturn": {"house": 10},
            "Rahu": {"house": 12},
        },
    }


def test_property_home_direction_is_available_and_ranked():
    result = analyze_property_home_direction_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "property_home_direction"
    assert result["primary_direction"] in result["direction_scores"]
    assert result["secondary_direction"] in result["direction_scores"]
    assert len(result["ranked_directions"]) == 5


def test_direction_scores_are_bounded():
    result = analyze_property_home_direction_v1(_chart())
    assert all(0.0 <= score <= 1.0 for score in result["direction_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_ownership_and_stability_are_not_the_same_output():
    result = analyze_property_home_direction_v1(_chart())
    scores = result["direction_scores"]
    assert "ownership_establishment" in scores
    assert "residential_stability" in scores
    assert "relocation_mobility" in scores


def test_reality_override_prevents_ownership_claims():
    result = analyze_property_home_direction_v1(_chart())
    override = result["reality_override"]
    assert override["known_facts_override"] is True
    assert "must never be converted into a claim" in override["rule"].lower()
    assert "does not predict or guarantee a property purchase" in result["limitation"].lower()


def test_missing_foundation_is_handled():
    result = analyze_property_home_direction_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
