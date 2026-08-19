from __future__ import annotations

import re
from typing import Any

from app.astrology.features.spouse_age_profile_reasoning_v1 import (
    AGE_LABELS,
    analyze_spouse_age_profile_v1,
)


TARGET_LABELS = {
    "general_age_profile": "General Spouse Age / Maturity Profile",
    "older_spouse": "Older / More Mature Spouse",
    "younger_spouse": "Younger / More Youthful Spouse",
    "similar_age_spouse": "Similar-Age Spouse",
}

TARGET_TO_PROFILE = {
    "older_spouse": "older_mature",
    "younger_spouse": "younger_youthful",
    "similar_age_spouse": "similar_age",
}


def _normalise(question: str) -> str:
    return " ".join(question.strip().lower().split())


def _detect_target(question: str) -> tuple[str, list[str]]:
    patterns = (
        ("older_spouse", r"\b(?:older|elder|elderly|more mature|senior)\b"),
        ("younger_spouse", r"\b(?:younger|youthful|junior)\b"),
        ("similar_age_spouse", r"\b(?:same age|similar age|close in age|around my age|my age)\b"),
    )
    for target, pattern in patterns:
        matches = re.findall(pattern, question)
        if matches:
            return target, [str(value) for value in matches]
    return "general_age_profile", []


def _support_level(score: float) -> tuple[str, str]:
    if score >= 0.78:
        return "strong", "Strong Support"
    if score >= 0.58:
        return "moderate", "Moderate Support"
    if score >= 0.38:
        return "mixed", "Mixed / Conditional Support"
    return "weak", "Weak Support"


def analyze_spouse_age_profile_v2(chart: dict[str, Any], question: str) -> dict[str, Any]:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    normalised = _normalise(question)
    target, matched = _detect_target(normalised)
    natal = analyze_spouse_age_profile_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "spouse_age_profile",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised,
            "target": target,
            "target_label": TARGET_LABELS[target],
            "matched_keywords": matched,
            "reason": natal.get("reason"),
        }

    scores = natal.get("profile", {}).get("profile_scores", {})
    if target == "general_age_profile":
        dominant = str(natal.get("dominant_profile", "mixed"))
        support_score = float(scores.get(dominant, 0.50) or 0.50)
        requested_profile = dominant
    else:
        requested_profile = TARGET_TO_PROFILE[target]
        support_score = float(scores.get(requested_profile, 0.0) or 0.0)

    support_score = round(max(0.0, min(1.0, support_score)), 3)
    support_level, support_label = _support_level(support_score)
    confidence = round(max(0.50, min(0.90, float(natal.get("confidence", 0.60)) * 0.85 + 0.10)), 3)

    if target == "general_age_profile":
        answer = f"The chart leans most toward a {AGE_LABELS.get(requested_profile, requested_profile)}."
    else:
        answer = (
            f"The chart shows {support_label.lower()} for a {AGE_LABELS.get(requested_profile, requested_profile)}."
        )

    return {
        "available": True,
        "event": "spouse_age_profile",
        "model_version": "v2",
        "question": question,
        "normalised_question": normalised,
        "target": target,
        "target_label": TARGET_LABELS[target],
        "matched_keywords": matched,
        "requested_profile": requested_profile,
        "support_score": support_score,
        "support_level": support_level,
        "support_label": support_label,
        "confidence": confidence,
        "answer": answer,
        "summary": natal.get("summary"),
        "limitation": natal.get("limitation"),
        "strongest_themes": natal.get("ranked_profiles", [])[:3],
        "evidence_count": len(natal.get("evidence", [])),
        "evidence": natal.get("evidence", []),
        "natal_profile": natal.get("profile", {}),
        "analysis": natal,
    }
