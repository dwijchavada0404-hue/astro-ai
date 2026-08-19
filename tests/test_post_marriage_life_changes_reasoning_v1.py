import pytest

from app.astrology.features.post_marriage_life_changes_reasoning_v1 import (
    analyze_post_marriage_life_changes_v1,
)


def _chart(seventh_lord="Venus", seventh_lord_house=12):
    return {
        "houses": {
            "2": {"sign": "Taurus", "lord": "Venus"},
            "4": {"sign": "Cancer", "lord": "Moon"},
            "7": {"sign": "Libra", "lord": seventh_lord},
            "8": {"sign": "Scorpio", "lord": "Mars"},
            "10": {"sign": "Capricorn", "lord": "Saturn"},
            "11": {"sign": "Aquarius", "lord": "Saturn"},
            "12": {"sign": "Pisces", "lord": "Jupiter"},
        },
        "planets": {
            "Venus": {"house": seventh_lord_house, "sign": "Pisces"},
            "Moon": {"house": 7, "sign": "Libra"},
            "Mars": {"house": 2, "sign": "Taurus"},
            "Saturn": {"house": 7, "sign": "Libra"},
            "Jupiter": {"house": 9, "sign": "Sagittarius"},
            "Mercury": {"house": 10, "sign": "Capricorn"},
            "Rahu": {"house": 12, "sign": "Pisces"},
        },
    }


def test_v1_contract_and_summary():
    result = analyze_post_marriage_life_changes_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "post_marriage_life_changes"
    assert result["model_version"] == "v1"
    assert result["summary"]
    assert result["evidence"]
    assert 0 <= result["confidence"] <= 1


def test_v1_highlights_relocation_and_international_exposure():
    result = analyze_post_marriage_life_changes_v1(_chart())
    scores = result["profile"]["profile_scores"]
    assert scores["relocation"] > 0
    assert scores["international_exposure"] > 0


def test_v1_can_highlight_career_change():
    result = analyze_post_marriage_life_changes_v1(_chart(seventh_lord="Mercury", seventh_lord_house=10))
    assert result["profile"]["profile_scores"]["career_shift"] > 0


def test_v1_limitation_avoids_guarantees():
    result = analyze_post_marriage_life_changes_v1(_chart())
    limitation = result["limitation"].lower()
    assert "cannot guarantee" in limitation
    assert "relocation" in limitation
    assert "career" in limitation
    assert "timeline" in limitation


def test_v1_missing_seventh_lord_is_unavailable():
    result = analyze_post_marriage_life_changes_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
    assert result["event"] == "post_marriage_life_changes"


def test_v1_rejects_non_dict_chart():
    with pytest.raises(ValueError):
        analyze_post_marriage_life_changes_v1([])
