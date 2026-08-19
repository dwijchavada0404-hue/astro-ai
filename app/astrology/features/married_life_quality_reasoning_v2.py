from __future__ import annotations

import re
from typing import Any

from app.astrology.features.married_life_quality_reasoning_v1 import (
    QUALITY_LABELS,
    analyze_married_life_quality_v1,
)


TARGET_LABELS = {
    "general_quality": "General Married-Life Quality",
    "harmony": "Marital Harmony / Cooperation",
    "stability": "Marital Stability / Endurance",
    "passion": "Passion / Intensity",
    "variability": "Variability / Unconventional Dynamics",
}

TARGET_TO_PROFILE = {
    "harmony": "harmonious",
    "stability": "stable",
    "passion": "passionate",
    "variability": "variable",
}


def _normalise(question: str) -> str:
    return " ".join(question.strip().lower().split())


def _detect_target(question: str) -> tuple[str, list[str]]:
    patterns = (
        ("harmony", r"\b(?:happy marriage|harmonious|harmony|supportive marriage|peaceful marriage|cooperative marriage|good married life)\b"),
        ("stability", r"\b(?:stable|stable marriage|stability|long lasting marriage|lasting marriage|enduring marriage|marriage last)\b"),
        ("passion", r"\b(?:passionate marriage|passion|intense relationship|strong chemistry|romantic intensity)\b"),
        ("variability", r"\b(?:unstable marriage|ups and downs|on and off|unconventional marriage|variable relationship|unpredictable relationship)\b"),
    )
    for target, pattern in patterns:
        matches = re.findall(pattern, question)
        if matches:
            return target, [str(value) for value in matches]
    return "general_quality", []


def _support_level(score: float) -> tuple[str, str]:
    if score >= 0.78:
        return "strong", "Strong Support"
    if score >= 0.58:
        return "moderate", "Moderate Support"
    if score >= 0.38:
        return "mixed", "Mixed / Conditional Support"
    return "weak", "Weak Support"


def analyze_married_life_quality_v2(chart: dict[str, Any], question: str) -> dict[str, Any]:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    normalised = _normalise(question)
    target, matched = _detect_target(normalised)
    natal = analyze_married_life_quality_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "married_life_quality",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised,
            "target": target,
            "target_label": TARGET_LABELS[target],
            "matched_keywords": matched,
            "reason": natal.get("reason"),
        }

    scores = natal.get("profile", {}).get("profile_scores", {})
    if target == "general_quality":
        requested_profile = str(natal.get("dominant_profile", "mixed"))
        support_score = float(scores.get(requested_profile, 0.50) or 0.50)
    else:
        requested_profile = TARGET_TO_PROFILE[target]
        support_score = float(scores.get(requested_profile, 0.0) or 0.0)

    support_score = round(max(0.0, min(1.0, support_score)), 3)
    support_level, support_label = _support_level(support_score)
    confidence = round(max(0.50, min(0.90, float(natal.get("confidence", 0.60)) * 0.85 + 0.10)), 3)

    if target == "general_quality":
        answer = f"The chart leans most toward a {QUALITY_LABELS.get(requested_profile, requested_profile)}."
    else:
        answer = f"The chart shows {support_label.lower()} for a {QUALITY_LABELS.get(requested_profile, requested_profile)}."

    return {
        "available": True,
        "event": "married_life_quality",
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
