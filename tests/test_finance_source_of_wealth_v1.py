from app.astrology.features.finance_source_of_wealth_v1 import analyze_finance_source_of_wealth_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "4": {"lord": "Venus"},
            "5": {"lord": "Jupiter"},
            "7": {"lord": "Mercury"},
            "8": {"lord": "Venus"},
            "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
        },
        "planets": {
            "Mercury": {"house": 10},
            "Mars": {"house": 3},
            "Venus": {"house": 4},
            "Jupiter": {"house": 11},
            "Saturn": {"house": 10},
        },
    }


def test_source_of_wealth_returns_ranked_channels():
    result = analyze_finance_source_of_wealth_v1(_chart())
    assert result["available"] is True
    assert len(result["ranked_sources"]) == 6
    assert result["primary_source"] in result["source_scores"]
    assert result["secondary_source"] in result["source_scores"]


def test_business_and_network_channels_can_score():
    result = analyze_finance_source_of_wealth_v1(_chart())
    assert result["source_scores"]["business_entrepreneurship"] > 0
    assert result["source_scores"]["networks_multiple_income"] > 0


def test_property_channel_uses_fourth_house_links():
    result = analyze_finance_source_of_wealth_v1(_chart())
    assert result["source_scores"]["property_assets"] > 0


def test_shared_wealth_channel_uses_eighth_house_links():
    result = analyze_finance_source_of_wealth_v1(_chart())
    assert result["source_scores"]["inheritance_shared_wealth"] > 0


def test_no_financial_advice_language():
    result = analyze_finance_source_of_wealth_v1(_chart())
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "not financial advice" in text
    assert "does not recommend" in text


def test_insufficient_chart_is_declined():
    result = analyze_finance_source_of_wealth_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
