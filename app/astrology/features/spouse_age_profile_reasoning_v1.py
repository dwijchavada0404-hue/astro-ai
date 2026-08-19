from __future__ import annotations

from typing import Any


AGE_LABELS = {
    "older_mature": "older, more mature or responsibility-oriented spouse pattern",
    "similar_age": "similar-age or broadly peer-group spouse pattern",
    "younger_youthful": "younger, youthful or noticeably fresh-tempered spouse pattern",
    "mixed": "mixed age-signature with no strong older/younger tilt",
}

PLANET_AGE_SIGNATURES = {
    "Saturn": {"older_mature": 1.0},
    "Jupiter": {"older_mature": 0.55, "similar_age": 0.30},
    "Sun": {"older_mature": 0.45, "similar_age": 0.30},
    "Mars": {"similar_age": 0.50, "younger_youthful": 0.25},
    "Mercury": {"younger_youthful": 0.95},
    "Moon": {"younger_youthful": 0.60, "similar_age": 0.25},
    "Venus": {"similar_age": 0.60, "younger_youthful": 0.35},
    "Rahu": {"mixed": 0.65},
    "Ketu": {"mixed": 0.55},
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
    for key, value in PLANET_AGE_SIGNATURES.get(planet, {}).items():
        scores[key] = scores.get(key, 0.0) + value * weight
        sources.setdefault(key, [])
        if source not in sources[key]:
            sources[key].append(source)


def analyze_spouse_age_profile_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh = _get_house(chart, 7)
    if not seventh:
        return {
            "available": False,
            "event": "spouse_age_profile",
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
            "interpretation": f"The 7th lord {seventh_lord} contributes strongly to the spouse age and maturity signature.",
            "details": {"planet": seventh_lord, "house": data.get("house"), "sign": data.get("sign")},
        })

    for occupant in _planets_in_house(chart, 7):
        _add(scores, sources, occupant, f"{occupant.lower()}_in_seventh", 0.88)
        evidence.append({
            "factor": f"{occupant.lower()}_in_seventh",
            "tier": "primary",
            "strength": 0.88,
            "interpretation": f"{occupant} in the 7th house directly modifies the spouse maturity and age-expression pattern.",
            "details": {"planet": occupant, "house": 7, "sign": _get_planet(chart, occupant).get("sign")},
        })

    for planet, weight in (("Saturn", 0.50), ("Mercury", 0.42), ("Jupiter", 0.34), ("Venus", 0.32)):
        data = _get_planet(chart, planet)
        if data:
            adjusted = weight + (0.16 if data.get("house") == 7 else 0.0)
            _add(scores, sources, planet, f"{planet.lower()}_age_significator", adjusted)
            evidence.append({
                "factor": f"{planet.lower()}_age_significator",
                "tier": "context",
                "strength": round(adjusted, 3),
                "interpretation": f"{planet} adds contextual evidence to the spouse age/maturity signature.",
                "details": {"planet": planet, "house": data.get("house"), "sign": data.get("sign")},
            })

    if not scores:
        scores["mixed"] = 1.0
        sources["mixed"] = ["insufficient_distinctive_age_signature"]

    ranked = []
    top_raw = max(scores.values()) if scores else 1.0
    for key, raw in scores.items():
        bonus = min(max(len(sources.get(key, [])) - 1, 0) * 0.08, 0.24)
        confirmed = raw + bonus
        ranked.append({
            "profile": key,
            "label": AGE_LABELS[key],
            "raw_score": round(raw, 3),
            "convergence_bonus": round(bonus, 3),
            "confirmed_score": round(confirmed, 3),
            "sources": sources.get(key, []),
        })
    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    max_confirmed = ranked[0]["confirmed_score"] if ranked else top_raw
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / max_confirmed, 3)

    dominant = ranked[0] if ranked else {"profile": "mixed", "label": AGE_LABELS["mixed"], "relative_strength": 1.0}
    confidence = round(_clamp(0.54 + min(len(evidence), 7) * 0.03 + min(len(dominant.get("sources", [])), 4) * 0.025, 0.50, 0.88), 3)

    return {
        "available": True,
        "event": "spouse_age_profile",
        "model_version": "v1",
        "confidence": confidence,
        "dominant_profile": dominant["profile"],
        "dominant_label": dominant["label"],
        "summary": f"The strongest spouse age/maturity signature is {dominant['label']}.",
        "profile": {
            "age_signature": dominant["profile"],
            "age_signature_label": dominant["label"],
            "profile_scores": {item["profile"]: item["relative_strength"] for item in ranked},
            "chart_context": {
                "seventh_house": {"sign": seventh.get("sign"), "lord": seventh_lord, "occupants": _planets_in_house(chart, 7)},
            },
        },
        "ranked_profiles": ranked,
        "evidence": evidence,
        "limitation": "This model estimates a symbolic maturity/relative-age tendency; it cannot reliably predict an exact age or exact age gap.",
    }
