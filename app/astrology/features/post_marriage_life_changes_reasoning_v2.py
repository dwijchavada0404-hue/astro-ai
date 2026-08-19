from __future__ import annotations

from typing import Any

from app.astrology.features.post_marriage_life_changes_reasoning_v1 import (
    analyze_post_marriage_life_changes_v1,
)


TARGETS = {
    "general": ("overall post-marriage life changes", ()),
    "relocation": ("relocation / geographic change", ("relocation",)),
    "career_shift": ("career or work-pattern change", ("career_shift",)),
    "financial_change": ("financial or resource change", ("financial_change",)),
    "lifestyle_change": ("lifestyle / domestic adjustment", ("lifestyle_change",)),
    "family_responsibility": ("family-responsibility expansion", ("family_responsibility",)),
    "international_exposure": ("international / cross-border exposure", ("international_exposure",)),
}


def _normalise(question: str) -> str:
    return " ".join(question.strip().lower().split())


def _detect_target(question: str) -> tuple[str, list[str]]:
    patterns = (
        ("international_exposure", ("abroad", "foreign country", "international", "overseas", "cross-border", "move countries")),
        ("relocation", ("relocate", "relocation", "move city", "move cities", "change city", "move after marriage")),
        ("career_shift", ("career change", "career shift", "job change", "work change", "profession change", "career after marriage")),
        ("financial_change", ("financial change", "finances change", "money change", "income change", "financially after marriage", "wealth after marriage")),
        ("family_responsibility", ("family responsibility", "family responsibilities", "responsibilities increase", "more responsibility")),
        ("lifestyle_change", ("lifestyle change", "life change", "daily life change", "domestic life", "home life change")),
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


def analyze_post_marriage_life_changes_v2(chart: dict[str, Any], question: str) -> dict[str, Any]:
    if not isinstance(question, str):
        raise ValueError("question must be a string.")
    normalised = _normalise(question)
    if not normalised:
        raise ValueError("question must not be empty.")

    natal = analyze_post_marriage_life_changes_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "post_marriage_life_changes",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised,
            "reason": natal.get("reason"),
            "natal_profile": natal,
        }

    target, matched = _detect_target(normalised)
    target_label, profiles = TARGETS[target]
    scores = natal.get("profile", {}).get("profile_scores", {})
    if target == "general":
        support_score = float(scores.get(natal.get("dominant_profile"), 0.0) or 0.0)
    else:
        support_score = max((float(scores.get(profile, 0.0) or 0.0) for profile in profiles), default=0.0)
    support_score = round(max(0.0, min(1.0, support_score)), 3)
    support_level, support_label = _support_level(support_score)
    confidence = round(min(0.90, max(0.50, float(natal.get("confidence", 0.60)) * 0.72 + support_score * 0.28)), 3)

    answer = natal.get("summary") if target == "general" else (
        f"The chart shows {support_level} symbolic support for {target_label} associated with marriage."
    )

    return {
        "available": True,
        "event": "post_marriage_life_changes",
        "model_version": "v2",
        "question": question,
        "normalised_question": normalised,
        "target": target,
        "target_label": target_label,
        "matched_keywords": matched,
        "support_score": support_score,
        "support_level": support_level,
        "support_label": support_label,
        "confidence": confidence,
        "answer": answer,
        "summary": answer,
        "limitation": natal.get("limitation"),
        "strongest_themes": natal.get("ranked_profiles", [])[:3],
        "evidence_count": len(natal.get("evidence", [])),
        "evidence": natal.get("evidence", []),
        "natal_profile": natal,
        "analysis": {
            "requested_target": target,
            "requested_profiles": list(profiles),
            "profile_scores": scores,
            "dominant_profile": natal.get("dominant_profile"),
        },
    }
