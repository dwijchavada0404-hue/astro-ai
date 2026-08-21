from app.astrology.features.location_settlement_reasoning_v1 import analyze_location_settlement_v1


def _chart():
    return {
        "houses": {
            "3": {"lord": "Mercury"},
            "4": {"lord": "Moon"},
            "9": {"lord": "Jupiter"},
            "12": {"lord": "Saturn"},
        },
        "planets": {
            "Mercury": {"house": 9},
            "Moon": {"house": 12},
            "Jupiter": {"house": 12},
            "Saturn": {"house": 4},
            "Rahu": {"house": 9},
            "Ketu": {"house": 3},
        },
    }


def test_location_scores_are_bounded_and_ranked():
    result = analyze_location_settlement_v1(_chart())
    assert result["available"] is True
    assert result["dominant_theme"] in result["theme_scores"]
    assert len(result["ranked_themes"]) == 5
    assert all(0.0 <= score <= 1.0 for score in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_foreign_exposure_is_separate_from_foreign_settlement():
    result = analyze_location_settlement_v1(_chart())
    scores = result["theme_scores"]
    assert "foreign_exposure" in scores
    assert "foreign_settlement" in scores
    assert result["known_reality_rule"].lower().find("must not") >= 0
    assert "permanent foreign settlement" in result["known_reality_rule"].lower()


def test_reality_and_immigration_boundaries_are_explicit():
    result = analyze_location_settlement_v1(_chart())
    text = (result["known_reality_rule"] + " " + result["limitation"]).lower()
    assert "known residence" in text
    assert "visa approval" in text
    assert "citizenship" in text
    assert "does not guarantee" in text


def test_missing_house_data_is_unavailable():
    result = analyze_location_settlement_v1({})
    assert result["available"] is False
    assert result["event"] == "location_settlement"
