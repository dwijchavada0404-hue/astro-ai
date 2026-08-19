from __future__ import annotations

from typing import Any

from app.astrology.features.spouse_family_background_reasoning_v1 import (
    analyze_spouse_family_background_v1,
)


TARGET_LABELS = {
    "general": "General Family / Social Background",
    "traditional": "Traditional / Established Family",
    "educated_cultured": "Educated / Cultured Family",
    "business_family": "Business / Entrepreneurial Family",
    "professional_family": "Professional / Structured Family",
    "affluent_family": "Affluent / Resourceful Family",
    "international_family": "International / Modern Family",
    "creative_social_family": "Creative / Social Family",
}

TARGET_THEMES = {
    "traditional": {"traditional_respectable", "professional_structured"},
    "educated_cultured": {"educated_cultured", "traditional_respectable"},
    "business_family": {"business_commercial", "affluent_resourceful"},
    "professional_family": {"professional_structured", "educated_cultured"},
    "affluent_family": {"affluent_resourceful", "business_commercial", "traditional_respectable"},
    "international_family": {"international_modern", "business_commercial"},
    "creative_social_family": {"creative_social", "educated_cultured"},
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _normalise(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _detect_target(question: str) -> dict[str, Any]:
    q = _normalise(question)
    patterns = (
        ("business_family", ("business family", "entrepreneurial family", "family business", "business background")),
        ("professional_family", ("professional family", "family of professionals", "professional background")),
        ("affluent_family", ("affluent family", "wealthy family", "rich family", "well off family", "well-off family", "resourceful family")),
        ("international_family", ("international family", "foreign family", "multicultural family", "modern family", "global family")),
        ("educated_cultured", ("educated family", "cultured family", "academic family", "intellectual family")),
        ("creative_social_family", ("creative family", "artistic family", "social family", "fashion family", "media family")),
        ("traditional", ("traditional family", "conservative family", "established family", "respectable family", "orthodox family")),
    )
    for target, phrases in patterns:
        matched = [phrase for phrase in phrases if phrase in q]
        if matched:
            return {"target": target, "target_label": TARGET_LABELS[target], "matched_keywords": matched}
    return {"target": "general", "target_label": TARGET_LABELS["general"], "matched_keywords": []}


def _extract(v1: dict[str, Any], target: str) -> list[dict[str, Any]]:
    ranked = [_safe_dict(item) for item in _safe_list(v1.get("ranked_themes")) if isinstance(item, dict)]
    if target == "general":
        return ranked[:6]
    allowed = TARGET_THEMES.get(target, set())
    return [item for item in ranked if str(item.get("theme", "")) in allowed]


def _support(evidence: list[dict[str, Any]], target: str) -> float:
    if not evidence:
        return 0.18
    strengths = [_safe_float(item.get("relative_strength")) for item in evidence]
    strongest = max(strengths, default=0.0)
    average = sum(strengths) / len(strengths) if strengths else 0.0
    score = strongest * 0.68 + average * 0.20 + min(max(len(evidence) - 1, 0) * 0.045, 0.14)
    if target == "general":
        score += 0.06
    return round(_clamp(score, 0.0, 0.92), 3)


def _classify(score: float) -> tuple[str, str]:
    if score >= 0.72:
        return "strong_support", "Strong Support"
    if score >= 0.54:
        return "moderate_support", "Moderate Support"
    if score >= 0.34:
        return "mild_support", "Mild Support"
    return "limited_support", "Limited Support"


def analyze_spouse_family_background_v2(chart: dict[str, Any], question: str) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(question, str):
        raise ValueError("question must be a string.")
    normalised = _normalise(question)
    if not normalised:
        raise ValueError("question must not be empty.")

    target_data = _detect_target(question)
    target = str(target_data["target"])
    v1 = analyze_spouse_family_background_v1(chart)
    if not v1.get("available"):
        return {
            "available": False,
            "event": "spouse_family_background",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised,
            "target": target,
            "target_label": target_data["target_label"],
            "matched_keywords": target_data["matched_keywords"],
            "reason": v1.get("reason"),
            "natal_analysis": v1,
        }

    evidence = _extract(v1, target)
    support_score = _support(evidence, target)
    support_level, support_label = _classify(support_score)
    confidence = round(_clamp(_safe_float(v1.get("confidence"), 0.55) + min(len(evidence) * 0.025, 0.10), 0.50, 0.90), 3)
    themes = [str(item.get("label", "")) for item in evidence[:5] if item.get("label")]

    if target == "general":
        answer = (
            "The strongest spouse family-background themes point toward " + ", ".join(themes[:3]) + "."
            if themes else
            "The currently modelled factors do not produce a distinct spouse family-background profile."
        )
    else:
        label = str(target_data["target_label"]).lower()
        if support_level == "strong_support":
            answer = f"The chart gives relatively strong support for a {label}."
        elif support_level == "moderate_support":
            answer = f"The chart gives moderate support for a {label}."
        elif support_level == "mild_support":
            answer = f"The chart gives some support for a {label}, although it is not dominant."
        else:
            answer = f"The currently modelled indicators provide limited support for a {label}."
        if themes:
            answer += " The most relevant themes are " + ", ".join(themes[:3]) + "."

    limitation = (
        "This analysis describes broad symbolic family and social-background tendencies. It cannot reliably predict an exact caste, community, surname, family wealth, social status or specific relatives."
    )

    return {
        "available": True,
        "event": "spouse_family_background",
        "model_version": "v2",
        "question": question,
        "normalised_question": normalised,
        "target": target,
        "target_label": target_data["target_label"],
        "matched_keywords": target_data["matched_keywords"],
        "support_score": support_score,
        "support_level": support_level,
        "support_label": support_label,
        "confidence": confidence,
        "answer": answer,
        "summary": answer,
        "limitation": limitation,
        "strongest_themes": themes,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "natal_profile": _safe_dict(v1.get("profile")),
        "natal_analysis": v1,
    }
