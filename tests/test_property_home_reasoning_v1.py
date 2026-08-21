import pytest

from app.astrology.features.property_home_reasoning_v1 import analyze_property_home_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"}, "2": {"lord": "Mercury"}, "3": {"lord": "Mars"},
            "4": {"lord": "Venus"}, "9": {"lord": "Jupiter"}, "11": {"lord": "Mercury"},
            "12": {"lord": "Jupiter"},
        },
        "planets": {
            "Sun": {"house": 1}, "Mercury": {"house": 11}, "Mars": {"house": 3},
            "Venus": {"house": 4}, "Jupiter": {"house": 9}, "Saturn": {"house": 10},
            "Moon": {"house": 4}, "Rahu": {"house": 12},
        },
    }


def test_property_home_foundation_is_available_and_bounded():
    result = analyze_property_home_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "property_home"
    assert set(result["theme_scores"]) == {
        "home_stability", "property_acquisition", "asset_accumulation", "home_comfort", "relocation_change"
    }
    assert all(0.0 <= score <= 1.0 for score in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_fourth_house_remains_primary_property_axis():
    result = analyze_property_home_v1(_chart())
    rules = [item["rule"] for item in result["evidence"]]
    assert "fourth_house_lord_available" in rules
    assert "fourth_lord_supportive_placement" in rules
    assert result["theme_scores"]["home_stability"] > 0
    assert result["theme_scores"]["property_acquisition"] > 0


def test_relocation_is_distinct_from_property_ownership():
    result = analyze_property_home_v1(_chart())
    assert result["theme_scores"]["relocation_change"] > 0
    assert "must not infer" in result["known_reality_rule"].lower()


def test_output_does_not_guarantee_property_outcome():
    result = analyze_property_home_v1(_chart())
    limitation = result["limitation"].lower()
    assert "does not guarantee property ownership" in limitation
    assert "financing approval" in limitation


def test_missing_house_data_is_unavailable():
    result = analyze_property_home_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_invalid_chart_type_raises():
    with pytest.raises(ValueError):
        analyze_property_home_v1([])
