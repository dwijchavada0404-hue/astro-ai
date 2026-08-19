from __future__ import annotations

from typing import Any


THEME_LABELS = {
    "traditional_respectable": "traditional, respectable or established family environment",
    "educated_cultured": "educated, cultured or knowledge-oriented family environment",
    "business_commercial": "business, commerce or entrepreneurial family environment",
    "professional_structured": "professional, disciplined or institution-linked family environment",
    "affluent_resourceful": "resourceful, comfortable or materially supported family environment",
    "international_modern": "international, modern or unconventional family environment",
    "creative_social": "creative, social or aesthetically oriented family environment",
    "private_intense": "private, intense or tightly bonded family environment",
}

PLANET_THEMES = {
    "Sun": {"traditional_respectable": 0.85, "professional_structured": 0.55},
    "Moon": {"educated_cultured": 0.55, "creative_social": 0.55},
    "Mars": {"business_commercial": 0.65, "private_intense": 0.55},
    "Mercury": {"business_commercial": 0.85, "educated_cultured": 0.70},
    "Jupiter": {"educated_cultured": 1.0, "traditional_respectable": 0.75},
    "Venus": {"affluent_resourceful": 0.85, "creative_social": 0.80},
    "Saturn": {"professional_structured": 0.95, "traditional_respectable": 0.55},
    "Rahu": {"international_modern": 0.95, "business_commercial": 0.45},
    "Ketu": {"private_intense": 0.70, "traditional_respectable": 0.30},
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _get_house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    return _safe_dict(_safe_dict(chart.get("houses")).get(str(number)))


def _get_planet(chart: dict[str, Any], planet: str | None) -> dict[str, Any]:
    if not planet:
        return {}
    return _safe_dict(_safe_dict(chart.get("planets")).get(planet))


def _planets_in_house(chart: dict[str, Any], number: int) -> list[str]:
    result: list[str] = []
    for name, raw in _safe_dict(chart.get("planets")).items():
        if _safe_dict(raw).get("house") == number:
            result.append(str(name))
    return result


def _add(score_map: dict[str, float], sources: dict[str, list[str]], planet: str, source: str, weight: float) -> None:
    for theme, base in PLANET_THEMES.get(planet, {}).items():
        score_map[theme] = score_map.get(theme, 0.0) + base * weight
        sources.setdefault(theme, [])
        if source not in sources[theme]:
            sources[theme].append(source)


def _rank(score_map: dict[str, float], sources: dict[str, list[str]]) -> list[dict[str, Any]]:
    ranked = []
    for theme, raw_score in score_map.items():
        theme_sources = sources.get(theme, [])
        bonus = min(max(len(theme_sources) - 1, 0) * 0.08, 0.24)
        score = raw_score + bonus
        ranked.append({
            "theme": theme,
            "label": THEME_LABELS.get(theme, theme),
            "raw_score": round(raw_score, 3),
            "convergence_bonus": round(bonus, 3),
            "confirmed_score": round(score, 3),
            "sources": theme_sources,
        })
    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    top = ranked[0]["confirmed_score"] if ranked else 1.0
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / top, 3)
    return ranked


