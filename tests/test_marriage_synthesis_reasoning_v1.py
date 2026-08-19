import pytest

from app.astrology.features.marriage_synthesis_reasoning_v1 import (
    synthesize_marriage_profile_v1,
)


def _component(event, answer, confidence=0.7, support_score=None):
    data = {
        "available": True,
        "event": event,
        "event_label": event.replace("_", " ").title(),
        "model_version": "v2",
        "answer": answer,
        "confidence": confidence,
    }
    if support_score is not None:
        data["support_score"] = support_score
    return data


def test_v1_synthesis_contract_and_sections():
    result = synthesize_marriage_profile_v1(
        {
            "spouse_traits": _component("spouse_traits", "Partner profile shows maturity and loyalty.", 0.82),
            "married_life_quality": _component("married_life_quality", "Marriage quality has supportive themes.", 0.78),
            "post_marriage_life_changes": _component("post_marriage_life_changes", "Relocation is a notable post-marriage theme.", 0.68),
        }
    )
    assert result["available"] is True
    assert result["event"] == "marriage_synthesis"
    assert result["model_version"] == "v1"
    assert result["component_count"] == 3
    section_names = {section["section"] for section in result["sections"]}
    assert "spouse_profile" in section_names
    assert "married_life" in section_names
    assert "post_marriage" in section_names


def test_v1_orders_strongest_themes_by_confidence():
    result = synthesize_marriage_profile_v1(
        {
            "spouse_traits": _component("spouse_traits", "Traits.", 0.61),
            "spouse_profession": _component("spouse_profession", "Profession.", 0.88),
            "spouse_education": _component("spouse_education", "Education.", 0.72),
        }
    )
    assert result["strongest_themes"][0]["event"] == "spouse_profession"
    assert result["headline"] == "Profession."


def test_v1_ignores_unavailable_or_empty_components():
    result = synthesize_marriage_profile_v1(
        {
            "spouse_traits": {"available": False, "event": "spouse_traits", "reason": "missing"},
            "spouse_profession": _component("spouse_profession", "Career profile is structured.", 0.75),
            "spouse_wealth": {"available": True, "event": "spouse_wealth", "answer": ""},
        }
    )
    assert result["component_count"] == 1
    assert result["strongest_themes"][0]["event"] == "spouse_profession"


def test_v1_detects_mixed_relationship_signals_without_cancelling_them():
    result = synthesize_marriage_profile_v1(
        {
            "marriage_compatibility_dynamics": _component(
                "marriage_compatibility_dynamics", "Compatibility has supportive patterns.", 0.76, 0.72
            ),
            "relationship_challenges": _component(
                "relationship_challenges", "Adjustment pressure is also meaningful.", 0.74, 0.69
            ),
        }
    )
    assert any(tension["type"] == "mixed_relationship_signals" for tension in result["tensions"])
    married_life = next(section for section in result["sections"] if section["section"] == "married_life")
    assert len(married_life["items"]) == 2


def test_v1_detects_quality_with_challenges():
    result = synthesize_marriage_profile_v1(
        {
            "married_life_quality": _component("married_life_quality", "Supportive marriage potential.", 0.8, 0.75),
            "relationship_challenges": _component("relationship_challenges", "Stress periods may require repair.", 0.72, 0.62),
        }
    )
    assert any(tension["type"] == "quality_with_challenges" for tension in result["tensions"])


def test_v1_preserves_source_components():
    source = _component("spouse_age_profile", "Maturity may be noticeable.", 0.66)
    result = synthesize_marriage_profile_v1({"spouse_age_profile": source})
    assert result["components"]["spouse_age_profile"] == source


def test_v1_returns_unavailable_for_no_usable_components():
    result = synthesize_marriage_profile_v1({})
    assert result["available"] is False
    assert result["component_count"] == 0


def test_v1_rejects_non_dictionary_input():
    with pytest.raises(ValueError):
        synthesize_marriage_profile_v1([])


def test_v1_limitation_is_non_deterministic():
    result = synthesize_marriage_profile_v1(
        {"spouse_traits": _component("spouse_traits", "Partner traits show a calm tone.", 0.7)}
    )
    limitation = result["limitation"].lower()
    assert "does not create new evidence" in limitation
    assert "probabilistic" in limitation
