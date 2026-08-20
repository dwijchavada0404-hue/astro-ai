from __future__ import annotations

from typing import Any


CAREER_THEMES = {
    "career_strength": "overall professional strength and visibility",
    "service_employment": "structured employment, service and organisational work",
    "leadership_authority": "leadership, authority, recognition and responsibility",
    "independent_enterprise": "independent work, entrepreneurship and self-directed activity",
    "skills_communication": "analysis, communication, commerce and adaptable skill-based work",
    "gains_progression": "career gains, advancement, networks and professional rewards",
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


def analyze_career_profession_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess core natal Career & Profession themes.

    The foundation emphasises the 10th house/lord, then integrates 6th-house
    employment/service symbolism, 2nd-house earning continuity, 11th-house gains,
    3rd/7th-house independence and enterprise, and relevant planetary support.
    It describes symbolic tendencies rather than guaranteeing employment, status,
    promotion, income, business success or professional outcomes.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "career_profession",
            "model_version": "v1",
            "reason": "House data required for career reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in CAREER_THEMES}
    evidence: list[dict[str, Any]] = []

    # 10th house is the primary profession/status axis.
    tenth_lord, tenth_lord_house = _lord_house(chart, 10)
    if tenth_lord:
        scores["career_strength"] += 0.34
        evidence.append({"rule": "tenth_house_lord_available", "lord": tenth_lord})
        if tenth_lord_house in {1, 2, 5, 9, 10, 11}:
            scores["career_strength"] += 0.28
            scores["leadership_authority"] += 0.14
            evidence.append({"rule": "tenth_lord_supportive_placement", "lord": tenth_lord, "house": tenth_lord_house})
        elif tenth_lord_house in {3, 6, 7}:
            scores["career_strength"] += 0.18
            evidence.append({"rule": "tenth_lord_active_work_placement", "lord": tenth_lord, "house": tenth_lord_house})
        elif tenth_lord_house in {8, 12}:
            scores["career_strength"] += 0.08
            evidence.append({"rule": "tenth_lord_complex_placement", "lord": tenth_lord, "house": tenth_lord_house})

    # Employment/service structure: 6th + 10th + Saturn.
    for house_no, weight in ((6, 0.26), (10, 0.22), (2, 0.12)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {2, 6, 10, 11}:
            scores["service_employment"] += weight
            evidence.append({"rule": "employment_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Leadership/recognition: 10th, 9th, 1st and Sun/Saturn support.
    for house_no, weight in ((10, 0.24), (9, 0.16), (1, 0.12)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {1, 5, 9, 10, 11}:
            scores["leadership_authority"] += weight
            evidence.append({"rule": "leadership_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Independent enterprise: 3rd initiative + 7th commerce + 10th profession + 11th scale.
    for house_no, weight in ((3, 0.22), (7, 0.26), (10, 0.16), (11, 0.14)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {1, 3, 7, 10, 11}:
            scores["independent_enterprise"] += weight
            evidence.append({"rule": "enterprise_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Skills/communication: Mercury plus 2nd/3rd/5th/10th links.
    for house_no, weight in ((2, 0.14), (3, 0.20), (5, 0.18), (10, 0.14)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {2, 3, 5, 6, 10, 11}:
            scores["skills_communication"] += weight
            evidence.append({"rule": "skills_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Career gains/progression: 10th + 11th + 2nd + 9th.
    for house_no, weight in ((11, 0.30), (10, 0.20), (2, 0.14), (9, 0.12)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {2, 9, 10, 11}:
            scores["gains_progression"] += weight
            evidence.append({"rule": "career_gain_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Natural significator support is deliberately modest.
    planet_nudges = {
        "Sun": ("leadership_authority", "career_strength"),
        "Saturn": ("service_employment", "career_strength", "gains_progression"),
        "Mercury": ("skills_communication", "independent_enterprise"),
        "Mars": ("independent_enterprise", "leadership_authority"),
        "Jupiter": ("leadership_authority", "gains_progression"),
    }
    for planet, themes in planet_nudges.items():
        ph = _planet_house(chart, planet)
        if ph in {1, 2, 3, 5, 6, 7, 9, 10, 11}:
            for theme in themes:
                scores[theme] += 0.07
                evidence.append({"rule": "career_significator_support", "planet": planet, "house": ph, "theme": theme})

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant_theme, dominant_score = ranked[0]
    secondary_theme, secondary_score = ranked[1]

    confidence = round(min(0.95, 0.45 + 0.04 * len(evidence)), 2)
    return {
        "available": True,
        "event": "career_profession",
        "model_version": "v1",
        "dominant_theme": dominant_theme,
        "dominant_theme_label": CAREER_THEMES[dominant_theme],
        "dominant_score": dominant_score,
        "secondary_theme": secondary_theme,
        "secondary_theme_label": CAREER_THEMES[secondary_theme],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [
            {"theme": theme, "label": CAREER_THEMES[theme], "score": score}
            for theme, score in ranked
        ],
        "confidence": confidence,
        "evidence": evidence,
        "summary": (
            f"The strongest career theme is {CAREER_THEMES[dominant_theme]}, followed by "
            f"{CAREER_THEMES[secondary_theme]}."
        ),
        "limitation": (
            "This is symbolic astrological pattern analysis. It does not guarantee employment, promotion, "
            "professional status, business success, salary, recognition or any career outcome."
        ),
    }
