from __future__ import annotations

from typing import Any


LOCATION_THEMES = {
    "rooted_home_base": "continuity, rootedness and stability of the primary home base",
    "domestic_relocation": "movement or relocation within the broader home environment",
    "foreign_exposure": "meaningful foreign, international or cross-cultural exposure",
    "long_distance_residence": "living materially away from the place of origin for an extended period",
    "foreign_settlement": "symbolic support for establishing a longer-term base outside the place of origin",
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


def analyze_location_settlement_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess natal location, relocation and foreign-settlement symbolism.

    The engine deliberately separates foreign exposure from actual long-term settlement.
    The 4th house/lord describes home base, the 3rd movement, the 9th long-distance and
    cross-cultural themes, and the 12th residence away from origin/foreign environments.
    No single planet or house is treated as proof of migration or citizenship.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "location_settlement",
            "model_version": "v1",
            "reason": "House data required for Location & Foreign Settlement reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in LOCATION_THEMES}
    evidence: list[dict[str, Any]] = []

    fourth_lord, fourth_house = _lord_house(chart, 4)
    if fourth_lord:
        scores["rooted_home_base"] += 0.24
        if fourth_house in {1, 2, 4, 5, 10, 11}:
            scores["rooted_home_base"] += 0.34
            evidence.append({"rule": "fourth_lord_rooted_placement", "lord": fourth_lord, "house": fourth_house})
        if fourth_house in {3, 7, 9, 12}:
            scores["domestic_relocation"] += 0.20
            scores["long_distance_residence"] += 0.16
            evidence.append({"rule": "fourth_lord_mobility_placement", "lord": fourth_lord, "house": fourth_house})
        if fourth_house in {9, 12}:
            scores["foreign_settlement"] += 0.24
            evidence.append({"rule": "fourth_lord_long_distance_link", "lord": fourth_lord, "house": fourth_house})

    # House-lord links are weighted evidence, not deterministic yoga declarations.
    for house_no, weight in ((3, 0.20), (9, 0.26), (12, 0.30)):
        lord, placed = _lord_house(chart, house_no)
        if lord and placed in {3, 7, 9, 12}:
            scores["domestic_relocation"] += weight * 0.55
            scores["foreign_exposure"] += weight
            evidence.append({"rule": "mobility_foreign_house_link", "house": house_no, "lord": lord, "lord_house": placed})
        if lord and placed in {4, 9, 12}:
            scores["long_distance_residence"] += weight * 0.72
            evidence.append({"rule": "residence_distance_house_link", "house": house_no, "lord": lord, "lord_house": placed})

    # Settlement requires combined home-base + long-distance evidence rather than 12th-house activation alone.
    if fourth_house in {9, 12}:
        scores["foreign_settlement"] += 0.18
    ninth_lord, ninth_house = _lord_house(chart, 9)
    twelfth_lord, twelfth_house = _lord_house(chart, 12)
    if ninth_lord and ninth_house in {4, 9, 12}:
        scores["foreign_settlement"] += 0.18
    if twelfth_lord and twelfth_house in {4, 9, 12}:
        scores["foreign_settlement"] += 0.20
    if ninth_lord and twelfth_lord and ninth_house in {9, 12} and twelfth_house in {4, 9, 12}:
        scores["foreign_settlement"] += 0.12
        evidence.append({"rule": "combined_long_distance_residence_support", "ninth_lord": ninth_lord, "twelfth_lord": twelfth_lord})

    planet_nudges = {
        "Rahu": ("foreign_exposure", "long_distance_residence"),
        "Ketu": ("domestic_relocation",),
        "Moon": ("rooted_home_base", "domestic_relocation"),
        "Saturn": ("long_distance_residence",),
        "Jupiter": ("foreign_exposure",),
        "Mercury": ("foreign_exposure",),
    }
    for planet, themes in planet_nudges.items():
        placed = _planet_house(chart, planet)
        if placed in {3, 4, 7, 9, 12}:
            for theme in themes:
                scores[theme] += 0.06
                evidence.append({"rule": "location_significator_nudge", "planet": planet, "house": placed, "theme": theme})

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant, dominant_score = ranked[0]
    secondary, secondary_score = ranked[1]
    confidence = round(min(0.94, 0.44 + 0.035 * len(evidence)), 2)

    return {
        "available": True,
        "event": "location_settlement",
        "model_version": "v1",
        "dominant_theme": dominant,
        "dominant_theme_label": LOCATION_THEMES[dominant],
        "dominant_score": dominant_score,
        "secondary_theme": secondary,
        "secondary_theme_label": LOCATION_THEMES[secondary],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [
            {"theme": theme, "label": LOCATION_THEMES[theme], "score": score}
            for theme, score in ranked
        ],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": (
            "Known residence, relocation, migration and citizenship facts override astrological inference. A foreign or mobility "
            "signature may describe travel, international work, study, family links or temporary residence and must not be "
            "silently converted into a claim of permanent foreign settlement."
        ),
        "summary": (
            f"The strongest Location & Settlement theme is {LOCATION_THEMES[dominant]}, followed by "
            f"{LOCATION_THEMES[secondary]}."
        ),
        "limitation": (
            "This is symbolic astrological pattern analysis. It does not guarantee travel, visa approval, immigration status, "
            "citizenship, relocation, permanent residence or settlement in any country or city."
        ),
    }
