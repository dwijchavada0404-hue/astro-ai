from __future__ import annotations

from typing import Any


WEALTH_HOUSES = {
    2: "income_savings",
    5: "speculation_creativity",
    8: "joint_assets_inheritance",
    9: "fortune_long_term_support",
    11: "gains_networks",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _safe_dict(chart.get("houses"))
    return _safe_dict(houses.get(str(number)) or houses.get(number))


def _planet(chart: dict[str, Any], name: str) -> dict[str, Any]:
    return _safe_dict(_safe_dict(chart.get("planets")).get(name))


def _lord_house(chart: dict[str, Any], house_number: int) -> tuple[str | None, int | None]:
    house = _house(chart, house_number)
    lord = house.get("lord")
    if not isinstance(lord, str) or not lord:
        return None, None
    placement = _planet(chart, lord)
    try:
        placed_house = int(placement.get("house"))
    except (TypeError, ValueError):
        placed_house = None
    return lord, placed_house


def analyze_finance_wealth_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Natal financial-pattern foundation for AstroAI.

    This engine describes symbolic earning, saving, gains, investment/speculation,
    shared-resource and long-term prosperity themes. It does not promise wealth,
    investment returns, or a fixed financial outcome.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    houses = _safe_dict(chart.get("houses"))
    planets = _safe_dict(chart.get("planets"))
    if not houses or not planets:
        return {
            "available": False,
            "event": "finance_wealth",
            "model_version": "v1",
            "reason": "Insufficient natal chart data for finance/wealth analysis.",
        }

    scores = {
        "income_savings": 0.0,
        "gains_networks": 0.0,
        "speculation_creativity": 0.0,
        "joint_assets_inheritance": 0.0,
        "fortune_long_term_support": 0.0,
    }
    evidence: list[dict[str, Any]] = []

    for number, theme in WEALTH_HOUSES.items():
        lord, placed_house = _lord_house(chart, number)
        if lord is None:
            continue
        scores[theme] += 0.25
        evidence.append({
            "rule": "wealth_house_lord_available",
            "house": number,
            "theme": theme,
            "lord": lord,
            "lord_house": placed_house,
        })

        if placed_house in {2, 5, 9, 10, 11}:
            scores[theme] += 0.35
            evidence.append({
                "rule": "wealth_lord_supportive_house",
                "house": number,
                "lord": lord,
                "lord_house": placed_house,
                "theme": theme,
            })
        elif placed_house in {6, 8, 12}:
            scores[theme] += 0.12
            evidence.append({
                "rule": "wealth_lord_complex_house",
                "house": number,
                "lord": lord,
                "lord_house": placed_house,
                "theme": theme,
            })

    # Natural financial significators: Jupiter for expansion/wisdom, Venus for
    # resources/comfort, Mercury for commerce/calculation, Saturn for accumulation.
    significators = {
        "Jupiter": "fortune_long_term_support",
        "Venus": "income_savings",
        "Mercury": "gains_networks",
        "Saturn": "income_savings",
    }
    for planet_name, theme in significators.items():
        placement = _planet(chart, planet_name)
        if not placement:
            continue
        try:
            ph = int(placement.get("house"))
        except (TypeError, ValueError):
            ph = None
        if ph in {2, 5, 9, 10, 11}:
            scores[theme] += 0.25
            evidence.append({
                "rule": "financial_significator_support",
                "planet": planet_name,
                "house": ph,
                "theme": theme,
            })

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant_theme, dominant_score = ranked[0]

    labels = {
        "income_savings": "earning and savings potential",
        "gains_networks": "gains through networks, opportunities and scaling",
        "speculation_creativity": "creative/speculative financial activity",
        "joint_assets_inheritance": "shared assets, inheritance or partner-linked resources",
        "fortune_long_term_support": "long-term financial growth and prosperity support",
    }

    confidence = round(min(0.9, 0.5 + len(evidence) * 0.025), 3)
    summary = (
        f"The strongest natal financial theme is {labels[dominant_theme]}. "
        "Other financial areas may still be active, but should be read comparatively rather than as guarantees."
    )

    return {
        "available": True,
        "event": "finance_wealth",
        "model_version": "v1",
        "dominant_theme": dominant_theme,
        "dominant_score": dominant_score,
        "theme_scores": scores,
        "ranked_themes": [
            {"theme": theme, "score": score, "label": labels[theme]}
            for theme, score in ranked
        ],
        "confidence": confidence,
        "summary": summary,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "limitation": (
            "This is an astrological pattern analysis, not financial advice and not a guarantee of income, wealth, "
            "investment performance, inheritance, or future financial outcomes."
        ),
    }
