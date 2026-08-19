from __future__ import annotations

from typing import Any

from app.astrology.features.marriage_compatibility_dynamics_reasoning_v1 import (
    analyze_marriage_compatibility_dynamics_v1,
)


TARGETS = {
    "general": {
        "label": "overall compatibility / partner dynamics profile",
        "dimensions": (),
    },
    "emotional_attunement": {
        "label": "emotional attunement / sensitivity",
        "dimensions": ("emotional_attunement",),
    },
    "communication_flow": {
        "label": "communication flow / mutual understanding",
        "dimensions": ("communication_flow",),
    },
    "shared_values": {
        "label": "shared values / alignment",
        "dimensions": ("shared_values",),
    },
    "chemistry": {
        "label": "chemistry / attraction",
        "dimensions": ("chemistry",),
    },
    "stability": {
        "label": "stability / long-term cooperation",
        "dimensions": ("stability",),
    },
    "independence": {
        "label": "independence / need for space",
        "dimensions": ("independence",),
    },
    "friction": {
        "label": "friction / adjustment pressure",
        "dimensions": ("friction",),
    },
}


def _normalise(question: str) -> str:
    return " ".join(question.strip().lower().split())


def _detect_target(question: str) -> tuple[str, list[str]]:
    patterns = (
        (
            "emotional_attunement",
            (
                "emotionally compatible",
                "emotional compatibility",
                "emotionally understand",
                "emotional understanding",
                "sensitive to each other",
                "emotional bond",
                "emotional connection",
            ),
        ),
        (
            "communication_flow",
            (
                "communicate well",
                "communication",
                "understand each other",
                "mutual understanding",
                "talk things through",
                "communication compatibility",
            ),
        ),
        (
            "shared_values",
            (
                "shared values",
                "same values",
                "values align",
                "aligned values",
                "similar beliefs",
                "life goals align",
                "same goals",
            ),
        ),
        (
            "chemistry",
            (
                "chemistry",
                "attraction",
                "romantic spark",
                "physical attraction",
                "romantic compatibility",
                "passion",
            ),
        ),
        (
            "stability",
            (
                "stable relationship",
                "stable marriage",
                "long term",
                "long-term",
                "lasting relationship",
                "lasting marriage",
                "cooperate long term",
            ),
        ),
        (
            "independence",
            (
                "need space",
                "need for space",
                "independence",
                "independent partner",
                "personal freedom",
                "too much space",
            ),
        ),
        (
            "friction",
            (
                "friction",
                "adjustment pressure",
                "adjustment issues",
                "compatibility issues",
                "clash",
                "clashes",
                "tension",
            ),
        ),
    )
    for target, keywords in patterns:
        matched = [keyword for keyword in keywords if keyword in question]
        if matched:
            return target, matched
    return "general", []


def _support_level(score: float) -> tuple[str, str]:
    if score >= 0.75:
        return "strong", "Strong symbolic support"
    if score >= 0.50:
        return "moderate", "Moderate symbolic support"
    if score >= 0.25:
        return "limited", "Limited symbolic support"
    return "weak", "Weak symbolic support"


def analyze_marriage_compatibility_dynamics_v2(
    chart: dict[str, Any],
    question: str,
) -> dict[str, Any]:
    if not isinstance(question, str):
        raise ValueError("question must be a string.")

    normalised = _normalise(question)
    if not normalised:
        raise ValueError("question must not be empty.")

    natal = analyze_marriage_compatibility_dynamics_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "marriage_compatibility_dynamics",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised,
            "reason": natal.get("reason"),
            "natal_profile": natal,
        }

    target, matched = _detect_target(normalised)
    target_data = TARGETS[target]
    dimension_scores = natal.get("profile", {}).get("dimension_scores", {})

    if target == "general":
        dominant = natal.get("dominant_dimension")
        support_score = float(dimension_scores.get(dominant, 0.0) or 0.0)
    else:
        support_score = max(
            (
                float(dimension_scores.get(dimension, 0.0) or 0.0)
                for dimension in target_data["dimensions"]
            ),
            default=0.0,
        )

    support_score = round(max(0.0, min(1.0, support_score)), 3)
    support_level, support_label = _support_level(support_score)

    confidence = round(
        min(
            0.90,
            max(
                0.50,
                float(natal.get("confidence", 0.60)) * 0.72
                + support_score * 0.28,
            ),
        ),
        3,
    )

    if target == "general":
        answer = natal.get("summary")
    elif target == "friction":
        answer = (
            f"The chart shows {support_level} symbolic emphasis on "
            f"{target_data['label']}. This describes possible adjustment themes, not a prediction that conflict or incompatibility must occur."
        )
    else:
        answer = (
            f"The chart shows {support_level} symbolic support for "
            f"{target_data['label']}. This is a one-chart tendency profile rather than a verdict on compatibility with a specific person."
        )

    ranked = natal.get("ranked_dimensions", [])
    strongest_themes = [
        {
            "dimension": item.get("dimension"),
            "label": item.get("label"),
            "strength": item.get("relative_strength"),
        }
        for item in ranked[:3]
    ]

    return {
        "available": True,
        "event": "marriage_compatibility_dynamics",
        "model_version": "v2",
        "question": question,
        "normalised_question": normalised,
        "target": target,
        "target_label": target_data["label"],
        "matched_keywords": matched,
        "support_score": support_score,
        "support_level": support_level,
        "support_label": support_label,
        "confidence": confidence,
        "answer": answer,
        "summary": answer,
        "limitation": natal.get("limitation"),
        "strongest_themes": strongest_themes,
        "evidence_count": len(natal.get("evidence", [])),
        "evidence": natal.get("evidence", []),
        "natal_profile": natal,
        "analysis": {
            "requested_target": target,
            "requested_dimensions": list(target_data["dimensions"]),
            "dimension_scores": dimension_scores,
            "dominant_dimension": natal.get("dominant_dimension"),
            "dominant_label": natal.get("dominant_label"),
        },
    }
