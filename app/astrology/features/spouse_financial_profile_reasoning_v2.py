from __future__ import annotations

from typing import Any

from app.astrology.features.spouse_financial_profile_reasoning_v1 import (
    analyze_spouse_financial_profile_v1,
)


TARGETS = {
    "general": {
        "label": "overall spouse financial / resource profile",
        "profiles": (),
    },
    "affluent": {
        "label": "financially comfortable / resourceful spouse tendency",
        "profiles": ("affluent",),
    },
    "stable": {
        "label": "financially stable / prudent spouse tendency",
        "profiles": ("stable",),
    },
    "entrepreneurial": {
        "label": "entrepreneurial / commercially active spouse tendency",
        "profiles": ("entrepreneurial",),
    },
    "variable": {
        "label": "variable / unconventional financial pattern",
        "profiles": ("variable",),
    },
}


def _normalise(question: str) -> str:
    return " ".join(question.strip().lower().split())


def _detect_target(question: str) -> tuple[str, list[str]]:
    patterns = (
        ("affluent", ("rich", "wealthy", "affluent", "well off", "well-off", "financially comfortable", "resourceful")),
        ("stable", ("financially stable", "financial stability", "stable financially", "prudent", "secure financially", "financially secure")),
        ("entrepreneurial", ("entrepreneur", "entrepreneurial", "business owner", "own business", "commercially active")),
        ("variable", ("variable income", "unstable income", "unconventional income", "unconventional earning", "financial ups and downs")),
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


def analyze_spouse_financial_profile_v2(chart: dict[str, Any], question: str) -> dict[str, Any]:
    if not isinstance(question, str):
        raise ValueError("question must be a string.")
    normalised = _normalise(question)
    if not normalised:
        raise ValueError("question must not be empty.")

    natal = analyze_spouse_financial_profile_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "spouse_financial_profile",
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
        support_score = float(profile_scores.get(natal.get("dominant_profile"), 0.0) or 0.0)
    else:
        support_score = max((float(profile_scores.get(profile, 0.0) or 0.0) for profile in target_data["profiles"]), default=0.0)

    support_score = round(max(0.0, min(1.0, support_score)), 3)
    support_level, support_label = _support_level(support_score)
    confidence = round(min(0.90, max(0.50, float(natal.get("confidence", 0.60)) * 0.72 + support_score * 0.28)), 3)

    if target == "general":
        answer = natal.get("summary")
    else:
        answer = f"The chart shows {support_level} symbolic support for a {target_data['label']}."

    ranked = natal.get("ranked_profiles", [])
    strongest_themes = [
        {"profile": item.get("profile"), "label": item.get("label"), "strength": item.get("relative_strength")}
        for item in ranked[:3]
    ]

    return {
        "available": True,
        "event": "spouse_financial_profile",
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
            "dominant_profile": natal.get("dominant_profile"),
        },
    }
