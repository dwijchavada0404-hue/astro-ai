from __future__ import annotations

from typing import Any


SIBLINGS_COMMUNICATION_THEMES = {
    "sibling_bond": "symbolic patterns around sibling and sibling-like peer relationships",
    "communication_expression": "communication, articulation and everyday exchange",
    "initiative_courage": "initiative, effort, courage and willingness to act",
    "learning_skills": "practical learning, skills, writing and information exchange",
    "collaboration": "cooperation with peers, teammates and close networks",
    "boundaries_competition": "assertiveness, boundaries and competitive friction",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _safe_dict(chart.get("houses"))
    return _safe_dict(houses.get(str(number)) or houses.get(number))


def _planet(chart: dict[str, Any], name: str) -> dict[str, Any]:
    return _safe_dict(_safe_dict(chart.get("planets")).get(name))


def _planet_house(chart: dict[str, Any], name: str) -> int | None:
    value = _planet(chart, name).get("house")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _lord(chart: dict[str, Any], number: int) -> str | None:
    value = _house(chart, number).get("lord")
    return str(value) if value else None


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_siblings_communication_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Evaluate sibling/peer and communication themes without judging specific people or factual events."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    houses = _safe_dict(chart.get("houses"))
    planets = _safe_dict(chart.get("planets"))
    if not houses or not planets:
        return {"available": False, "event": "siblings_communication", "model_version": "v1", "reason": "Usable house and planetary data are required."}

    lord3 = _lord(chart, 3)
    lord7 = _lord(chart, 7)
    lord11 = _lord(chart, 11)
    lord5 = _lord(chart, 5)
    lord6 = _lord(chart, 6)
    h3_planets = {name for name in planets if _planet_house(chart, name) == 3}

    sibling = 0.28 + (0.20 if lord3 and _planet_house(chart, lord3) in {1, 3, 5, 9, 11} else 0.0) + (0.12 if h3_planets & {"Mercury", "Jupiter", "Venus", "Moon"} else 0.0) + (0.10 if lord11 and _planet_house(chart, lord11) in {3, 5, 7, 11} else 0.0)
    communication = 0.26 + (0.24 if _planet_house(chart, "Mercury") in {1, 2, 3, 5, 10, 11} else 0.0) + (0.16 if lord3 and _planet_house(chart, lord3) in {1, 2, 3, 5, 10, 11} else 0.0) + (0.08 if _planet_house(chart, "Moon") in {2, 3, 5} else 0.0)
    initiative = 0.24 + (0.22 if _planet_house(chart, "Mars") in {1, 3, 6, 10, 11} else 0.0) + (0.16 if lord3 and _planet_house(chart, lord3) in {1, 3, 6, 10, 11} else 0.0) + (0.08 if _planet_house(chart, "Sun") in {1, 3, 10, 11} else 0.0)
    learning = 0.24 + (0.20 if _planet_house(chart, "Mercury") in {3, 5, 9, 10} else 0.0) + (0.14 if lord5 and _planet_house(chart, lord5) in {3, 5, 9, 11} else 0.0) + (0.10 if _planet_house(chart, "Jupiter") in {3, 5, 9} else 0.0)
    collaboration = 0.24 + (0.14 if lord7 and _planet_house(chart, lord7) in {3, 7, 11} else 0.0) + (0.14 if lord11 and _planet_house(chart, lord11) in {3, 7, 11} else 0.0) + (0.10 if _planet_house(chart, "Venus") in {3, 7, 11} else 0.0) + (0.08 if _planet_house(chart, "Mercury") in {3, 7, 11} else 0.0)
    boundaries = 0.22 + (0.18 if _planet_house(chart, "Saturn") in {3, 6, 11} else 0.0) + (0.16 if _planet_house(chart, "Mars") in {3, 6, 11} else 0.0) + (0.10 if lord6 and _planet_house(chart, lord6) in {3, 6, 11} else 0.0)

    scores = {
        "sibling_bond": _bounded(sibling), "communication_expression": _bounded(communication),
        "initiative_courage": _bounded(initiative), "learning_skills": _bounded(learning),
        "collaboration": _bounded(collaboration), "boundaries_competition": _bounded(boundaries),
    }
    strongest = max(scores.items(), key=lambda item: item[1])
    evidence = [
        {"factor": "third_house_axis", "house": 3, "lord": lord3, "planets": sorted(h3_planets), "interpretation": "The 3rd house is the primary axis for siblings, communication, skills, initiative and everyday exchange."},
        {"factor": "mercury", "house": _planet_house(chart, "Mercury"), "interpretation": "Mercury contributes modestly to communication, writing, learning and information exchange."},
        {"factor": "mars", "house": _planet_house(chart, "Mars"), "interpretation": "Mars contributes modestly to initiative, assertiveness and competitive expression."},
        {"factor": "peer_network_context", "seventh_lord": lord7, "eleventh_lord": lord11, "interpretation": "The 7th and 11th houses provide secondary context for cooperation and peer networks."},
    ]
    confidence = _bounded(0.44 + 0.10 * bool(lord3) + 0.08 * bool(lord7) + 0.08 * bool(lord11) + 0.18 * strongest[1])
    return {
        "available": True, "event": "siblings_communication", "model_version": "v1",
        "theme_scores": scores, "strongest_theme": strongest[0], "strongest_theme_score": strongest[1],
        "confidence": confidence, "evidence": evidence,
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known sibling relationships, communication history and lived events override astrology. The chart must not manufacture siblings, estrangement, conflict, reconciliation or other interpersonal events."},
        "summary": f"The strongest symbolic Siblings & Communication theme is {strongest[0].replace('_', ' ')}. This describes tendencies, not facts about specific people.",
        "limitation": "This analysis cannot determine whether a sibling exists, identify a specific sibling's personality or intentions, judge loyalty, predict conflict/estrangement/reconciliation, or guarantee communication, learning or collaboration outcomes.",
    }
