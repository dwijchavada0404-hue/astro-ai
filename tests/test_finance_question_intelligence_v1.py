import pytest

from app.astrology.features.finance_question_intelligence_v1 import analyze_finance_question_v1


@pytest.mark.parametrize(
    ("question", "intent"),
    [
        ("Will I become wealthy?", "wealth_potential"),
        ("How is my savings potential?", "income_savings"),
        ("Will I earn through business?", "business_wealth"),
        ("Are gains through my network indicated?", "gains_networks"),
        ("Is inheritance indicated in my chart?", "joint_assets_inheritance"),
        ("How is my long-term wealth growth?", "fortune_long_term_support"),
    ],
)
def test_targeted_finance_intents(question, intent):
    result = analyze_finance_question_v1(question)
    assert result["available"] is True
    assert result["event"] == "finance_wealth"
    assert result["primary_intent"] == intent
    assert result["requires_natal_engine"] is True


def test_finance_timing_is_detected_as_modifier():
    result = analyze_finance_question_v1("When is my strongest financial growth period?")
    assert result["available"] is True
    assert result["primary_intent"] == "fortune_long_term_support"
    assert result["timing_requested"] is True
    assert result["requires_timing_engine"] is True


def test_generic_money_timing_can_route_to_timing():
    result = analyze_finance_question_v1("When will my money situation improve?")
    assert result["available"] is True
    assert result["primary_intent"] == "finance_timing"
    assert result["requires_timing_engine"] is True


def test_unrelated_question_is_not_claimed():
    result = analyze_finance_question_v1("When will I get married?")
    assert result["available"] is False
    assert result["event"] == "unknown"
    assert result["primary_intent"] == "unknown"


def test_financial_safety_contract_is_explicit():
    result = analyze_finance_question_v1("Should I invest in stocks?")
    assert result["available"] is True
    assert result["safety"]["financial_advice_allowed"] is False
    assert result["safety"]["investment_instruction_allowed"] is False
    assert result["safety"]["guaranteed_return_language_allowed"] is False


def test_empty_question_rejected():
    with pytest.raises(ValueError):
        analyze_finance_question_v1("   ")
