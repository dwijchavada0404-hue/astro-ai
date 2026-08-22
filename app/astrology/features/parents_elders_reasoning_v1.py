from __future__ import annotations

from typing import Any


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _safe_dict(chart.get("houses"))
    return _safe_dict(houses.get(str(number)) or houses.get(number))


def _planet_house(chart: dict[str, Any], name: str) -> int | None:
    value = _safe_dict(_safe_dict(chart.get("planets")).get(name)).get("house")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _lord(chart: dict[str, Any], number: int) -> str | None:
    value = _house(chart, number).get("lord")
    return str(value) if value else None


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_parents_elders_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Evaluate symbolic parent/elder relationship themes without predicting health, death or specific behaviour."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    houses = _safe_dict(chart.get("houses")); planets = _safe_dict(chart.get("planets"))
    if not houses or not planets:
        return {"available": False, "event": "parents_elders", "model_version": "v1", "reason": "Usable house and planetary data are required."}

    lord4, lord9, lord10 = _lord(chart, 4), _lord(chart, 9), _lord(chart, 10)
    emotional_support = 0.28 + (0.20 if lord4 and _planet_house(chart, lord4) in {1, 4, 5, 9, 11} else 0.0) + (0.14 if _planet_house(chart, "Moon") in {1, 4, 5, 9, 11} else 0.0) + (0.08 if _planet_house(chart, "Venus") in {4, 5, 9} else 0.0)
    guidance = 0.26 + (0.20 if lord9 and _planet_house(chart, lord9) in {1, 5, 9, 10, 11} else 0.0) + (0.16 if _planet_house(chart, "Jupiter") in {1, 5, 9, 10, 11} else 0.0) + (0.08 if _planet_house(chart, "Sun") in {1, 9, 10} else 0.0)
    authority = 0.24 + (0.18 if _planet_house(chart, "Sun") in {1, 4, 9, 10} else 0.0) + (0.14 if lord10 and _planet_house(chart, lord10) in {1, 4, 9, 10} else 0.0) + (0.10 if _planet_house(chart, "Saturn") in {4, 9, 10} else 0.0)
    duty = 0.22 + (0.20 if _planet_house(chart, "Saturn") in {4, 6, 9, 10} else 0.0) + (0.12 if lord4 and _planet_house(chart, lord4) in {6, 10, 11} else 0.0) + (0.10 if lord9 and _planet_house(chart, lord9) in {6, 10, 11} else 0.0)
    independence = 0.22 + (0.16 if _planet_house(chart, "Mars") in {1, 3, 10} else 0.0) + (0.14 if _planet_house(chart, "Rahu") in {1, 4, 9, 10} else 0.0) + (0.10 if lord4 and _planet_house(chart, lord4) in {3, 10, 11} else 0.0)
    family_continuity = 0.24 + (0.16 if lord4 and _planet_house(chart, lord4) in {2, 4, 5, 9, 11} else 0.0) + (0.14 if lord9 and _planet_house(chart, lord9) in {2, 4, 5, 9, 11} else 0.0) + (0.10 if _planet_house(chart, "Jupiter") in {2, 4, 5, 9, 11} else 0.0)

    scores = {
        "emotional_support": _bounded(emotional_support), "guidance_mentorship": _bounded(guidance),
        "authority_structure": _bounded(authority), "duty_responsibility": _bounded(duty),
        "independence_boundaries": _bounded(independence), "family_continuity": _bounded(family_continuity),
    }
    strongest = max(scores.items(), key=lambda item: item[1])
    return {
        "available": True, "event": "parents_elders", "model_version": "v1", "theme_scores": scores,
        "strongest_theme": strongest[0], "strongest_theme_score": strongest[1],
        "confidence": _bounded(0.46 + 0.08 * bool(lord4) + 0.08 * bool(lord9) + 0.16 * strongest[1]),
        "evidence": [
            {"factor": "fourth_house_axis", "house": 4, "lord": lord4, "interpretation": "The 4th house contributes to home, emotional roots and caregiving context."},
            {"factor": "ninth_house_axis", "house": 9, "lord": lord9, "interpretation": "The 9th house contributes to guidance, elders, values and mentorship context."},
            {"factor": "sun_moon_context", "sun_house": _planet_house(chart, "Sun"), "moon_house": _planet_house(chart, "Moon"), "interpretation": "Sun and Moon contribute symbolically to authority and nurturing themes without mapping one planet to one parent."},
        ],
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known parent/elder relationships and family history override astrology. The chart must not manufacture closeness, conflict, estrangement, reconciliation, caregiving events, illness or loss."},
        "summary": f"The strongest symbolic Parents & Elders theme is {strongest[0].replace('_', ' ')}.",
        "limitation": "This analysis cannot diagnose or predict a parent/elder's health, lifespan or death, identify their intentions or character, determine whether a parent is present or absent, or guarantee closeness, conflict, caregiving, reconciliation or inheritance outcomes.",
    }
