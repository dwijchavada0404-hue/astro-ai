from __future__ import annotations

from typing import Any


CHALLENGE_LABELS = {
    "conflict_intensity": "higher conflict / intensity potential",
    "emotional_distance": "emotional distance / withdrawal potential",
    "instability": "instability / unpredictability potential",
    "delay_pressure": "delay / pressure around commitment and partnership",
    "repair_capacity": "repair, patience and reconciliation capacity",
    "balanced": "mixed but manageable relationship challenge profile",
}

PLANET_SIGNATURES = {
    "Mars": {"conflict_intensity": 1.0, "instability": 0.35},
    "Saturn": {"emotional_distance": 0.8, "delay_pressure": 0.85, "repair_capacity": 0.35},
    "Rahu": {"instability": 0.9, "conflict_intensity": 0.35},
    "Ketu": {"emotional_distance": 0.75, "instability": 0.35},
    "Sun": {"conflict_intensity": 0.4},
    "Moon": {"repair_capacity": 0.45},
    "Venus": {"repair_capacity": 0.9},
    "Jupiter": {"repair_capacity": 0.8},
    "Mercury": {"repair_capacity": 0.35},
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _get_house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    return _safe_dict(_safe_dict(chart.get("houses")).get(str(number)))


def _get_planet(chart: dict[str, Any], planet: str | None) -> dict[str, Any]:
    if not planet:
        return {}
    return _safe_dict(_safe_dict(chart.get("planets")).get(planet))


def _planets_in_house(chart: dict[str, Any], number: int) -> list[str]:
    return [
        str(name)
        for name, raw in _safe_dict(chart.get("planets")).items()
        if _safe_dict(raw).get("house") == number
    ]


def _add(scores: dict[str, float], sources: dict[str, list[str]], planet: str, source: str, weight: float) -> None:
    for key, value in PLANET_SIGNATURES.get(planet, {}).items():
        scores[key] = scores.get(key, 0.0) + value * weight
        sources.setdefault(key, [])
        if source not in sources[key]:
            sources[key].append(source)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def analyze_relationship_challenges_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh = _get_house(chart, 7)
    if not seventh:
        return {
            "available": False,
            "event": "relationship_challenges",
            "model_version": "v1",
            "reason": "7th house data is unavailable.",
        }

    scores: dict[str, float] = {}
    sources: dict[str, list[str]] = {}
    evidence: list[dict[str, Any]] = []

    seventh_lord = str(seventh.get("lord", "") or "")
    if seventh_lord:
        _add(scores, sources, seventh_lord, "seventh_lord", 1.0)
        data = _get_planet(chart, seventh_lord)
        evidence.append({
            "factor": "seventh_lord",
            "tier": "primary",
            "strength": 1.0,
            "interpretation": f"The 7th lord {seventh_lord} is a primary relationship-dynamics indicator.",
            "details": {"planet": seventh_lord, "house": data.get("house"), "sign": data.get("sign")},
        })

    for occupant in _planets_in_house(chart, 7):
        _add(scores, sources, occupant, f"{occupant.lower()}_in_seventh", 0.95)
        evidence.append({
            "factor": f"{occupant.lower()}_in_seventh",
            "tier": "primary",
            "strength": 0.95,
            "interpretation": f"{occupant} in the 7th house directly modifies partnership friction and repair patterns.",
            "details": {"planet": occupant, "house": 7, "sign": _get_planet(chart, occupant).get("sign")},
        })

    for planet, weight in (("Mars", 0.50), ("Saturn", 0.48), ("Rahu", 0.42), ("Ketu", 0.38), ("Venus", 0.46), ("Jupiter", 0.38), ("Moon", 0.30)):
        data = _get_planet(chart, planet)
        if data:
            _add(scores, sources, planet, f"{planet.lower()}_relationship_context", weight)
            evidence.append({
                "factor": f"{planet.lower()}_relationship_context",
                "tier": "context",
                "strength": weight,
                "interpretation": f"{planet} contributes contextual evidence to the challenge-and-repair pattern.",
                "details": {"planet": planet, "house": data.get("house"), "sign": data.get("sign")},
            })

    if not scores:
        scores["balanced"] = 1.0
        sources["balanced"] = ["insufficient_distinctive_signature"]

    ranked = []
    for key, raw in scores.items():
        bonus = min(max(len(sources.get(key, [])) - 1, 0) * 0.07, 0.21)
        ranked.append({
            "profile": key,
            "label": CHALLENGE_LABELS[key],
            "confirmed_score": round(raw + bonus, 3),
            "sources": sources.get(key, []),
        })
    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    maximum = ranked[0]["confirmed_score"] if ranked else 1.0
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / maximum, 3)

    strongest = ranked[0]
    repair = next((item for item in ranked if item["profile"] == "repair_capacity"), None)
    challenge_candidates = [item for item in ranked if item["profile"] != "repair_capacity"]
    dominant_challenge = challenge_candidates[0] if challenge_candidates else strongest

    confidence = round(_clamp(0.54 + min(len(evidence), 8) * 0.025 + min(len(dominant_challenge["sources"]), 4) * 0.025, 0.50, 0.88), 3)

    if repair and repair["relative_strength"] >= 0.65:
        summary = f"The strongest challenge theme is {dominant_challenge['label']}, with meaningful symbolic repair capacity also present."
    else:
        summary = f"The strongest symbolic relationship challenge theme is {dominant_challenge['label']}."

    return {
        "available": True,
        "event": "relationship_challenges",
        "model_version": "v1",
        "confidence": confidence,
        "dominant_challenge": dominant_challenge["profile"],
        "dominant_label": dominant_challenge["label"],
        "repair_capacity": None if repair is None else repair["relative_strength"],
        "summary": summary,
        "profile": {
            "challenge_signature": dominant_challenge["profile"],
            "challenge_signature_label": dominant_challenge["label"],
            "profile_scores": {item["profile"]: item["relative_strength"] for item in ranked},
            "chart_context": {
                "seventh_house": {"sign": seventh.get("sign"), "lord": seventh_lord, "occupants": _planets_in_house(chart, 7)},
            },
        },
        "ranked_profiles": ranked,
        "evidence": evidence,
        "limitation": "This is a symbolic relationship-stress assessment, not a prediction of divorce, separation, abuse, infidelity, violence, or any guaranteed real-world outcome. Serious relationship or safety concerns should be evaluated using real-world evidence and appropriate professional support.",
    }
