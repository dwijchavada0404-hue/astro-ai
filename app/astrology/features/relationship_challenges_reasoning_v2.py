from __future__ import annotations

from typing import Any

from app.astrology.features.relationship_challenges_reasoning_v1 import (
    analyze_relationship_challenges_v1,
)


TARGETS = {
    "general": {
        "label": "overall relationship challenge / repair profile",
        "profiles": (),
    },
    "conflict": {
        "label": "conflict / intensity tendency",
        "profiles": ("conflict_intensity",),
    },
    "distance": {
        "label": "emotional distance / withdrawal tendency",
        "profiles": ("emotional_distance",),
    },
    "instability": {
        "label": "instability / unpredictability tendency",
        "profiles": ("instability",),
    },
    "delay_pressure": {
        "label": "commitment delay / pressure tendency",
        "profiles": ("delay_pressure",),
    },
    "repair": {
        "label": "repair / reconciliation capacity",
        "profiles": ("repair_capacity",),
    },
}


def _normalise(question: str) -> str:
    return " ".join(question.strip().lower().split())


def _detect_target(question: str) -> tuple[str, list[str]]:
    patterns = (
        ("repair", ("reconcile", "reconciliation", "repair", "recover", "work things out", "resolve conflict", "bounce back")),
        ("conflict", ("conflict", "fights", "fight a lot", "arguments", "argue a lot", "heated", "friction", "clashes")),
        ("distance", ("emotional distance", "emotionally distant", "withdraw", "withdrawal", "cold", "detached", "drift apart")),
        ("instability", ("unstable", "instability", "unpredictable", "ups and downs", "on and off", "volatile")),
        ("delay_pressure", ("delay in commitment", "commitment delay", "pressure around commitment", "marriage delay", "delayed marriage", "commitment pressure")),
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


def analyze_relationship_challenges_v2(chart: dict[str, Any], question: str) -> dict[str, Any]:
    if not isinstance(question, str):
        raise ValueError("question must be a string.")

    normalised = _normalise(question)
    if not normalised:
        raise ValueError("question must not be empty.")

    natal = analyze_relationship_challenges_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "relationship_challenges",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised,
            "reason": natal.get("reason"),
            "natal_profile": natal,
        }

    target, matched = _detect_target(normalised)
    target_data = TARGETS[target]
    profile_scores = natal.get("profile", {}).get("profile_scores", {})

    if target == "general":
        support_score = float(
            profile_scores.get(natal.get("dominant_challenge"), 0.0) or 0.0
        )
    else:
        support_score = max(
            (
                float(profile_scores.get(profile, 0.0) or 0.0)
                for profile in target_data["profiles"]
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
    elif target == "repair":
        answer = (
            f"The chart shows {support_level} symbolic support for "
            f"{target_data['label']}."
        )
    else:
        answer = (
            f"The chart shows {support_level} symbolic support for "
            f"{target_data['label']}. This should be read as a tendency, not as a prediction of a specific relationship outcome."
        )

    ranked = natal.get("ranked_profiles", [])
    strongest_themes = [
        {
            "profile": item.get("profile"),
            "label": item.get("label"),
            "strength": item.get("relative_strength"),
        }
        for item in ranked[:3]
    ]

    return {
        "available": True,
        "event": "relationship_challenges",
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
            "requested_profiles": list(target_data["profiles"]),
            "profile_scores": profile_scores,
            "dominant_challenge": natal.get("dominant_challenge"),
            "repair_capacity": natal.get("repair_capacity"),
        },
    }
