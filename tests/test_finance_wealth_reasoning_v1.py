from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"},
            "5": {"lord": "Venus"},
            "8": {"lord": "Jupiter"},
            "9": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
        },
        "planets": {
            "Mercury": {"house": 11},
            "Venus": {"house": 5},
            "Jupiter": {"house": 11},
            "Saturn": {"house": 9},
        },
    }


def test_finance_v1_contract():
    result = analyze_finance_wealth_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "finance_wealth"
    assert result["model_version"] == "v1"
    assert result["dominant_theme"]
    assert result["evidence_count"] == len(result["evidence"])
    assert len(result["ranked_themes"]) == 5


def test_finance_v1_scores_are_bounded():
    result = analyze_finance_wealth_v1(_chart())
    assert all(0.0 <= value <= 1.0 for value in result["theme_scores"].values())


def test_finance_v1_includes_non_advice_limitation():
    result = analyze_finance_wealth_v1(_chart())
    limitation = result["limitation"].lower()
    assert "not financial advice" in limitation
    assert "not a guarantee" in limitation


def test_finance_v1_unavailable_without_chart_data():
    result = analyze_finance_wealth_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_finance_v1_rejects_non_dict_chart():
    try:
        analyze_finance_wealth_v1([])
    except ValueError as exc:
        assert "dictionary" in str(exc)
    else:
        raise AssertionError("ValueError expected")
