from __future__ import annotations

from typing import Any


TRAVEL_THEMES = {
    "short_journeys": "short-distance movement, local travel and recurring day-to-day mobility",
    "long_distance_travel": "long-distance journeys and travel materially away from the usual base",
    "international_exposure": "foreign, international or cross-cultural travel exposure",
    "work_study_travel": "travel linked symbolically with work, learning or skill development",
    "recurring_mobility": "a repeated pattern of movement, commuting or multiple journeys",
    "travel_adaptability": "adaptability to movement, changing environments and travel routines",
}


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _d(chart.get("houses"))
    return _d(houses.get(str(number)) or houses.get(number))


def _planet_house(chart: dict[str, Any], name: str) -> int | None:
    try:
        return int(_d(_d(chart.get("planets")).get(name)).get("house"))
    except (TypeError, ValueError):
        return None


def _lord_house(chart: dict[str, Any], number: int) -> tuple[str | None, int | None]:
    lord = _house(chart, number).get("lord")
    if not isinstance(lord, str) or not lord:
        return None, None
    return lord, _planet_house(chart, lord)


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_travel_journeys_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess travel and journey symbolism without converting it into relocation or settlement claims."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _d(chart.get("houses")) or not _d(chart.get("planets")):
        return {"available": False, "event": "travel_journeys", "model_version": "v1", "reason": "Usable house and planetary data are required."}

    third_lord, third_house = _lord_house(chart, 3)
    ninth_lord, ninth_house = _lord_house(chart, 9)
    twelfth_lord, twelfth_house = _lord_house(chart, 12)
    sixth_lord, sixth_house = _lord_house(chart, 6)
    tenth_lord, tenth_house = _lord_house(chart, 10)

    short = .24 + (.24 if third_lord and third_house in {1, 3, 5, 7, 9, 11} else 0) + (.10 if _planet_house(chart, "Mercury") in {3, 7, 9, 11} else 0) + (.08 if _planet_house(chart, "Moon") in {3, 7, 9} else 0)
    long_distance = .24 + (.26 if ninth_lord and ninth_house in {1, 3, 7, 9, 12} else 0) + (.12 if _planet_house(chart, "Jupiter") in {3, 7, 9, 12} else 0) + (.08 if _planet_house(chart, "Moon") in {9, 12} else 0)
    international = .20 + (.24 if twelfth_lord and twelfth_house in {3, 7, 9, 12} else 0) + (.18 if ninth_lord and ninth_house in {9, 12} else 0) + (.12 if _planet_house(chart, "Rahu") in {3, 7, 9, 12} else 0) + (.08 if _planet_house(chart, "Jupiter") in {9, 12} else 0)
    work_study = .20 + (.14 if sixth_lord and sixth_house in {3, 9, 10, 12} else 0) + (.14 if tenth_lord and tenth_house in {3, 9, 12} else 0) + (.12 if _planet_house(chart, "Mercury") in {3, 9, 10, 12} else 0) + (.10 if _planet_house(chart, "Jupiter") in {3, 9, 10, 12} else 0)
    recurring = .22 + (.20 if third_lord and third_house in {3, 6, 7, 9, 11, 12} else 0) + (.12 if _planet_house(chart, "Mercury") in {3, 6, 7, 11} else 0) + (.10 if _planet_house(chart, "Rahu") in {3, 7, 9, 12} else 0) + (.08 if _planet_house(chart, "Moon") in {3, 7, 9, 12} else 0)
    adaptability = .24 + (.16 if _planet_house(chart, "Mercury") in {1, 3, 7, 9, 11} else 0) + (.14 if _planet_house(chart, "Moon") in {1, 3, 7, 9, 11} else 0) + (.10 if _planet_house(chart, "Jupiter") in {3, 9, 11} else 0)

    scores = {
        "short_journeys": _b(short),
        "long_distance_travel": _b(long_distance),
        "international_exposure": _b(international),
        "work_study_travel": _b(work_study),
        "recurring_mobility": _b(recurring),
        "travel_adaptability": _b(adaptability),
    }
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant, dominant_score = ranked[0]
    evidence = [
        {"factor": "third_house_mobility", "lord": third_lord, "lord_house": third_house, "interpretation": "The 3rd house is the primary axis for short journeys and recurring movement."},
        {"factor": "ninth_house_distance", "lord": ninth_lord, "lord_house": ninth_house, "interpretation": "The 9th house contributes long-distance, cross-cultural and extended-journey symbolism."},
        {"factor": "twelfth_house_foreign_exposure", "lord": twelfth_lord, "lord_house": twelfth_house, "interpretation": "The 12th house can contribute foreign-environment exposure, but is not proof of travel or settlement."},
        {"factor": "work_study_context", "sixth_lord": sixth_lord, "tenth_lord": tenth_lord, "interpretation": "6th and 10th house links provide secondary context for work-linked travel; Mercury/Jupiter provide modest learning and exchange context."},
    ]
    confidence = _b(.42 + .10*bool(third_lord) + .10*bool(ninth_lord) + .08*bool(twelfth_lord) + .18*dominant_score)
    return {
        "available": True,
        "event": "travel_journeys",
        "model_version": "v1",
        "theme_scores": scores,
        "dominant_theme": dominant,
        "dominant_theme_label": TRAVEL_THEMES[dominant],
        "dominant_score": dominant_score,
        "ranked_themes": [{"theme": key, "label": TRAVEL_THEMES[key], "score": value} for key, value in ranked],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": "Known travel history overrides astrological inference. Mobility signatures may describe commuting, local movement, work/study travel, international exposure or temporary journeys and must not be silently converted into relocation, immigration or permanent settlement claims.",
        "summary": f"The strongest symbolic Travel & Journeys theme is {TRAVEL_THEMES[dominant]}.",
        "limitation": "This analysis does not guarantee that a journey will happen, identify an exact destination, predict travel safety or accidents, guarantee visa/immigration outcomes, or imply permanent relocation or foreign settlement.",
    }
