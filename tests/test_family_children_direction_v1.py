from app.astrology.features.family_children_direction_v1 import analyze_family_children_direction_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Venus"},
            "4": {"lord": "Moon"},
            "5": {"lord": "Jupiter"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Mars"},
            "11": {"lord": "Mercury"},
            "12": {"lord": "Sun"},
        },
        "planets": {
            "Venus": {"house": 4},
            "Moon": {"house": 5},
            "Jupiter": {"house": 9},
            "Saturn": {"house": 8},
            "Mars": {"house": 11},
            "Mercury": {"house": 2},
            "Sun": {"house": 12},
        },
    }


def test_direction_is_bounded_and_ranked():
    result = analyze_family_children_direction_v1(_chart())
    assert result["available"] is True
    assert result["primary_direction"] in result["direction_scores"]
    assert len(result["ranked_directions"]) == 5
    assert all(0.0 <= score <= 1.0 for score in result["direction_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_parenting_symbolism_does_not_assert_biological_outcome():
    result = analyze_family_children_direction_v1(_chart())
    text = (result["reality_override"]["rule"] + " " + result["limitation"]).lower()
    assert "must never" in text
    assert "pregnancy" in text
    assert "biological parenthood" in text
    assert "does not predict or guarantee" in text


def test_missing_foundation_is_unavailable():
    result = analyze_family_children_direction_v1({})
    assert result["available"] is False
    assert result["event"] == "family_children_direction"
