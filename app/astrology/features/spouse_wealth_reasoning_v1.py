from __future__ import annotations

from typing import Any


THEME_LABELS = {
    "wealth_accumulation": "wealth accumulation and financial growth",
    "stable_assets": "stable assets, savings or property orientation",
    "business_commercial": "business, commerce or entrepreneurial earning",
    "professional_income": "structured professional income",
    "financial_analysis": "finance, accounting or analytical money management",
    "international_income": "international, foreign-linked or unconventional income",
    "family_resources": "family resources or inherited financial support",
    "variable_speculative": "variable, speculative or opportunity-driven finances",
}

PLANET_WEALTH_THEMES = {
    "Sun": {"professional_income": 0.80, "wealth_accumulation": 0.55},
    "Moon": {"family_resources": 0.65, "stable_assets": 0.50},
    "Mars": {"business_commercial": 0.70, "stable_assets": 0.55},
    "Mercury": {"financial_analysis": 0.90, "business_commercial": 0.75},
    "Jupiter": {"wealth_accumulation": 1.00, "family_resources": 0.70},
    "Venus": {"wealth_accumulation": 0.85, "stable_assets": 0.65},
    "Saturn": {"stable_assets": 0.90, "professional_income": 0.75},
    "Rahu": {"international_income": 0.90, "variable_speculative": 0.65},
    "Ketu": {"variable_speculative": 0.45, "financial_analysis": 0.35},
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


def _get_house(chart: dict[str, Any], house_number: int) -> dict[str, Any]:
    return _safe_dict(_safe_dict(chart.get("houses")).get(str(house_number)))


def _get_planet(chart: dict[str, Any], planet: str | None) -> dict[str, Any]:
    if not planet:
        return {}
    return _safe_dict(_safe_dict(chart.get("planets")).get(planet))


def _planets_in_house(chart: dict[str, Any], house_number: int) -> list[str]:
    result: list[str] = []
    for name, raw in _safe_dict(chart.get("planets")).items():
        data = _safe_dict(raw)
        if data.get("house") == house_number:
            result.append(str(name))
    return result


def _add_scores(
    score_map: dict[str, float],
    source_map: dict[str, list[str]],
    themes: dict[str, float],
    source: str,
    weight: float,
) -> None:
    for theme, base_weight in themes.items():
        score_map[theme] = score_map.get(theme, 0.0) + base_weight * weight
        source_map.setdefault(theme, [])
        if source not in source_map[theme]:
            source_map[theme].append(source)


def _rank_themes(
    score_map: dict[str, float],
    source_map: dict[str, list[str]],
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for theme, raw_score in score_map.items():
        sources = source_map.get(theme, [])
        bonus = min(max(len(sources) - 1, 0) * 0.08, 0.24)
        confirmed = raw_score + bonus
        ranked.append(
            {
                "theme": theme,
                "label": THEME_LABELS.get(theme, theme),
                "raw_score": round(raw_score, 3),
                "convergence_bonus": round(bonus, 3),
                "confirmed_score": round(confirmed, 3),
                "sources": sources,
            }
        )
    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    top = ranked[0]["confirmed_score"] if ranked else 1.0
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / top, 3)
    return ranked


def _summary(strongest: list[dict[str, Any]]) -> str:
    if not strongest:
        return "The currently modelled chart factors do not produce a distinct spouse financial profile."
    labels = [item["label"] for item in strongest[:4]]
    text = labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " and " + labels[-1]
    return (
        "The spouse's financial profile is most consistent with "
        f"{text}. These are broad symbolic wealth and money-management themes rather than "
        "a prediction of an exact income, net worth or asset value."
    )


def analyze_spouse_wealth_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh_house = _get_house(chart, 7)
    if not seventh_house:
        return {
            "available": False,
            "event": "spouse_wealth",
            "model_version": "v1",
            "reason": "7th house data is unavailable.",
        }

    # Derived-house framework from spouse axis:
    # 2nd from 7th -> natal 8th: spouse resources, accumulated wealth and family assets.
    # 11th from 7th -> natal 5th: gains, income growth and financial upside.
    # 10th from 7th -> natal 4th: income stability through profession and tangible foundations.
    wealth_house_number = 8
    gains_house_number = 5
    stability_house_number = 4

    wealth_house = _get_house(chart, wealth_house_number)
    gains_house = _get_house(chart, gains_house_number)
    stability_house = _get_house(chart, stability_house_number)

    if not wealth_house or not gains_house or not stability_house:
        return {
            "available": False,
            "event": "spouse_wealth",
            "model_version": "v1",
            "reason": "Derived spouse wealth house data is unavailable.",
        }

    score_map: dict[str, float] = {}
    source_map: dict[str, list[str]] = {}
    evidence: list[dict[str, Any]] = []

    factors = (
        ("spouse_resources_house_lord", wealth_house_number, wealth_house, 1.0),
        ("spouse_gains_house_lord", gains_house_number, gains_house, 0.92),
        ("spouse_financial_stability_house_lord", stability_house_number, stability_house, 0.82),
    )

    for factor, house_number, house_data, weight in factors:
        lord = str(house_data.get("lord", "") or "")
        _add_scores(score_map, source_map, PLANET_WEALTH_THEMES.get(lord, {}), factor, weight)
        evidence.append(
            {
                "factor": factor,
                "tier": "primary",
                "strength": round(weight, 3),
                "interpretation": (
                    f"The derived spouse financial house {house_number} is ruled by {lord}, "
                    "contributing to the spouse's wealth and money-management pattern."
                ),
                "details": {"house": house_number, "sign": house_data.get("sign"), "lord": lord},
            }
        )
        for occupant in _planets_in_house(chart, house_number):
            source = f"{occupant.lower()}_in_spouse_financial_house_{house_number}"
            _add_scores(
                score_map,
                source_map,
                PLANET_WEALTH_THEMES.get(occupant, {}),
                source,
                weight * 0.72,
            )
            evidence.append(
                {
                    "factor": source,
                    "tier": "secondary",
                    "strength": round(weight * 0.72, 3),
                    "interpretation": (
                        f"{occupant} occupies derived spouse financial house {house_number} and modifies the wealth pattern."
                    ),
                    "details": {
                        "planet": occupant,
                        "house": house_number,
                        "sign": _get_planet(chart, occupant).get("sign"),
                    },
                }
            )

    for planet, factor, weight in (
        ("Jupiter", "jupiter_wealth_significator", 0.52),
        ("Venus", "venus_material_comfort_significator", 0.46),
        ("Mercury", "mercury_financial_skill_significator", 0.42),
    ):
        data = _get_planet(chart, planet)
        adjusted = weight
        if data.get("house") in {wealth_house_number, gains_house_number, stability_house_number}:
            adjusted += 0.16
        _add_scores(score_map, source_map, PLANET_WEALTH_THEMES.get(planet, {}), factor, adjusted)
        evidence.append(
            {
                "factor": factor,
                "tier": "context",
                "strength": round(adjusted, 3),
                "interpretation": f"{planet} provides contextual evidence for the spouse's financial capacity and money style.",
                "details": {"planet": planet, "house": data.get("house"), "sign": data.get("sign")},
            }
        )

    seventh_lord = str(seventh_house.get("lord", "") or "")
    seventh_lord_data = _get_planet(chart, seventh_lord)
    if seventh_lord:
        weight = 0.38
        if seventh_lord_data.get("house") in {wealth_house_number, gains_house_number, stability_house_number}:
            weight = 0.56
        _add_scores(
            score_map,
            source_map,
            PLANET_WEALTH_THEMES.get(seventh_lord, {}),
            "seventh_lord_financial_context",
            weight,
        )
        evidence.append(
            {
                "factor": "seventh_lord_financial_context",
                "tier": "secondary",
                "strength": weight,
                "interpretation": f"The 7th lord {seventh_lord} adds secondary context to the spouse's financial style.",
                "details": {
                    "planet": seventh_lord,
                    "house": seventh_lord_data.get("house"),
                    "sign": seventh_lord_data.get("sign"),
                },
            }
        )

    ranked = _rank_themes(score_map, source_map)
    strongest = ranked[:5]
    primary_count = sum(1 for item in evidence if item.get("tier") == "primary")
    top_sources = len(strongest[0].get("sources", [])) if strongest else 0
    confidence = round(
        _clamp(
            0.52 + min(primary_count, 3) * 0.055 + min(top_sources, 4) * 0.035 + min(len(evidence), 9) * 0.011,
            0.50,
            0.88,
        ),
        3,
    )

    return {
        "available": True,
        "event": "spouse_wealth",
        "model_version": "v1",
        "confidence": confidence,
        "summary": _summary(strongest),
        "profile": {
            "wealth_themes": [item["label"] for item in strongest],
            "theme_scores": {item["theme"]: item["relative_strength"] for item in ranked},
            "chart_context": {
                "seventh_house": {"sign": seventh_house.get("sign"), "lord": seventh_lord},
                "resources_house": {
                    "natal_house": wealth_house_number,
                    "sign": wealth_house.get("sign"),
                    "lord": wealth_house.get("lord"),
                    "occupants": _planets_in_house(chart, wealth_house_number),
                },
                "gains_house": {
                    "natal_house": gains_house_number,
                    "sign": gains_house.get("sign"),
                    "lord": gains_house.get("lord"),
                    "occupants": _planets_in_house(chart, gains_house_number),
                },
                "stability_house": {
                    "natal_house": stability_house_number,
                    "sign": stability_house.get("sign"),
                    "lord": stability_house.get("lord"),
                    "occupants": _planets_in_house(chart, stability_house_number),
                },
            },
        },
        "strongest_themes": strongest,
        "ranked_themes": ranked,
        "evidence": evidence,
    }
