from __future__ import annotations

from typing import Any


THEME_LABELS = {
    "academic_advisory": "academic, advisory or knowledge-oriented education",
    "analytical_commercial": "analytical, commercial or communication-oriented learning",
    "technical_practical": "technical, engineering or practical education",
    "creative_social": "creative, design or social-oriented education",
    "structured_professional": "structured, professional or disciplined education",
    "research_specialist": "research, specialist or depth-oriented study",
    "international_modern": "international, modern or unconventional learning",
    "management_leadership": "management, administration or leadership-oriented study",
}

PLANET_EDUCATION_THEMES = {
    "Sun": {
        "management_leadership": 0.85,
        "structured_professional": 0.55,
    },
    "Moon": {
        "creative_social": 0.65,
        "academic_advisory": 0.45,
    },
    "Mars": {
        "technical_practical": 0.95,
        "structured_professional": 0.45,
    },
    "Mercury": {
        "analytical_commercial": 0.95,
        "academic_advisory": 0.55,
    },
    "Jupiter": {
        "academic_advisory": 1.0,
        "management_leadership": 0.55,
    },
    "Venus": {
        "creative_social": 0.95,
        "analytical_commercial": 0.35,
    },
    "Saturn": {
        "structured_professional": 0.95,
        "technical_practical": 0.55,
    },
    "Rahu": {
        "international_modern": 0.95,
        "analytical_commercial": 0.45,
    },
    "Ketu": {
        "research_specialist": 0.95,
        "technical_practical": 0.35,
    },
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
    for planet_name, raw_data in _safe_dict(chart.get("planets")).items():
        data = _safe_dict(raw_data)
        if data.get("house") == house_number:
            result.append(str(planet_name))
    return result


def _add_theme_scores(
    score_map: dict[str, float],
    source_map: dict[str, list[str]],
    themes: dict[str, float],
    source: str,
    factor_weight: float,
) -> None:
    for theme, base_weight in themes.items():
        contribution = base_weight * factor_weight
        score_map[theme] = score_map.get(theme, 0.0) + contribution
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
        convergence_bonus = min(max(len(sources) - 1, 0) * 0.08, 0.24)
        confirmed_score = raw_score + convergence_bonus
        ranked.append(
            {
                "theme": theme,
                "label": THEME_LABELS.get(theme, theme),
                "raw_score": round(raw_score, 3),
                "convergence_bonus": round(convergence_bonus, 3),
                "confirmed_score": round(confirmed_score, 3),
                "sources": sources,
            }
        )
    ranked.sort(key=lambda item: item["confirmed_score"], reverse=True)
    top_score = ranked[0]["confirmed_score"] if ranked else 1.0
    for item in ranked:
        item["relative_strength"] = round(item["confirmed_score"] / top_score, 3)
    return ranked


def _add_indicator(
    indicators: list[dict[str, Any]],
    factor: str,
    tier: str,
    strength: float,
    interpretation: str,
    details: dict[str, Any],
) -> None:
    indicators.append(
        {
            "factor": factor,
            "tier": tier,
            "strength": round(_clamp(strength), 3),
            "interpretation": interpretation,
            "details": details,
        }
    )


def _build_summary(strongest_themes: list[dict[str, Any]]) -> str:
    if not strongest_themes:
        return (
            "The currently modelled chart factors do not produce a sufficiently distinct "
            "spouse education or intellectual profile."
        )
    labels = [item["label"] for item in strongest_themes[:4]]
    if len(labels) == 1:
        text = labels[0]
    else:
        text = ", ".join(labels[:-1]) + " and " + labels[-1]
    return (
        "The spouse's education and intellectual profile is most consistent with "
        f"{text}. These are broad symbolic study and learning themes rather than a "
        "prediction of one exact degree, institution or qualification."
    )


def analyze_spouse_education_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    seventh_house = _get_house(chart, 7)
    if not seventh_house:
        return {
            "available": False,
            "event": "spouse_education",
            "model_version": "v1",
            "reason": "7th house data is unavailable.",
        }

    # Derived-house framework from the spouse axis:
    # 4th from the 7th -> natal 10th: foundational/formal education environment.
    # 5th from the 7th -> natal 11th: intellect, learning style and applied intelligence.
    # 9th from the 7th -> natal 3rd: higher learning, specialisation and worldview.
    education_house_number = 10
    intellect_house_number = 11
    higher_education_house_number = 3

    education_house = _get_house(chart, education_house_number)
    intellect_house = _get_house(chart, intellect_house_number)
    higher_education_house = _get_house(chart, higher_education_house_number)

    if not education_house or not intellect_house or not higher_education_house:
        return {
            "available": False,
            "event": "spouse_education",
            "model_version": "v1",
            "reason": "Derived spouse education house data is unavailable.",
        }

    score_map: dict[str, float] = {}
    source_map: dict[str, list[str]] = {}
    indicators: list[dict[str, Any]] = []

    derived_factors = (
        (
            "formal_education_house_lord",
            education_house_number,
            education_house,
            1.0,
            "primary",
        ),
        (
            "intellect_house_lord",
            intellect_house_number,
            intellect_house,
            0.92,
            "primary",
        ),
        (
            "higher_education_house_lord",
            higher_education_house_number,
            higher_education_house,
            0.88,
            "primary",
        ),
    )

    for factor, house_number, house_data, weight, tier in derived_factors:
        lord = str(house_data.get("lord", "") or "")
        themes = PLANET_EDUCATION_THEMES.get(lord, {})
        _add_theme_scores(score_map, source_map, themes, factor, weight)
        _add_indicator(
            indicators,
            factor,
            tier,
            weight,
            (
                f"The derived spouse education house {house_number} is ruled by {lord}, "
                "which contributes to the spouse's learning and educational profile."
            ),
            {
                "house": house_number,
                "sign": house_data.get("sign"),
                "lord": lord,
            },
        )

        for occupant in _planets_in_house(chart, house_number):
            occupant_factor = f"{occupant.lower()}_in_derived_education_house_{house_number}"
            _add_theme_scores(
                score_map,
                source_map,
                PLANET_EDUCATION_THEMES.get(occupant, {}),
                occupant_factor,
                weight * 0.72,
            )
            _add_indicator(
                indicators,
                occupant_factor,
                "secondary",
                weight * 0.72,
                (
                    f"{occupant} occupies the derived spouse education house {house_number} "
                    "and modifies the educational or intellectual themes."
                ),
                {
                    "planet": occupant,
                    "house": house_number,
                    "sign": _get_planet(chart, occupant).get("sign"),
                },
            )

    # Mercury and Jupiter are treated as natural learning significators.
    for planet, factor, factor_weight in (
        ("Mercury", "mercury_learning_significator", 0.48),
        ("Jupiter", "jupiter_higher_learning_significator", 0.52),
    ):
        planet_data = _get_planet(chart, planet)
        house = planet_data.get("house")
        contextual_weight = factor_weight
        if house in {
            education_house_number,
            intellect_house_number,
            higher_education_house_number,
        }:
            contextual_weight += 0.18
        _add_theme_scores(
            score_map,
            source_map,
            PLANET_EDUCATION_THEMES.get(planet, {}),
            factor,
            contextual_weight,
        )
        _add_indicator(
            indicators,
            factor,
            "context",
            contextual_weight,
            (
                f"{planet} provides contextual evidence for the spouse's learning style, "
                "knowledge orientation and educational environment."
            ),
            {
                "planet": planet,
                "house": house,
                "sign": planet_data.get("sign"),
            },
        )

    seventh_lord = str(seventh_house.get("lord", "") or "")
    seventh_lord_data = _get_planet(chart, seventh_lord)
    seventh_lord_house = seventh_lord_data.get("house")
    if seventh_lord:
        link_weight = 0.38
        if seventh_lord_house in {
            education_house_number,
            intellect_house_number,
            higher_education_house_number,
        }:
            link_weight = 0.56
        _add_theme_scores(
            score_map,
            source_map,
            PLANET_EDUCATION_THEMES.get(seventh_lord, {}),
            "seventh_lord_education_context",
            link_weight,
        )
        _add_indicator(
            indicators,
            "seventh_lord_education_context",
            "secondary",
            link_weight,
            (
                f"The 7th lord {seventh_lord} adds secondary context to the spouse's "
                "education and intellectual style."
            ),
            {
                "planet": seventh_lord,
                "house": seventh_lord_house,
                "sign": seventh_lord_data.get("sign"),
            },
        )

    ranked_themes = _rank_themes(score_map, source_map)
    strongest_themes = ranked_themes[:5]

    primary_count = sum(1 for item in indicators if item.get("tier") == "primary")
    top_source_count = len(strongest_themes[0].get("sources", [])) if strongest_themes else 0
    confidence = round(
        _clamp(
            0.52
            + min(primary_count, 3) * 0.055
            + min(top_source_count, 4) * 0.035
            + min(len(indicators), 8) * 0.012,
            0.50,
            0.88,
        ),
        3,
    )

    summary = _build_summary(strongest_themes)

    return {
        "available": True,
        "event": "spouse_education",
        "model_version": "v1",
        "confidence": confidence,
        "summary": summary,
        "profile": {
            "education_themes": [item["label"] for item in strongest_themes],
            "theme_scores": {
                item["theme"]: item["relative_strength"] for item in ranked_themes
            },
            "chart_context": {
                "seventh_house": {
                    "sign": seventh_house.get("sign"),
                    "lord": seventh_lord,
                },
                "formal_education_house": {
                    "natal_house": education_house_number,
                    "sign": education_house.get("sign"),
                    "lord": education_house.get("lord"),
                    "occupants": _planets_in_house(chart, education_house_number),
                },
                "intellect_house": {
                    "natal_house": intellect_house_number,
                    "sign": intellect_house.get("sign"),
                    "lord": intellect_house.get("lord"),
                    "occupants": _planets_in_house(chart, intellect_house_number),
                },
                "higher_education_house": {
                    "natal_house": higher_education_house_number,
                    "sign": higher_education_house.get("sign"),
                    "lord": higher_education_house.get("lord"),
                    "occupants": _planets_in_house(chart, higher_education_house_number),
                },
                "mercury": {
                    "house": _get_planet(chart, "Mercury").get("house"),
                    "sign": _get_planet(chart, "Mercury").get("sign"),
                },
                "jupiter": {
                    "house": _get_planet(chart, "Jupiter").get("house"),
                    "sign": _get_planet(chart, "Jupiter").get("sign"),
                },
            },
        },
        "strongest_themes": strongest_themes,
        "ranked_themes": ranked_themes,
        "indicators": indicators,
    }
