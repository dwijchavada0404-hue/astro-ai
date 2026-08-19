import pytest

from app.astrology.features.spouse_family_background_reasoning_v2 import (
    analyze_spouse_family_background_v2,
)


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
        ("What kind of family will my spouse come from?", "general"),
        ("Will my spouse come from a traditional family?", "traditional"),
        ("Will my spouse come from an educated family?", "educated_cultured"),
        ("Will my spouse come from a business family?", "business_family"),
        ("Will my spouse come from a professional family?", "professional_family"),
        ("Will my spouse come from a wealthy family?", "affluent_family"),
        ("Will my spouse come from an international family?", "international_family"),
        ("Will my spouse come from a creative family?", "creative_social_family"),
    ],
)
def test_target_detection(question: str, target: str):
    assert analyze_spouse_family_background_v2(_chart(), question)["target"] == target


def test_v2_contract():
    result = analyze_spouse_family_background_v2(_chart(), "What kind of family will my spouse come from?")
    for key in (
        "event", "model_version", "question", "normalised_question", "target",
        "target_label", "matched_keywords", "support_score", "support_level",
        "support_label", "confidence", "answer", "summary", "limitation",
        "strongest_themes", "evidence_count", "evidence", "natal_profile", "natal_analysis",
    ):
        assert key in result


def test_scores_bounded():
    result = analyze_spouse_family_background_v2(_chart(), "Will my spouse come from a traditional family?")
    assert 0.0 <= result["support_score"] <= 0.92
    assert 0.50 <= result["confidence"] <= 0.90


def test_limitation_avoids_exact_social_identity_claims():
    text = analyze_spouse_family_background_v2(_chart(), "What family will my spouse come from?")["limitation"].lower()
    assert "caste" in text
    assert "community" in text


def test_missing_chart_returns_unavailable():
    assert analyze_spouse_family_background_v2({"houses": {}, "planets": {}}, "What family will my spouse come from?")["available"] is False


def test_invalid_inputs():
    with pytest.raises(ValueError):
        analyze_spouse_family_background_v2([], "test")
    with pytest.raises(ValueError):
        analyze_spouse_family_background_v2(_chart(), None)
    with pytest.raises(ValueError):
        analyze_spouse_family_background_v2(_chart(), "   ")
