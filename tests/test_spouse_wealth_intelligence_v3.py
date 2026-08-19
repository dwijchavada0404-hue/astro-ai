from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3


def test_spouse_wealth_detection():
    questions = [
        "Will my spouse be wealthy?",
        "Will my spouse be financially stable?",
        "What will my future spouse's financial profile be?",
        "Will my spouse come from a wealthy family?",
        "Will my spouse own property assets?",
        "Will my spouse have international income?",
        "Will my spouse be good with money?",
        "Will my spouse earn through stock market income?",
    ]
    for question in questions:
        result = analyze_marriage_question_v3(question)
        assert result["primary_event"] == "spouse_wealth"
        assert result["query_mode"] == "single_event"


def test_spouse_profession_is_not_hijacked_by_wealth():
    assert (
        analyze_marriage_question_v3("Will my spouse work in finance?")["primary_event"]
        == "spouse_profession"
    )
    assert (
        analyze_marriage_question_v3("Will my spouse own a business?")["primary_event"]
        == "spouse_profession"
    )


def test_spouse_education_is_not_hijacked_by_wealth():
    assert (
        analyze_marriage_question_v3("Will my spouse have a finance degree?")["primary_event"]
        == "spouse_education"
    )
