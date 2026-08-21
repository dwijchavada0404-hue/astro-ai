from __future__ import annotations

from typing import Any


PURPOSE_THEMES = {
    "self_development": "identity development, self-authorship and personal growth",
    "creative_expression": "creative contribution, expression and meaning-making",
    "service_contribution": "useful contribution, responsibility and service to others",
    "knowledge_guidance": "learning, teaching, mentoring, philosophy and guidance",
    "public_contribution": "visible contribution through work, leadership or responsibility",
    "inner_growth": "reflection, spiritual inquiry, detachment and inner development",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _safe_dict(chart.get("houses"))
    return _safe_dict(houses.get(str(number)) or houses.get(number))


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _lord_house(chart: dict[str, Any], house_no: int) -> tuple[str | None, int | None]:
    lord = _house(chart, house_no).get("lord")
    if not isinstance(lord, str) or not lord:
        return None, None
    return lord, _planet_house(chart, lord)


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_purpose_personal_growth_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess symbolic purpose and growth themes without declaring a fixed destiny.

    The 1st house anchors self-development, the 5th creative expression, the 6th useful
    contribution/service, the 9th meaning/learning/guidance, the 10th public contribution,
    and the 12th inner/reflective development. Planetary significators are supporting
    evidence only; no planet is treated as proof of a single life purpose or vocation.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "purpose_personal_growth",
            "model_version": "v1",
            "reason": "House data required for Purpose & Personal Growth reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in PURPOSE_THEMES}
    evidence: list[dict[str, Any]] = []

    house_theme_weights = {
        1: (("self_development", 0.34),),
        5: (("creative_expression", 0.30), ("self_development", 0.10)),
        6: (("service_contribution", 0.28),),
        9: (("knowledge_guidance", 0.34), ("inner_growth", 0.10)),
        10: (("public_contribution", 0.34), ("service_contribution", 0.08)),
        12: (("inner_growth", 0.32),),
    }
    supportive_houses = {1, 2, 3, 5, 6, 9, 10, 11, 12}
    for house_no, theme_weights in house_theme_weights.items():
        lord, placed = _lord_house(chart, house_no)
        if not lord:
            continue
        for theme, base_weight in theme_weights:
            scores[theme] += base_weight * 0.60
            if placed in supportive_houses:
                scores[theme] += base_weight * 0.40
                evidence.append({"rule": "purpose_house_lord_support", "house": house_no, "lord": lord, "lord_house": placed, "theme": theme})

    significator_themes = {
        "Sun": ("self_development", "public_contribution"),
        "Jupiter": ("knowledge_guidance", "service_contribution"),
        "Saturn": ("service_contribution", "public_contribution"),
        "Mercury": ("knowledge_guidance", "creative_expression"),
        "Venus": ("creative_expression",),
        "Moon": ("self_development", "inner_growth"),
        "Ketu": ("inner_growth",),
        "Mars": ("public_contribution",),
    }
    for planet, themes in significator_themes.items():
        placed = _planet_house(chart, planet)
        if placed in supportive_houses:
            for theme in themes:
                scores[theme] += 0.07
                evidence.append({"rule": "purpose_significator_support", "planet": planet, "house": placed, "theme": theme})

    first_lord, first_house = _lord_house(chart, 1)
    ninth_lord, ninth_house = _lord_house(chart, 9)
    tenth_lord, tenth_house = _lord_house(chart, 10)
    twelfth_lord, twelfth_house = _lord_house(chart, 12)
    if first_lord and ninth_lord and first_house in {5, 9, 10, 12} and ninth_house in {1, 5, 9, 10, 12}:
        scores["self_development"] += 0.10
        scores["knowledge_guidance"] += 0.10
        evidence.append({"rule": "identity_meaning_link", "first_lord": first_lord, "ninth_lord": ninth_lord})
    if ninth_lord and tenth_lord and ninth_house in {1, 5, 9, 10, 11} and tenth_house in {5, 9, 10, 11}:
        scores["knowledge_guidance"] += 0.08
        scores["public_contribution"] += 0.10
        evidence.append({"rule": "meaning_public_contribution_link", "ninth_lord": ninth_lord, "tenth_lord": tenth_lord})
    if ninth_lord and twelfth_lord and ninth_house in {9, 12} and twelfth_house in {9, 12}:
        scores["inner_growth"] += 0.12
        evidence.append({"rule": "meaning_inner_growth_link", "ninth_lord": ninth_lord, "twelfth_lord": twelfth_lord})

    scores = {key: _bounded(value) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant, dominant_score = ranked[0]
    secondary, secondary_score = ranked[1]
    margin = dominant_score - secondary_score
    confidence = round(min(0.94, 0.44 + 0.035 * len(evidence) + 0.12 * max(0.0, margin)), 2)

    return {
        "available": True,
        "event": "purpose_personal_growth",
        "model_version": "v1",
        "dominant_theme": dominant,
        "dominant_theme_label": PURPOSE_THEMES[dominant],
        "dominant_score": dominant_score,
        "secondary_theme": secondary,
        "secondary_theme_label": PURPOSE_THEMES[secondary],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [
            {"theme": theme, "label": PURPOSE_THEMES[theme], "score": score}
            for theme, score in ranked
        ],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": (
            "Known values, choices, responsibilities, interests and lived experience override astrological assumptions. "
            "Astrology may describe symbolic growth themes but must not declare a fixed destiny, mandatory vocation or singular life purpose."
        ),
        "summary": (
            f"The strongest Purpose & Personal Growth theme is {PURPOSE_THEMES[dominant]}, followed by "
            f"{PURPOSE_THEMES[secondary]}."
        ),
        "limitation": (
            "This is symbolic reflective analysis, not proof of destiny, spiritual status, moral worth or a required career/life path. "
            "Important life decisions should remain grounded in the person's actual values, opportunities, obligations and preferences."
        ),
    }
