import pytest

from app.astrology.features.spouse_wealth_reasoning_v2 import analyze_spouse_wealth_v2


def _chart() -> dict:
    houses = {
        str(i): {"sign": sign, "lord": lord}
        for i, (sign, lord) in enumerate(
            [
                ("Aries", "Mars"), ("Taurus", "Venus"), ("Gemini", "Mercury"),
                ("Cancer", "Moon"), ("Leo", "Sun"), ("Virgo", "Mercury"),
                ("Libra", "Venus"), ("Scorpio", "Mars"), ("Sagittarius", "Jupiter"),
                ("Capricorn", "Saturn"), ("Aquarius", "Saturn"), ("Pisces", "Jupiter"),
            ],
            start=1,
        )
    }
    planets = {
        "Sun": {"house": 5, "sign": "Leo"},
        "Moon": {"house": 4, "sign": "Cancer"},
        "Mars": {"house": 8, "sign": "Scorpio"},
        "Mercury": {"house": 6, "sign": "Virgo"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Venus": {"house": 7, "sign": "Libra"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
        "Ketu": {"house": 5, "sign": "Leo"},
    }
    return {"houses": houses, "planets": planets}


@pytest.mark.parametrize(
    "question,target",
    [
        ("Will my spouse be wealthy?", "wealthy"),
        ("Will my spouse be financially stable?", "financially_stable"),
        ("Will my spouse come from a wealthy family?", "family_wealth"),
        ("Will my spouse own a business?", "business_wealth"),
        ("Will my spouse have a high professional income?", "professional_income"),
        ("Will my spouse own property?", "property_assets"),
        ("Will my spouse earn abroad?", "international_income"),
        ("Will my spouse be good with money?", "finance_skill"),
        ("Will my spouse earn through stock market trading income?", "speculative_income"),
        ("What will my spouse's financial profile be?", "general"),
    ],
)
def test_target_detection(question: str, target: str):
    result = analyze_spouse_wealth_v2(_chart(), question)
    assert result["target"] == target


def test_v2_contract():
    result = analyze_spouse_wealth_v2(_chart(), "Will my spouse be wealthy?")
    required = (
        "event", "model_version", "question", "normalised_question", "target",
        "target_label", "matched_keywords", "support_score", "support_level",
        "support_label", "confidence", "answer", "summary", "limitation",
        "strongest_themes", "evidence_count", "evidence", "natal_profile", "natal_analysis",
    )
    for key in required:
        assert key in result


def test_support_score_bounded():
    result = analyze_spouse_wealth_v2(_chart(), "Will my spouse be rich?")
    assert 0.0 <= result["support_score"] <= 0.92


def test_confidence_bounded():
    result = analyze_spouse_wealth_v2(_chart(), "Will my spouse own property?")
    assert 0.50 <= result["confidence"] <= 0.90


def test_answer_nonempty():
    result = analyze_spouse_wealth_v2(_chart(), "Will my spouse be financially stable?")
    assert result["answer"]
    assert result["summary"] == result["answer"]


def test_general_has_evidence():
    result = analyze_spouse_wealth_v2(_chart(), "What is my spouse's financial profile?")
    assert result["target"] == "general"
    assert result["evidence_count"] > 0


def test_wealth_limitation_avoids_exact_networth_claim():
    result = analyze_spouse_wealth_v2(_chart(), "Will my spouse be wealthy?")
    assert "net worth" in result["limitation"].lower()


def test_international_limitation_is_contextual():
    result = analyze_spouse_wealth_v2(_chart(), "Will my spouse have foreign income?")
    assert "foreign" in result["limitation"].lower()


def test_missing_chart_data_returns_unavailable():
    chart = _chart()
    del chart["houses"]["7"]
    result = analyze_spouse_wealth_v2(chart, "Will my spouse be wealthy?")
    assert result["available"] is False
    assert result["event"] == "spouse_wealth"


def test_invalid_question_type():
    with pytest.raises(ValueError):
        analyze_spouse_wealth_v2(_chart(), None)


def test_empty_question():
    with pytest.raises(ValueError):
        analyze_spouse_wealth_v2(_chart(), "   ")
