from __future__ import annotations

from typing import Any

from app.astrology.features.spouse_wealth_reasoning_v1 import analyze_spouse_wealth_v1


TARGET_LABELS = {
    "general": "General Financial Profile",
    "wealthy": "Affluent / Wealthy Background",
    "financially_stable": "Financial Stability",
    "business_wealth": "Business / Entrepreneurial Wealth",
    "professional_income": "Professional Income",
    "property_assets": "Property / Asset Orientation",
    "family_wealth": "Family Wealth / Inherited Resources",
    "international_income": "International Income",
    "finance_skill": "Financial / Analytical Money Skill",
    "speculative_income": "Variable / Speculative Income",
}

TARGET_THEMES = {
    "wealthy": {"wealth_accumulation", "family_resources", "stable_assets"},
    "financially_stable": {"stable_assets", "professional_income", "wealth_accumulation"},
    "business_wealth": {"business_commercial", "wealth_accumulation", "variable_speculative"},
    "professional_income": {"professional_income", "financial_analysis", "stable_assets"},
    "property_assets": {"stable_assets", "family_resources"},
    "family_wealth": {"family_resources", "stable_assets", "wealth_accumulation"},
    "international_income": {"international_income", "business_commercial"},
    "finance_skill": {"financial_analysis", "business_commercial", "professional_income"},
    "speculative_income": {"variable_speculative", "business_commercial", "international_income"},
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
        ("family_wealth", ("family wealth", "wealthy family", "rich family", "inherited wealth", "inheritance")),
        ("financially_stable", ("financially stable", "stable financially", "stable income", "money stable")),
        ("business_wealth", ("business family", "business wealth", "business income", "entrepreneurial wealth", "own business", "own a business")),
        ("professional_income", ("professional income", "salary", "salaried", "high earning professional", "professional earnings")),
        ("property_assets", ("property", "real estate", "assets", "asset rich", "asset-rich")),
        ("international_income", ("foreign income", "international income", "earn abroad", "income abroad", "overseas income")),
        ("finance_skill", ("good with money", "financially intelligent", "money management", "financial skill", "finance minded")),
        ("speculative_income", ("speculative", "trading income", "stock market", "variable income", "high risk income")),
        ("wealthy", ("wealthy", "rich", "affluent", "well off", "well-off", "financially strong")),
    )
    for target, words in patterns:
        matched = [word for word in words if word in q]
        if matched:
            return {"target": target, "target_label": TARGET_LABELS[target], "matched_keywords": matched}
    return {"target": "general", "target_label": TARGET_LABELS["general"], "matched_keywords": []}


def _extract_evidence(v1: dict[str, Any], target: str) -> list[dict[str, Any]]:
    ranked = [_safe_dict(item) for item in _safe_list(v1.get("ranked_themes")) if isinstance(item, dict)]
    if target == "general":
        return ranked[:6]
    allowed = TARGET_THEMES.get(target, set())
    return [item for item in ranked if str(item.get("theme", "")) in allowed]


def _support_score(evidence: list[dict[str, Any]], target: str) -> float:
    if not evidence:
        return 0.18
    strengths = [_safe_float(item.get("relative_strength")) for item in evidence]
    strongest = max(strengths, default=0.0)
    average = sum(strengths) / len(strengths) if strengths else 0.0
    breadth = min(max(len(evidence) - 1, 0) * 0.045, 0.14)
    score = strongest * 0.68 + average * 0.20 + breadth
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


def _confidence(v1: dict[str, Any], evidence: list[dict[str, Any]], target: str) -> float:
    value = _safe_float(v1.get("confidence"), 0.55) + min(len(evidence) * 0.025, 0.10)
    if target != "general" and not evidence:
        value = min(value, 0.58)
    return round(_clamp(value, 0.50, 0.90), 3)


def _answer(target: str, support_level: str, themes: list[str]) -> str:
    if target == "general":
        if not themes:
            return "The currently modelled factors do not produce a distinct spouse financial profile."
        return "The strongest spouse financial themes point toward " + ", ".join(themes[:3]) + "."
    label = TARGET_LABELS.get(target, target).lower()
    if support_level == "strong_support":
        text = f"The chart gives relatively strong support for {label}."
    elif support_level == "moderate_support":
        text = f"The chart gives moderate support for {label}."
    elif support_level == "mild_support":
        text = f"The chart gives some support for {label}, although it is not dominant."
    else:
        text = f"The currently modelled indicators provide limited support for {label}."
    if themes:
        text += " The most relevant themes are " + ", ".join(themes[:3]) + "."
    return text


def _limitation(target: str) -> str:
    if target == "wealthy":
        return (
            "Astrological wealth indicators cannot reliably predict an exact salary, net worth, social class or future asset value. "
            "The result should be read as a broad financial tendency."
        )
    if target == "international_income":
        return (
            "International-income indicators may manifest through foreign clients, multinational employers, overseas assignments or globally linked business rather than literal residence abroad."
        )
    return (
        "This analysis represents broad symbolic financial tendencies rather than a guaranteed income level, asset portfolio or financial outcome."
    )


def analyze_spouse_wealth_v2(chart: dict[str, Any], question: str) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(question, str):
        raise ValueError("question must be a string.")
    normalised = _normalise(question)
    if not normalised:
        raise ValueError("question must not be empty.")

    target_data = _detect_target(question)
    target = str(target_data["target"])
    v1 = analyze_spouse_wealth_v1(chart)
    if not v1.get("available"):
        return {
            "available": False,
            "event": "spouse_wealth",
            "model_version": "v2",
            "question": question,
            "normalised_question": normalised,
            "target": target,
            "target_label": target_data["target_label"],
            "matched_keywords": target_data["matched_keywords"],
            "reason": v1.get("reason"),
            "natal_analysis": v1,
        }

    evidence = _extract_evidence(v1, target)
    support_score = _support_score(evidence, target)
    support_level, support_label = _classify(support_score)
    confidence = _confidence(v1, evidence, target)
    themes = [str(item.get("label", "")) for item in evidence[:5] if item.get("label")]
    answer = _answer(target, support_level, themes)

    return {
        "available": True,
        "event": "spouse_wealth",
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
        "limitation": _limitation(target),
        "strongest_themes": themes,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "natal_profile": _safe_dict(v1.get("profile")),
        "natal_analysis": v1,
    }
