from __future__ import annotations

from typing import Any


FAMILY_CHILDREN_THEMES = {
    "family_stability": "family continuity, support and stability of the family environment",
    "children_parenthood": "symbolic emphasis on children, parenting and nurturing responsibilities",
    "family_growth": "expansion or development of family responsibilities and bonds",
    "family_support": "support from family networks, elders or intergenerational relationships",
    "family_change": "changes in family structure, responsibilities or domestic dynamics",
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


def analyze_family_children_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess core natal Family & Children themes without inferring real-life facts.

    The 5th house/lord is the primary children/parenting axis, while the 2nd and 4th
    houses support family continuity and domestic bonds. The 9th/11th provide broader
    support/growth context and the 8th/12th may describe change or complexity. These
    are symbolic patterns only: this engine does not diagnose fertility or predict
    pregnancy, childbirth, number/sex of children, or guaranteed family outcomes.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "family_children",
            "model_version": "v1",
            "reason": "House data required for Family & Children reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in FAMILY_CHILDREN_THEMES}
    evidence: list[dict[str, Any]] = []

    fifth_lord, fifth_lord_house = _lord_house(chart, 5)
    if fifth_lord:
        scores["children_parenthood"] += 0.30
        scores["family_growth"] += 0.12
        evidence.append({"rule": "fifth_house_lord_available", "lord": fifth_lord})
        if fifth_lord_house in {1, 2, 4, 5, 9, 10, 11}:
            scores["children_parenthood"] += 0.24
            scores["family_growth"] += 0.18
            evidence.append({"rule": "fifth_lord_supportive_placement", "lord": fifth_lord, "house": fifth_lord_house})
        elif fifth_lord_house in {6, 8, 12}:
            scores["family_change"] += 0.16
            evidence.append({"rule": "fifth_lord_complex_placement", "lord": fifth_lord, "house": fifth_lord_house})

    for house_no, weight in ((2, 0.26), (4, 0.24), (5, 0.16), (9, 0.10)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {1, 2, 4, 5, 9, 10, 11}:
            scores["family_stability"] += weight
            evidence.append({"rule": "family_stability_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    for house_no, weight in ((5, 0.28), (2, 0.14), (9, 0.14), (11, 0.18)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {1, 2, 4, 5, 9, 11}:
            scores["family_growth"] += weight
            evidence.append({"rule": "family_growth_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    for house_no, weight in ((2, 0.22), (4, 0.22), (9, 0.20), (11, 0.16)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {1, 2, 4, 5, 9, 11}:
            scores["family_support"] += weight
            evidence.append({"rule": "family_support_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    for house_no, weight in ((4, 0.16), (5, 0.16), (8, 0.20), (12, 0.22)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {3, 6, 8, 12}:
            scores["family_change"] += weight
            evidence.append({"rule": "family_change_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    planet_nudges = {
        "Jupiter": ("children_parenthood", "family_growth", "family_support"),
        "Moon": ("family_stability", "children_parenthood"),
        "Venus": ("family_stability", "family_support"),
        "Sun": ("family_support",),
        "Saturn": ("family_stability", "family_change"),
    }
    for planet, themes in planet_nudges.items():
        ph = _planet_house(chart, planet)
        if ph in {1, 2, 4, 5, 9, 11}:
            for theme in themes:
                scores[theme] += 0.05
                evidence.append({"rule": "family_significator_support", "planet": planet, "house": ph, "theme": theme})

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant_theme, dominant_score = ranked[0]
    secondary_theme, secondary_score = ranked[1]
    confidence = round(min(0.94, 0.44 + 0.04 * len(evidence)), 2)

    return {
        "available": True,
        "event": "family_children",
        "model_version": "v1",
        "dominant_theme": dominant_theme,
        "dominant_theme_label": FAMILY_CHILDREN_THEMES[dominant_theme],
        "dominant_score": dominant_score,
        "secondary_theme": secondary_theme,
        "secondary_theme_label": FAMILY_CHILDREN_THEMES[secondary_theme],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [
            {"theme": theme, "label": FAMILY_CHILDREN_THEMES[theme], "score": score}
            for theme, score in ranked
        ],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": (
            "Known family, relationship and children milestones override predictive assumptions. Astrology may interpret "
            "confirmed history but must not infer pregnancy, childbirth, parenthood or another family event as fact without confirmation."
        ),
        "summary": (
            f"The strongest Family & Children theme is {FAMILY_CHILDREN_THEMES[dominant_theme]}, followed by "
            f"{FAMILY_CHILDREN_THEMES[secondary_theme]}."
        ),
        "limitation": (
            "This is symbolic astrological pattern analysis. It is not medical or fertility advice and does not predict or "
            "guarantee conception, pregnancy, childbirth, number or sex of children, adoption, or any family outcome."
        ),
    }
