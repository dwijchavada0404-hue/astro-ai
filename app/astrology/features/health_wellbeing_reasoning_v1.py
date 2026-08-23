from __future__ import annotations

from typing import Any


HEALTH_WELLBEING_THEMES = {
    "vitality_energy": "general vitality, energy management and physical drive",
    "routine_discipline": "health-supportive routines, consistency and daily maintenance",
    "recovery_resilience": "recovery, adaptation and resilience after demanding periods",
    "stress_balance": "pressure management, emotional regulation and sustainable pacing",
    "rest_restoration": "rest, restoration, retreat and recovery capacity",
    "preventive_self_care": "preventive self-care, moderation and attention to wellbeing habits",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _safe_dict(chart.get("houses"))
    return _safe_dict(houses.get(str(number)) or houses.get(number))


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _lord_house(chart: dict[str, Any], house_no: int) -> tuple[str | None, int | None]:
    lord = _house(chart, house_no).get("lord")
    if not isinstance(lord, str) or not lord:
        return None, None
    return lord, _planet_house(chart, lord)


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_health_wellbeing_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess symbolic wellbeing themes without diagnosing or predicting disease.

    The 1st house anchors vitality, the 6th routines and maintenance, the 8th adaptation
    and recovery from demanding transitions, and the 12th rest/restoration. These axes
    are used only for reflective wellbeing themes, never for diagnosis, prognosis,
    lifespan, death, accident, treatment or medication claims.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "health_wellbeing",
            "model_version": "v1",
            "reason": "House data required for Health & Wellbeing reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in HEALTH_WELLBEING_THEMES}
    evidence: list[dict[str, Any]] = []
    house_theme_weights = {
        1: (("vitality_energy", 0.38), ("preventive_self_care", 0.10)),
        6: (("routine_discipline", 0.36), ("preventive_self_care", 0.18)),
        8: (("recovery_resilience", 0.32), ("stress_balance", 0.12)),
        12: (("rest_restoration", 0.36), ("stress_balance", 0.14)),
    }
    supportive_houses = {1, 3, 5, 6, 9, 10, 11, 12}
    for house_no, theme_weights in house_theme_weights.items():
        lord, placed = _lord_house(chart, house_no)
        if not lord:
            continue
        for theme, weight in theme_weights:
            scores[theme] += weight * 0.60
            if placed in supportive_houses:
                scores[theme] += weight * 0.40
                evidence.append({"rule": "wellbeing_house_lord_support", "house": house_no, "lord": lord, "lord_house": placed, "theme": theme})

    significator_themes = {
        "Sun": ("vitality_energy",),
        "Moon": ("stress_balance", "rest_restoration"),
        "Mars": ("vitality_energy", "recovery_resilience"),
        "Saturn": ("routine_discipline", "preventive_self_care"),
        "Jupiter": ("recovery_resilience", "preventive_self_care"),
        "Mercury": ("stress_balance",),
        "Venus": ("rest_restoration",),
    }
    for planet, themes in significator_themes.items():
        placed = _planet_house(chart, planet)
        if placed in supportive_houses:
            for theme in themes:
                scores[theme] += 0.07
                evidence.append({"rule": "wellbeing_significator_support", "planet": planet, "house": placed, "theme": theme})

    first_lord, first_house = _lord_house(chart, 1)
    sixth_lord, sixth_house = _lord_house(chart, 6)
    twelfth_lord, twelfth_house = _lord_house(chart, 12)
    if first_lord and sixth_lord and first_house in supportive_houses and sixth_house in supportive_houses:
        scores["routine_discipline"] += 0.10
        scores["preventive_self_care"] += 0.08
        evidence.append({"rule": "vitality_routine_link", "first_lord": first_lord, "sixth_lord": sixth_lord})
    if first_lord and twelfth_lord and first_house in supportive_houses and twelfth_house in supportive_houses:
        scores["rest_restoration"] += 0.08
        scores["stress_balance"] += 0.08
        evidence.append({"rule": "vitality_rest_link", "first_lord": first_lord, "twelfth_lord": twelfth_lord})

    scores = {key: _bounded(value) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant, dominant_score = ranked[0]
    secondary, secondary_score = ranked[1]
    margin = dominant_score - secondary_score
    confidence = round(min(0.92, 0.42 + 0.035 * len(evidence) + 0.10 * max(0.0, margin)), 2)

    return {
        "available": True,
        "event": "health_wellbeing",
        "model_version": "v1",
        "dominant_theme": dominant,
        "dominant_theme_label": HEALTH_WELLBEING_THEMES[dominant],
        "dominant_score": dominant_score,
        "secondary_theme": secondary,
        "secondary_theme_label": HEALTH_WELLBEING_THEMES[secondary],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [{"theme": k, "label": HEALTH_WELLBEING_THEMES[k], "score": v} for k, v in ranked],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": (
            "Known medical history, symptoms, diagnoses, clinician advice and real-world wellbeing information always override astrological assumptions. "
            "Astrology may discuss only general reflective wellbeing themes."
        ),
        "summary": f"The strongest Health & Wellbeing theme is {HEALTH_WELLBEING_THEMES[dominant]}, followed by {HEALTH_WELLBEING_THEMES[secondary]}.",
        "limitation": (
            "This is not medical advice and cannot diagnose disease, predict illness, prognosis, lifespan, death or accidents, "
            "or recommend medication, treatment, tests, procedures, supplements or changes to professional care."
        ),
        "safety": {
            "diagnosis_allowed": False,
            "disease_prediction_allowed": False,
            "prognosis_allowed": False,
            "lifespan_or_death_prediction_allowed": False,
            "accident_prediction_allowed": False,
            "treatment_or_medication_advice_allowed": False,
        },
    }
