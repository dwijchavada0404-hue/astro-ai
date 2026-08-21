from app.astrology.features.family_children_reasoning_v1 import analyze_family_children_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"}, "2": {"lord": "Moon"}, "4": {"lord": "Venus"},
            "5": {"lord": "Jupiter"}, "8": {"lord": "Saturn"}, "9": {"lord": "Mars"},
            "11": {"lord": "Mercury"}, "12": {"lord": "Saturn"},
        },
        "planets": {
            "Sun": {"house": 1}, "Moon": {"house": 4}, "Venus": {"house": 2},
            "Jupiter": {"house": 5}, "Mars": {"house": 9}, "Mercury": {"house": 11},
            "Saturn": {"house": 8},
        },
    }


def test_family_children_foundation_returns_bounded_evidence_backed_scores():
    result = analyze_family_children_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "family_children"
    assert set(result["theme_scores"]) == {
        "family_stability", "children_parenthood", "family_growth", "family_support", "family_change"
    }
    assert all(0.0 <= value <= 1.0 for value in result["theme_scores"].values())
    assert result["evidence"]
    assert 0.0 <= result["confidence"] <= 1.0


def test_family_children_foundation_does_not_claim_sensitive_outcomes():
    result = analyze_family_children_v1(_chart())
    limitation = result["limitation"].lower()
    reality = result["known_reality_rule"].lower()
    assert "does not predict or guarantee" in limitation
    assert "pregnancy" in limitation
    assert "fertility" in limitation
    assert "without confirmation" in reality
    assert "override predictive assumptions" in reality


def test_family_children_foundation_requires_house_data():
    result = analyze_family_children_v1({"planets": {}})
    assert result["available"] is False


def test_family_children_foundation_rejects_non_dict_chart():
    try:
        analyze_family_children_v1([])
    except ValueError as exc:
        assert "dictionary" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
