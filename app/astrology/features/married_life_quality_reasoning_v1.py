from __future__ import annotations

from typing import Any


QUALITY_LABELS = {
    "harmonious": "harmonious, supportive and cooperative married-life pattern",
    "passionate": "passionate, active and high-intensity married-life pattern",
    "stable": "stable, duty-oriented and enduring married-life pattern",
    "variable": "variable or unconventional married-life pattern requiring adaptability",
    "mixed": "mixed married-life pattern with both supportive and challenging themes",
}

PLANET_SIGNATURES = {
    "Venus": {"harmonious": 1.0},
    "Jupiter": {"harmonious": 0.8, "stable": 0.45},
    "Moon": {"harmonious": 0.6},
    "Saturn": {"stable": 0.85, "mixed": 0.25},
    "Mars": {"passionate": 0.85, "mixed": 0.35},
    "Sun": {"passionate": 0.45, "stable": 0.25},
    "Mercury": {"harmonious": 0.35, "variable": 0.25},
    "Rahu": {"variable": 0.8, "mixed": 0.35},
    "Ketu": {"variable": 0.6, "mixed": 0.35},
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


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


def analyze_married_life_quality_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh = _get_house(chart, 7)
    if not seventh:
        return {
            "available": False,
            "event": "married_life_quality",
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
            "interpretation": f"The 7th lord {seventh_lord} is a primary indicator of partnership dynamics.",
            "details": {"planet": seventh_lord, "house": data.get("house"), "sign": data.get("sign")},
        })

    for occupant in _planets_in_house(chart, 7):
        _add(scores, sources, occupant, f"{occupant.lower()}_in_seventh", 0.9)
        evidence.append({
            "factor": f"{occupant.lower()}_in_seventh",
            "tier": "primary",
            "strength": 0.9,
            "interpretation": f"{occupant} in the 7th house directly modifies the tone of partnership and married life.",
            "details": {"planet": occupant, "house": 7, "sign": _get_planet(chart, occupant).get("sign")},
        })

    for planet, weight in (("Venus", 0.62), ("Jupiter", 0.42), ("Moon", 0.30), ("Saturn", 0.28), ("Mars", 0.25)):
        data = _get_planet(chart, planet)
        if data:
            _add(scores, sources, planet, f"{planet.lower()}_relationship_context", weight)
            evidence.append({
                "factor": f"{planet.lower()}_relationship_context",
                "tier": "context",
                "strength": weight,
                "interpretation": f"{planet} contributes contextual evidence to the relationship-quality pattern.",
                "details": {"planet": planet, "house": data.get("house"), "sign": data.get("sign")},
            })

    if not scores:
        scores["mixed"] = 1.0
        sources["mixed"] = ["insufficient_distinctive_signature"]

    ranked = []
    for key, raw in scores.items():
        bonus = min(max(len(sources.get(key, [])) - 1, 0) * 0.08, 0.24)
        ranked.append({
            "profile": key,
            "label": QUALITY_LABELS[key],
            "confirmed_score": round(raw + bonus, 3),
            "sources": sources.get(key, []),
        })
    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    maximum = ranked[0]["confirmed_score"] if ranked else 1.0
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / maximum, 3)

    dominant = ranked[0]
    confidence = round(_clamp(0.54 + min(len(evidence), 7) * 0.03 + min(len(dominant["sources"]), 4) * 0.025, 0.50, 0.88), 3)

    return {
        "available": True,
        "event": "married_life_quality",
        "model_version": "v1",
        "confidence": confidence,
        "dominant_profile": dominant["profile"],
        "dominant_label": dominant["label"],
        "summary": f"The strongest symbolic married-life theme is a {dominant['label']}.",
        "profile": {
            "quality_signature": dominant["profile"],
            "quality_signature_label": dominant["label"],
            "profile_scores": {item["profile"]: item["relative_strength"] for item in ranked},
            "chart_context": {
                "seventh_house": {"sign": seventh.get("sign"), "lord": seventh_lord, "occupants": _planets_in_house(chart, 7)},
            },
        },
        "ranked_profiles": ranked,
        "evidence": evidence,
        "limitation": "This is a symbolic relationship-quality assessment. It cannot guarantee marital happiness, conflict, separation, divorce, abuse, or any specific real-world outcome.",
    }
