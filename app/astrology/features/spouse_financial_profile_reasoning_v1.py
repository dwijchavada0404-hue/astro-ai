from __future__ import annotations

from typing import Any


FINANCIAL_LABELS = {
    "affluent": "financially comfortable, resourceful or materially well-supported spouse pattern",
    "stable": "financially steady, prudent and security-oriented spouse pattern",
    "entrepreneurial": "commercially active, self-driven or entrepreneurial spouse pattern",
    "variable": "financially variable or unconventional earning pattern",
    "mixed": "mixed financial signature without a strong single tilt",
}

PLANET_SIGNATURES = {
    "Jupiter": {"affluent": 1.0, "stable": 0.35},
    "Venus": {"affluent": 0.8, "stable": 0.25},
    "Mercury": {"entrepreneurial": 0.8, "stable": 0.25},
    "Mars": {"entrepreneurial": 0.6, "variable": 0.2},
    "Saturn": {"stable": 0.9},
    "Sun": {"stable": 0.35, "entrepreneurial": 0.3},
    "Moon": {"stable": 0.25, "variable": 0.2},
    "Rahu": {"variable": 0.8, "entrepreneurial": 0.35},
    "Ketu": {"variable": 0.55},
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


def analyze_spouse_financial_profile_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh = _get_house(chart, 7)
    if not seventh:
        return {
            "available": False,
            "event": "spouse_financial_profile",
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
            "interpretation": f"The 7th lord {seventh_lord} contributes strongly to the spouse financial-resource signature.",
            "details": {"planet": seventh_lord, "house": data.get("house"), "sign": data.get("sign")},
        })

    for occupant in _planets_in_house(chart, 7):
        _add(scores, sources, occupant, f"{occupant.lower()}_in_seventh", 0.86)
        evidence.append({
            "factor": f"{occupant.lower()}_in_seventh",
            "tier": "primary",
            "strength": 0.86,
            "interpretation": f"{occupant} in the 7th house directly modifies the spouse financial style and resource pattern.",
            "details": {"planet": occupant, "house": 7, "sign": _get_planet(chart, occupant).get("sign")},
        })

    # 8th house is the 2nd from the 7th and is used here as a spouse-resource context.
    eighth = _get_house(chart, 8)
    eighth_lord = str(eighth.get("lord", "") or "")
    if eighth_lord:
        _add(scores, sources, eighth_lord, "eighth_house_spouse_resources", 0.68)
        data = _get_planet(chart, eighth_lord)
        evidence.append({
            "factor": "eighth_house_spouse_resources",
            "tier": "supporting",
            "strength": 0.68,
            "interpretation": f"The 8th-house lord {eighth_lord} adds context about spouse-side resources and financial support patterns.",
            "details": {"planet": eighth_lord, "house": data.get("house"), "sign": data.get("sign")},
        })

    for planet, weight in (("Jupiter", 0.48), ("Venus", 0.42), ("Mercury", 0.34), ("Saturn", 0.32), ("Rahu", 0.24)):
        data = _get_planet(chart, planet)
        if data:
            adjusted = weight + (0.14 if data.get("house") in (7, 8, 11) else 0.0)
            _add(scores, sources, planet, f"{planet.lower()}_financial_context", adjusted)
            evidence.append({
                "factor": f"{planet.lower()}_financial_context",
                "tier": "context",
                "strength": round(adjusted, 3),
                "interpretation": f"{planet} adds contextual evidence to the spouse financial profile.",
                "details": {"planet": planet, "house": data.get("house"), "sign": data.get("sign")},
            })

    if not scores:
        scores["mixed"] = 1.0
        sources["mixed"] = ["insufficient_distinctive_financial_signature"]

    ranked = []
    for key, raw in scores.items():
        bonus = min(max(len(sources.get(key, [])) - 1, 0) * 0.08, 0.24)
        confirmed = raw + bonus
        ranked.append({
            "profile": key,
            "label": FINANCIAL_LABELS[key],
            "confirmed_score": round(confirmed, 3),
            "sources": sources.get(key, []),
        })

    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    max_confirmed = ranked[0]["confirmed_score"] if ranked else 1.0
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / max_confirmed, 3)

    dominant = ranked[0]
    confidence = round(
        _clamp(
            0.54
            + min(len(evidence), 8) * 0.028
            + min(len(dominant.get("sources", [])), 4) * 0.025,
            0.50,
            0.88,
        ),
        3,
    )

    return {
        "available": True,
        "event": "spouse_financial_profile",
        "model_version": "v1",
        "confidence": confidence,
        "dominant_profile": dominant["profile"],
        "dominant_label": dominant["label"],
        "summary": f"The strongest symbolic spouse financial theme is a {dominant['label']}.",
        "profile": {
            "financial_signature": dominant["profile"],
            "financial_signature_label": dominant["label"],
            "profile_scores": {item["profile"]: item["relative_strength"] for item in ranked},
            "chart_context": {
                "seventh_house": {"sign": seventh.get("sign"), "lord": seventh_lord, "occupants": _planets_in_house(chart, 7)},
                "eighth_house": {"sign": eighth.get("sign"), "lord": eighth_lord, "occupants": _planets_in_house(chart, 8)},
            },
        },
        "ranked_profiles": ranked,
        "evidence": evidence,
        "limitation": "This is a symbolic financial-profile estimate. It cannot reliably predict exact salary, net worth, inheritance amount, social class, or guaranteed future wealth.",
    }
