from app.astrology.features.career_direction_intelligence_v1 import analyze_career_direction_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"},
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "5": {"lord": "Mercury"},
            "6": {"lord": "Saturn"},
            "7": {"lord": "Venus"},
            "8": {"lord": "Jupiter"},
            "9": {"lord": "Jupiter"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Mercury"},
            "12": {"lord": "Jupiter"},
        },
        "planets": {
            "Sun": {"house": 10},
            "Mercury": {"house": 11},
            "Mars": {"house": 3},
            "Jupiter": {"house": 9},
            "Venus": {"house": 7},
            "Saturn": {"house": 10},
            "Rahu": {"house": 11},
        },
    }


def test_direction_engine_returns_ranked_profession_families():
    result = analyze_career_direction_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "career_direction"
    assert len(result["ranked_directions"]) == 9
    assert result["primary_direction"] in result["direction_scores"]
    assert 0.0 <= result["primary_score"] <= 1.0


def test_work_environment_is_ranked_separately():
    result = analyze_career_direction_v1(_chart())
    assert result["primary_environment"] in {
        "structured_organisation", "independent_practice", "foreign_mnc", "public_institutional"
    }
    assert len(result["ranked_environments"]) == 4


def test_mercury_career_chart_supports_commerce_and_communication():
    result = analyze_career_direction_v1(_chart())
    assert result["direction_scores"]["finance_commerce_analytics"] > 0
    assert result["direction_scores"]["consulting_communication"] > 0


def test_foreign_environment_can_receive_support():
    result = analyze_career_direction_v1(_chart())
    assert result["environment_scores"]["foreign_mnc"] > 0


def test_missing_house_data_returns_unavailable():
    result = analyze_career_direction_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_input_validation():
    try:
        analyze_career_direction_v1([])  # type: ignore[arg-type]
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
