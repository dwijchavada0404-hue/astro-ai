from app.astrology.features.finance_wealth_trajectory_v1 import analyze_finance_wealth_trajectory_v1


def _base_chart():
    return {
        "houses": {
            "2": {"lord": "Venus"},
            "4": {"lord": "Sun"},
            "5": {"lord": "Mercury"},
            "8": {"lord": "Jupiter"},
            "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
        },
        "planets": {
            "Venus": {"house": 2},
            "Sun": {"house": 4},
            "Mercury": {"house": 5},
            "Jupiter": {"house": 11},
            "Saturn": {"house": 10},
            "Mars": {"house": 3},
            "Rahu": {"house": 6},
            "Ketu": {"house": 12},
        },
    }


def test_trajectory_returns_core_scores_and_patterns():
    result = analyze_finance_wealth_trajectory_v1(_base_chart())
    assert result["available"] is True
    assert result["event"] == "finance_wealth_trajectory"
    assert 0.0 <= result["earning_capacity_score"] <= 1.0
    assert 0.0 <= result["retention_score"] <= 1.0
    assert 0.0 <= result["stability_score"] <= 1.0
    assert 0.0 <= result["volatility_score"] <= 1.0
    assert result["accumulation_pattern"] in {
        "gradual_stable_accumulation",
        "volatile_or_cyclical_growth",
        "strong_earning_weaker_retention",
        "conservative_accumulation",
        "mixed_accumulation_pattern",
    }
    assert result["earning_retention_balance"] in {
        "retention_stronger_than_earning",
        "earning_stronger_than_retention",
        "earning_and_retention_balanced",
    }


def test_later_life_strengthening_can_be_identified():
    chart = _base_chart()
    chart["planets"]["Mercury"] = {"house": 6}
    result = analyze_finance_wealth_trajectory_v1(chart)
    assert result["later_life_score"] >= result["early_life_score"]
    assert result["life_phase_pattern"] in {
        "later_life_strengthening",
        "broadly_balanced_across_life",
    }


def test_finance_house_nodes_raise_volatility():
    chart = _base_chart()
    chart["planets"]["Rahu"] = {"house": 5}
    chart["planets"]["Mars"] = {"house": 8}
    result = analyze_finance_wealth_trajectory_v1(chart)
    assert result["volatility_score"] >= 0.24


def test_missing_natal_data_returns_unavailable():
    result = analyze_finance_wealth_trajectory_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_input_validation():
    try:
        analyze_finance_wealth_trajectory_v1([])  # type: ignore[arg-type]
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
