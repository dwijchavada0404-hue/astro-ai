from app.astrology.features.career_direction_v1 import analyze_career_direction_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "5": {"lord": "Venus"},
            "6": {"lord": "Mercury"},
            "7": {"lord": "Jupiter"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
            "12": {"lord": "Mars"},
        },
        "planets": {
            "Mercury": {"house": 10},
            "Mars": {"house": 3},
            "Venus": {"house": 5},
            "Jupiter": {"house": 11},
            "Saturn": {"house": 10},
            "Sun": {"house": 9},
            "Rahu": {"house": 12},
        },
    }


def test_direction_returns_ranked_professions():
    result = analyze_career_direction_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "career_direction"
    assert result["primary_direction"] in result["direction_scores"]
    assert result["secondary_direction"] in result["direction_scores"]
    assert result["tertiary_direction"] in result["direction_scores"]
    assert len(result["ranked_directions"]) == 11


def test_scores_are_bounded():
    result = analyze_career_direction_v1(_chart())
    assert all(0.0 <= score <= 1.0 for score in result["direction_scores"].values())


def test_finance_audit_and_management_can_receive_support():
    result = analyze_career_direction_v1(_chart())
    assert result["direction_scores"]["finance_audit_risk"] > 0
    assert result["direction_scores"]["management_leadership"] > 0


def test_missing_natal_foundation_returns_unavailable():
    result = analyze_career_direction_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_input_validation():
    try:
        analyze_career_direction_v1([])  # type: ignore[arg-type]
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