def analyze_spouse_family_background_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh = _get_house(chart, 7)
    if not seventh:
        return {"available": False, "event": "spouse_family_background", "model_version": "v1", "reason": "7th house data is unavailable."}

    # 2nd from spouse (7th) = natal 8th: spouse family, lineage, accumulated resources.
    # 4th from spouse (7th) = natal 10th: home culture, respectability, social structure.
    family_house_number = 8
    home_culture_house_number = 10
    family_house = _get_house(chart, family_house_number)
    home_culture_house = _get_house(chart, home_culture_house_number)
    if not family_house or not home_culture_house:
        return {"available": False, "event": "spouse_family_background", "model_version": "v1", "reason": "Derived spouse family house data is unavailable."}

    score_map: dict[str, float] = {}
    sources: dict[str, list[str]] = {}
    evidence: list[dict[str, Any]] = []

    for factor, number, house, weight in (
        ("spouse_family_house_lord", family_house_number, family_house, 1.0),
        ("spouse_home_culture_house_lord", home_culture_house_number, home_culture_house, 0.88),
    ):
        lord = str(house.get("lord", "") or "")
        _add(score_map, sources, lord, factor, weight)
        evidence.append({
            "factor": factor,
            "tier": "primary",
            "strength": round(weight, 3),
            "interpretation": f"Derived spouse family house {number} is ruled by {lord}, shaping family background and social environment.",
            "details": {"house": number, "sign": house.get("sign"), "lord": lord},
        })
        for occupant in _planets_in_house(chart, number):
            source = f"{occupant.lower()}_in_spouse_family_house_{number}"
            _add(score_map, sources, occupant, source, weight * 0.72)
            evidence.append({
                "factor": source,
                "tier": "secondary",
                "strength": round(weight * 0.72, 3),
                "interpretation": f"{occupant} occupies derived spouse family house {number} and modifies the family-background pattern.",
                "details": {"planet": occupant, "house": number, "sign": _get_planet(chart, occupant).get("sign")},
            })

    seventh_lord = str(seventh.get("lord", "") or "")
    if seventh_lord:
        data = _get_planet(chart, seventh_lord)
        weight = 0.42 if data.get("house") not in {8, 10} else 0.58
        _add(score_map, sources, seventh_lord, "seventh_lord_family_context", weight)
        evidence.append({
            "factor": "seventh_lord_family_context",
            "tier": "secondary",
            "strength": weight,
            "interpretation": f"The 7th lord {seventh_lord} adds context to the spouse's family and social background.",
            "details": {"planet": seventh_lord, "house": data.get("house"), "sign": data.get("sign")},
        })

    for planet, factor, weight in (
        ("Jupiter", "jupiter_family_culture_significator", 0.46),
        ("Venus", "venus_social_comfort_significator", 0.42),
        ("Saturn", "saturn_family_structure_significator", 0.40),
    ):
        data = _get_planet(chart, planet)
        adjusted = weight + (0.14 if data.get("house") in {8, 10} else 0.0)
        _add(score_map, sources, planet, factor, adjusted)
        evidence.append({
            "factor": factor,
            "tier": "context",
            "strength": round(adjusted, 3),
            "interpretation": f"{planet} provides contextual evidence for family culture, resources and social structure.",
            "details": {"planet": planet, "house": data.get("house"), "sign": data.get("sign")},
        })

    ranked = _rank(score_map, sources)
    strongest = ranked[:5]
    themes = [item["label"] for item in strongest]
    summary = (
        "The spouse family-background pattern is most consistent with " + ", ".join(themes[:3]) + "."
        if themes else
        "The currently modelled chart factors do not produce a distinct spouse family-background profile."
    )
    confidence = round(_clamp(0.54 + min(len(evidence), 8) * 0.025 + min(len(strongest[0].get("sources", [])) if strongest else 0, 4) * 0.03, 0.50, 0.88), 3)

    return {
        "available": True,
        "event": "spouse_family_background",
        "model_version": "v1",
        "confidence": confidence,
        "summary": summary,
        "profile": {
            "family_themes": themes,
            "theme_scores": {item["theme"]: item["relative_strength"] for item in ranked},
            "chart_context": {
                "seventh_house": {"sign": seventh.get("sign"), "lord": seventh_lord},
                "family_house": {"natal_house": 8, "sign": family_house.get("sign"), "lord": family_house.get("lord"), "occupants": _planets_in_house(chart, 8)},
                "home_culture_house": {"natal_house": 10, "sign": home_culture_house.get("sign"), "lord": home_culture_house.get("lord"), "occupants": _planets_in_house(chart, 10)},
            },
        },
        "strongest_themes": strongest,
        "ranked_themes": ranked,
        "evidence": evidence,
    }
