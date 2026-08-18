from __future__ import annotations

from typing import Any

from app.astrology.features.spouse_education_reasoning_v1 import (
    analyze_spouse_education_v1,
)


EDUCATION_TARGET_LABELS = {
    "general": "General Education / Intellectual Profile",
    "higher_education": "Higher Education",
    "professional_qualification": "Professional Qualification",
    "analytical_intellect": "Analytical / Commercial Intellect",
    "technical_education": "Technical / Engineering Education",
    "finance_commerce": "Finance / Commerce Education",
    "law_advisory": "Law / Advisory Education",
    "creative_education": "Creative / Design Education",
    "international_education": "International Education",
    "research_specialisation": "Research / Specialist Education",
}

TARGET_THEMES = {
    "higher_education": {
        "academic_advisory",
        "research_specialist",
        "international_modern",
    },
    "professional_qualification": {
        "structured_professional",
        "academic_advisory",
        "analytical_commercial",
        "management_leadership",
    },
    "analytical_intellect": {
        "analytical_commercial",
        "academic_advisory",
    },
    "technical_education": {
        "technical_practical",
        "structured_professional",
        "research_specialist",
    },
    "finance_commerce": {
        "analytical_commercial",
        "structured_professional",
        "management_leadership",
    },
    "law_advisory": {
        "academic_advisory",
        "structured_professional",
        "management_leadership",
    },
    "creative_education": {
        "creative_social",
        "analytical_commercial",
    },
    "international_education": {
        "international_modern",
        "academic_advisory",
    },
    "research_specialisation": {
        "research_specialist",
        "academic_advisory",
        "technical_practical",
    },
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


def _normalise_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _detect_target(question: str) -> dict[str, Any]:
    normalised = _normalise_text(question)
    target_patterns = (
        (
            "higher_education",
            (
                "highly educated",
                "higher education",
                "postgraduate",
                "post graduate",
                "masters degree",
                "master's degree",
                "doctorate",
                "phd",
            ),
        ),
        (
            "professional_qualification",
            (
                "professional qualification",
                "professionally qualified",
                "chartered accountant",
                "ca qualification",
                "mba",
                "professional degree",
            ),
        ),
        (
            "technical_education",
            (
                "engineer",
                "engineering",
                "technical education",
                "technical degree",
                "computer science",
                "software degree",
                "technology degree",
            ),
        ),
        (
            "finance_commerce",
            (
                "finance education",
                "finance degree",
                "commerce degree",
                "commerce background",
                "accounting",
                "banking education",
                "economics",
            ),
        ),
        (
            "law_advisory",
            (
                "law degree",
                "study law",
                "legal education",
                "lawyer",
                "advocate",
            ),
        ),
        (
            "creative_education",
            (
                "study design",
                "design degree",
                "design education",
                "creative education",
                "arts degree",
                "fashion degree",
                "media degree",
            ),
        ),
        (
            "international_education",
            (
                "study abroad",
                "studied abroad",
                "educated abroad",
                "foreign university",
                "international education",
                "overseas education",
            ),
        ),
        (
            "research_specialisation",
            (
                "research",
                "specialisation",
                "specialization",
                "specialist education",
                "research degree",
            ),
        ),
        (
            "analytical_intellect",
            (
                "intelligent",
                "intellectual",
                "analytical",
                "smart",
                "academic minded",
                "academic-minded",
                "learning style",
            ),
        ),
    )

    for target, patterns in target_patterns:
        matched = [pattern for pattern in patterns if pattern in normalised]
        if matched:
            return {
                "target": target,
                "target_label": EDUCATION_TARGET_LABELS[target],
                "matched_keywords": matched,
            }

    return {
        "target": "general",
        "target_label": EDUCATION_TARGET_LABELS["general"],
        "matched_keywords": [],
    }


def _extract_target_evidence(
    v1_result: dict[str, Any],
    target: str,
) -> list[dict[str, Any]]:
    ranked = [
        _safe_dict(item)
        for item in _safe_list(v1_result.get("ranked_themes"))
        if isinstance(item, dict)
    ]
    if target == "general":
        return ranked[:6]

    allowed = TARGET_THEMES.get(target, set())
    return [item for item in ranked if str(item.get("theme", "")) in allowed]


def _calculate_support_score(
    evidence: list[dict[str, Any]],
    target: str,
) -> float:
    if not evidence:
        return 0.20

    strengths = [_safe_float(item.get("relative_strength")) for item in evidence]
    strongest = max(strengths, default=0.0)
    average = sum(strengths) / len(strengths) if strengths else 0.0
    breadth_bonus = min(max(len(evidence) - 1, 0) * 0.045, 0.14)
    score = strongest * 0.68 + average * 0.20 + breadth_bonus
    if target == "general":
        score += 0.06
    return round(_clamp(score, 0.0, 0.92), 3)


def _classify_support(score: float) -> tuple[str, str]:
    if score >= 0.72:
        return "strong_support", "Strong Support"
    if score >= 0.54:
        return "moderate_support", "Moderate Support"
    if score >= 0.34:
        return "mild_support", "Mild Support"
    return "limited_support", "Limited Support"


def _calculate_confidence(
    v1_result: dict[str, Any],
    evidence: list[dict[str, Any]],
    target: str,
) -> float:
    base = _safe_float(v1_result.get("confidence"), 0.55)
    evidence_bonus = min(len(evidence) * 0.025, 0.10)
    confidence = base + evidence_bonus
    if target != "general" and not evidence:
        confidence = min(confidence, 0.58)
    return round(_clamp(confidence, 0.50, 0.90), 3)


def _strongest_themes(evidence: list[dict[str, Any]]) -> list[str]:
    return [
        str(item.get("label", ""))
        for item in evidence[:5]
        if item.get("label")
    ]


def _build_answer(
    target: str,
    support_level: str,
    themes: list[str],
) -> str:
    if target == "general":
        if themes:
            return (
                "The strongest spouse education themes point toward "
                + ", ".join(themes[:3])
                + "."
            )
        return (
            "The currently modelled factors do not produce a sufficiently distinct spouse "
            "education or intellectual profile."
        )

    label = EDUCATION_TARGET_LABELS.get(target, target)
    if support_level == "strong_support":
        opening = f"The chart gives relatively strong support for {label.lower()}."
    elif support_level == "moderate_support":
        opening = f"The chart gives moderate support for {label.lower()}."
    elif support_level == "mild_support":
        opening = f"The chart gives some support for {label.lower()}, although it is not dominant."
    else:
        opening = f"The currently modelled indicators provide limited support for {label.lower()}."

    if themes:
        opening += " The most relevant themes are " + ", ".join(themes[:3]) + "."
    return opening


def _build_limitation(target: str) -> str:
    if target in {"higher_education", "professional_qualification"}:
        return (
            "This engine describes symbolic educational tendencies; it cannot reliably predict "
            "an exact degree, institution, credential or level of formal qualification."
        )
    if target == "international_education":
        return (
            "International-learning indicators can also manifest as multicultural exposure, "
            "foreign-linked institutions or globally oriented study rather than literal overseas education."
        )
    return (
        "Spouse education analysis represents broad symbolic learning and intellectual tendencies "
        "rather than a guaranteed academic field or qualification."
    )


def analyze_spouse_education_v2(
    chart: dict[str, Any],
    question: str,
) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(question, str):
        raise ValueError("question must be a string.")

    normalised_question = _normalise_text(question)
    if not normalised_question:
        raise ValueError("question must not be empty.")

    target_data = _detect_target(question)
    target = str(target_data["target"])
    v1_result = analyze_spouse_education_v1(chart)

    if not v1_result.get("available"):
        return {
            "available": False,
            "event": "spouse_education",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised_question,
            "target": target,
            "target_label": target_data["target_label"],
            "matched_keywords": target_data["matched_keywords"],
            "reason": v1_result.get("reason"),
            "natal_analysis": v1_result,
        }

    evidence = _extract_target_evidence(v1_result, target)
    support_score = _calculate_support_score(evidence, target)
    support_level, support_label = _classify_support(support_score)
    confidence = _calculate_confidence(v1_result, evidence, target)
    strongest_themes = _strongest_themes(evidence)
    answer = _build_answer(target, support_level, strongest_themes)
    limitation = _build_limitation(target)

    return {
        "available": True,
        "event": "spouse_education",
        "model_version": "v2",
        "question": question,
        "normalised_question": normalised_question,
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
        "strongest_themes": strongest_themes,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "natal_profile": _safe_dict(v1_result.get("profile")),
        "natal_analysis": v1_result,
    }
