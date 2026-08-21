from app.astrology.features.education_learning_reasoning_v1 import analyze_education_learning_v1


def _chart():
    return {
        "houses": {
            "3": {"lord": "Mercury"},
            "4": {"lord": "Moon"},
            "5": {"lord": "Jupiter"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Venus"},
        },
        "planets": {
            "Mercury": {"house": 3},
            "Moon": {"house": 4},
            "Jupiter": {"house": 5},
            "Saturn": {"house": 8},
            "Venus": {"house": 9},
            "Mars": {"house": 10},
        },
    }


def test_scores_are_bounded_and_ranked():
    result = analyze_education_learning_v1(_chart())
    assert result["available"] is True
    assert result["dominant_theme"] in result["theme_scores"]
    assert len(result["ranked_themes"]) == 6
    assert all(0.0 <= score <= 1.0 for score in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_learning_directions_are_not_collapsed_into_one_course_rule():
    result = analyze_education_learning_v1(_chart())
    assert "analytical_learning" in result["theme_scores"]
    assert "communication_learning" in result["theme_scores"]
    assert "higher_education" in result["theme_scores"]
    assert "creative_learning" in result["theme_scores"]


def test_reality_override_and_outcome_boundaries_are_explicit():
    result = analyze_education_learning_v1(_chart())
    text = (result["known_reality_rule"] + " " + result["limitation"]).lower()
    assert "known education history" in text
    assert "must not invent" in text
    assert "does not guarantee admission" in text
    assert "examination success" in text


def test_missing_house_data_is_unavailable():
    result = analyze_education_learning_v1({})
    assert result["available"] is False
    assert result["event"] == "education_learning"
