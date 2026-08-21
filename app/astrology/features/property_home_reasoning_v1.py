from __future__ import annotations

from typing import Any


PROPERTY_HOME_THEMES = {
    "home_stability": "residential stability, rootedness and continuity of home base",
    "property_acquisition": "symbolic support for acquiring or establishing property",
    "asset_accumulation": "long-term accumulation of tangible home/property assets",
    "home_comfort": "domestic comfort, belonging and supportive living environment",
    "relocation_change": "residential movement, relocation or changes of home base",
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


def analyze_property_home_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess core natal Property & Home themes.

    The 4th house/lord is the primary home/property axis. Supporting evidence uses
    the 2nd/11th houses for resources and accumulation, 9th for broader support,
    and 3rd/12th for movement or residence change. Planetary significators provide
    only modest nudges. Scores describe symbolic tendencies, not ownership facts.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "property_home",
            "model_version": "v1",
            "reason": "House data required for Property & Home reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in PROPERTY_HOME_THEMES}
    evidence: list[dict[str, Any]] = []

    fourth_lord, fourth_lord_house = _lord_house(chart, 4)
    if fourth_lord:
        scores["home_stability"] += 0.32
        scores["home_comfort"] += 0.18
        evidence.append({"rule": "fourth_house_lord_available", "lord": fourth_lord})
        if fourth_lord_house in {1, 2, 4, 5, 9, 10, 11}:
            scores["home_stability"] += 0.26
            scores["property_acquisition"] += 0.20
            evidence.append({"rule": "fourth_lord_supportive_placement", "lord": fourth_lord, "house": fourth_lord_house})
        elif fourth_lord_house in {3, 7, 12}:
            scores["relocation_change"] += 0.24
            evidence.append({"rule": "fourth_lord_mobility_placement", "lord": fourth_lord, "house": fourth_lord_house})
        elif fourth_lord_house in {6, 8}:
            scores["home_stability"] += 0.06
            evidence.append({"rule": "fourth_lord_complex_placement", "lord": fourth_lord, "house": fourth_lord_house})

    for house_no, weight in ((4, 0.24), (2, 0.18), (11, 0.18), (9, 0.10)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {1, 2, 4, 5, 9, 10, 11}:
            scores["property_acquisition"] += weight
            evidence.append({"rule": "property_support_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    for house_no, weight in ((2, 0.24), (4, 0.20), (11, 0.24), (9, 0.10)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {2, 4, 9, 10, 11}:
            scores["asset_accumulation"] += weight
            evidence.append({"rule": "property_asset_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    for house_no, weight in ((4, 0.30), (1, 0.12), (2, 0.12)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {1, 2, 4, 5, 9, 11}:
            scores["home_comfort"] += weight
            evidence.append({"rule": "home_comfort_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    for house_no, weight in ((3, 0.18), (4, 0.22), (12, 0.28), (9, 0.10)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {3, 7, 9, 12}:
            scores["relocation_change"] += weight
            evidence.append({"rule": "residence_change_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    planet_nudges = {
        "Venus": ("home_comfort", "property_acquisition"),
        "Mars": ("property_acquisition", "asset_accumulation"),
        "Moon": ("home_stability", "home_comfort"),
        "Jupiter": ("property_acquisition", "asset_accumulation"),
        "Saturn": ("home_stability", "asset_accumulation"),
        "Rahu": ("relocation_change",),
    }
    for planet, themes in planet_nudges.items():
        ph = _planet_house(chart, planet)
        if ph in {1, 2, 4, 9, 10, 11, 12}:
            for theme in themes:
                scores[theme] += 0.06
                evidence.append({"rule": "property_significator_support", "planet": planet, "house": ph, "theme": theme})

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant_theme, dominant_score = ranked[0]
    secondary_theme, secondary_score = ranked[1]
    confidence = round(min(0.95, 0.45 + 0.04 * len(evidence)), 2)

    return {
        "available": True,
        "event": "property_home",
        "model_version": "v1",
        "dominant_theme": dominant_theme,
        "dominant_theme_label": PROPERTY_HOME_THEMES[dominant_theme],
        "dominant_score": dominant_score,
        "secondary_theme": secondary_theme,
        "secondary_theme_label": PROPERTY_HOME_THEMES[secondary_theme],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [
            {"theme": theme, "label": PROPERTY_HOME_THEMES[theme], "score": score}
            for theme, score in ranked
        ],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": (
            "Known residence or property ownership facts override predictive assumptions. Astrology may interpret "
            "confirmed milestones but must not infer that property was bought, sold or inherited without confirmation."
        ),
        "summary": (
            f"The strongest Property & Home theme is {PROPERTY_HOME_THEMES[dominant_theme]}, followed by "
            f"{PROPERTY_HOME_THEMES[secondary_theme]}."
        ),
        "limitation": (
            "This is symbolic astrological pattern analysis. It does not guarantee property ownership, purchase, sale, "
            "inheritance, relocation, investment returns, financing approval or residential stability."
        ),
    }
