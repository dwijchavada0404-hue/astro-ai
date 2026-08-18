from __future__ import annotations

from typing import Any

import pytest

from app.astrology.features.spouse_education_reasoning_v1 import (
    analyze_spouse_education_v1,
)


def _reference_chart() -> dict[str, Any]:
    return {
        "houses": {
            "1": {"sign": "Cancer", "lord": "Moon"},
            "2": {"sign": "Leo", "lord": "Sun"},
            "3": {"sign": "Virgo", "lord": "Mercury"},
            "4": {"sign": "Libra", "lord": "Venus"},
            "5": {"sign": "Scorpio", "lord": "Mars"},
            "6": {"sign": "Sagittarius", "lord": "Jupiter"},
            "7": {"sign": "Capricorn", "lord": "Saturn"},
            "8": {"sign": "Aquarius", "lord": "Saturn"},
            "9": {"sign": "Pisces", "lord": "Jupiter"},
            "10": {"sign": "Aries", "lord": "Mars"},
            "11": {"sign": "Taurus", "lord": "Venus"},
            "12": {"sign": "Gemini", "lord": "Mercury"},
        },
        "planets": {
            "Sun": {"house": 9, "sign": "Pisces"},
            "Moon": {"house": 9, "sign": "Pisces"},
            "Mars": {"house": 10, "sign": "Aries"},
            "Mercury": {"house": 3, "sign": "Virgo"},
            "Jupiter": {"house": 10, "sign": "Aries"},
            "Venus": {"house": 11, "sign": "Taurus"},
            "Saturn": {"house": 10, "sign": "Aries"},
            "Rahu": {"house": 12, "sign": "Gemini"},
            "Ketu": {"house": 6, "sign": "Sagittarius"},
        },
    }


def test_spouse_education_v1_basic_contract():
    result = analyze_spouse_education_v1(_reference_chart())
    assert result["available"] is True
    assert result["event"] == "spouse_education"
    assert result["model_version"] == "v1"
    assert isinstance(result["summary"], str)
    assert result["summary"]
    assert isinstance(result["confidence"], float)


def test_spouse_education_v1_derived_house_context():
    result = analyze_spouse_education_v1(_reference_chart())
    context = result["profile"]["chart_context"]
    assert context["formal_education_house"]["natal_house"] == 10
    assert context["intellect_house"]["natal_house"] == 11
    assert context["higher_education_house"]["natal_house"] == 3


def test_spouse_education_v1_has_ranked_themes():
    result = analyze_spouse_education_v1(_reference_chart())
    assert result["ranked_themes"]
    assert result["strongest_themes"]
    assert result["ranked_themes"][0]["relative_strength"] == 1.0


def test_spouse_education_v1_mercury_supports_analytical_theme():
    result = analyze_spouse_education_v1(_reference_chart())
    themes = {item["theme"] for item in result["ranked_themes"]}
    assert "analytical_commercial" in themes


def test_spouse_education_v1_jupiter_supports_academic_theme():
    result = analyze_spouse_education_v1(_reference_chart())
    themes = {item["theme"] for item in result["ranked_themes"]}
    assert "academic_advisory" in themes


def test_spouse_education_v1_technical_theme_from_mars():
    result = analyze_spouse_education_v1(_reference_chart())
    themes = {item["theme"] for item in result["ranked_themes"]}
    assert "technical_practical" in themes


def test_spouse_education_v1_indicator_sources_are_preserved():
    result = analyze_spouse_education_v1(_reference_chart())
    assert result["indicators"]
    assert all("factor" in item for item in result["indicators"])
    assert all("interpretation" in item for item in result["indicators"])


def test_spouse_education_v1_confidence_is_bounded():
    result = analyze_spouse_education_v1(_reference_chart())
    assert 0.50 <= result["confidence"] <= 0.88


def test_spouse_education_v1_missing_seventh_house():
    result = analyze_spouse_education_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
    assert result["event"] == "spouse_education"
    assert result["model_version"] == "v1"
    assert "reason" in result


def test_spouse_education_v1_missing_derived_house():
    chart = _reference_chart()
    chart["houses"].pop("10")
    result = analyze_spouse_education_v1(chart)
    assert result["available"] is False
    assert "education house" in result["reason"].lower()


def test_spouse_education_v1_rejects_non_dict_chart():
    with pytest.raises(ValueError, match="chart must be a dictionary"):
        analyze_spouse_education_v1([])
