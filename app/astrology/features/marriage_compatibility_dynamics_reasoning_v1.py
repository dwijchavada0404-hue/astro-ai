from __future__ import annotations

from typing import Any


DYNAMICS_LABELS = {
    "emotional_attunement": "emotional attunement / sensitivity",
    "communication_flow": "communication flow / mutual understanding",
    "shared_values": "shared values / alignment",
    "chemistry": "chemistry / attraction",
    "stability": "stability / long-term cooperation",
    "independence": "independence / need for space",
    "friction": "friction / adjustment pressure",
}

PLANET_SIGNATURES = {
    "Moon": {"emotional_attunement": 1.0},
    "Mercury": {"communication_flow": 1.0},
    "Jupiter": {"shared_values": 0.9, "stability": 0.45},
    "Venus": {"chemistry": 1.0, "emotional_attunement": 0.35},
    "Saturn": {"stability": 0.9, "friction": 0.25},
    "Mars": {"chemistry": 0.7, "friction": 0.65},
    "Sun": {"independence": 0.45, "friction": 0.25},
    "Rahu": {"chemistry": 0.45, "independence": 0.45, "friction": 0.45},
    "Ketu": {"independence": 0.55, "emotional_attunement": 0.15},
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


def analyze_marriage_compatibility_dynamics_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh = _get_house(chart, 7)
    if not seventh:
        return {
            "available": False,
            "event": "marriage_compatibility_dynamics",
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
            "interpretation": f"The 7th lord {seventh_lord} is a primary indicator of how partnership dynamics are experienced.",
            "details": {"planet": seventh_lord, "house": data.get("house"), "sign": data.get("sign")},
        })

    for occupant in _planets_in_house(chart, 7):
        _add(scores, sources, occupant, f"{occupant.lower()}_in_seventh", 0.9)
        evidence.append({
            "factor": f"{occupant.lower()}_in_seventh",
            "tier": "primary",
            "strength": 0.9,
            "interpretation": f"{occupant} in the 7th house directly shapes compatibility and adjustment dynamics.",
            "details": {"planet": occupant, "house": 7, "sign": _get_planet(chart, occupant).get("sign")},
        })

    for planet, weight in (("Moon", 0.42), ("Mercury", 0.42), ("Venus", 0.50), ("Jupiter", 0.38), ("Saturn", 0.30), ("Mars", 0.28)):
        data = _get_planet(chart, planet)
        if data:
            _add(scores, sources, planet, f"{planet.lower()}_compatibility_context", weight)
            evidence.append({
                "factor": f"{planet.lower()}_compatibility_context",
                "tier": "context",
                "strength": weight,
                "interpretation": f"{planet} contributes contextual evidence to the partnership compatibility profile.",
                "details": {"planet": planet, "house": data.get("house"), "sign": data.get("sign")},
            })

    if not scores:
        scores["shared_values"] = 0.5
        sources["shared_values"] = ["insufficient_distinctive_signature"]

    ranked = []
    for key, raw in scores.items():
        bonus = min(max(len(sources.get(key, [])) - 1, 0) * 0.07, 0.21)
        ranked.append({
            "dimension": key,
            "label": DYNAMICS_LABELS[key],
            "confirmed_score": round(raw + bonus, 3),
            "sources": sources.get(key, []),
        })
    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    maximum = ranked[0]["confirmed_score"] if ranked else 1.0
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / maximum, 3)

    strongest = ranked[0]
    friction = next((item for item in ranked if item["dimension"] == "friction"), None)
    confidence = round(_clamp(0.55 + min(len(evidence), 8) * 0.025 + min(len(strongest["sources"]), 4) * 0.025, 0.50, 0.88), 3)

    if friction and friction["relative_strength"] >= 0.65:
        summary = f"The strongest compatibility theme is {strongest['label']}, with noticeable adjustment or friction themes also present."
    else:
        summary = f"The strongest symbolic compatibility theme is {strongest['label']}."

    return {
        "available": True,
        "event": "marriage_compatibility_dynamics",
        "model_version": "v1",
        "confidence": confidence,
        "dominant_dimension": strongest["dimension"],
        "dominant_label": strongest["label"],
        "summary": summary,
        "profile": {
            "dominant_dimension": strongest["dimension"],
            "dominant_dimension_label": strongest["label"],
            "dimension_scores": {item["dimension"]: item["relative_strength"] for item in ranked},
            "chart_context": {
                "seventh_house": {"sign": seventh.get("sign"), "lord": seventh_lord, "occupants": _planets_in_house(chart, 7)},
            },
        },
        "ranked_dimensions": ranked,
        "evidence": evidence,
        "limitation": "This is a symbolic compatibility-style profile derived from one natal chart. It does not replace two-person synastry, real-world relationship history, communication patterns, values, consent, or lived compatibility.",
    }
