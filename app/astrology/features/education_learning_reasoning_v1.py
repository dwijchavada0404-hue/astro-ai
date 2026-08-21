from __future__ import annotations

from typing import Any


EDUCATION_THEMES = {
    "foundational_learning": "foundational education, study discipline and learning continuity",
    "higher_education": "advanced study, specialization and higher education",
    "analytical_learning": "analysis, logic, numeracy and structured problem-solving",
    "communication_learning": "language, writing, communication and knowledge exchange",
    "research_depth": "research, investigation and depth-oriented learning",
    "creative_learning": "creative, design-oriented and expressive learning",
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


def analyze_education_learning_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess natal education and learning patterns using multi-factor evidence.

    The 4th house is treated as the main foundation for formal learning, the 5th for
    intelligence/retention, the 9th for advanced learning, and the 3rd for skills and
    communication. Mercury and Jupiter are primary significators, with Saturn, Venus,
    Mars and Moon used only as modest supporting signals. No single planet or house is
    mapped deterministically to a degree, exam result, institution or profession.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "education_learning",
            "model_version": "v1",
            "reason": "House data required for Education & Learning reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in EDUCATION_THEMES}
    evidence: list[dict[str, Any]] = []

    fourth_lord, fourth_house = _lord_house(chart, 4)
    fifth_lord, fifth_house = _lord_house(chart, 5)
    ninth_lord, ninth_house = _lord_house(chart, 9)
    third_lord, third_house = _lord_house(chart, 3)
    eighth_lord, eighth_house = _lord_house(chart, 8)

    if fourth_lord:
        scores["foundational_learning"] += 0.24
        if fourth_house in {1, 2, 4, 5, 9, 10, 11}:
            scores["foundational_learning"] += 0.30
            evidence.append({"rule": "fourth_lord_supportive_placement", "lord": fourth_lord, "house": fourth_house})

    if fifth_lord:
        scores["foundational_learning"] += 0.12
        scores["analytical_learning"] += 0.16
        if fifth_house in {1, 2, 3, 5, 9, 10, 11}:
            scores["analytical_learning"] += 0.24
            evidence.append({"rule": "fifth_lord_learning_support", "lord": fifth_lord, "house": fifth_house})

    if ninth_lord:
        scores["higher_education"] += 0.26
        if ninth_house in {1, 4, 5, 9, 10, 11}:
            scores["higher_education"] += 0.34
            evidence.append({"rule": "ninth_lord_higher_learning_support", "lord": ninth_lord, "house": ninth_house})

    if third_lord:
        scores["communication_learning"] += 0.22
        if third_house in {1, 2, 3, 5, 9, 10, 11}:
            scores["communication_learning"] += 0.28
            evidence.append({"rule": "third_lord_skill_learning_support", "lord": third_lord, "house": third_house})

    if eighth_lord:
        scores["research_depth"] += 0.16
        if eighth_house in {5, 8, 9, 10, 11, 12}:
            scores["research_depth"] += 0.26
            evidence.append({"rule": "eighth_lord_research_support", "lord": eighth_lord, "house": eighth_house})

    significator_themes = {
        "Mercury": ("analytical_learning", "communication_learning"),
        "Jupiter": ("higher_education", "foundational_learning"),
        "Saturn": ("foundational_learning", "research_depth"),
        "Venus": ("creative_learning",),
        "Mars": ("analytical_learning",),
        "Moon": ("foundational_learning", "creative_learning"),
    }
    supportive_houses = {1, 2, 3, 4, 5, 9, 10, 11}
    for planet, themes in significator_themes.items():
        placed = _planet_house(chart, planet)
        if placed in supportive_houses:
            for theme in themes:
                scores[theme] += 0.08
                evidence.append({"rule": "education_significator_support", "planet": planet, "house": placed, "theme": theme})

    # Cross-links matter more than one-planet = one-course rules.
    if fourth_lord and ninth_lord and fourth_house in {5, 9} and ninth_house in {4, 5, 9}:
        scores["higher_education"] += 0.12
        scores["foundational_learning"] += 0.08
        evidence.append({"rule": "formal_higher_learning_link", "fourth_lord": fourth_lord, "ninth_lord": ninth_lord})
    if fifth_lord and eighth_lord and fifth_house in {8, 9, 10, 11} and eighth_house in {5, 8, 9, 10, 11}:
        scores["research_depth"] += 0.12
        evidence.append({"rule": "intellect_research_link", "fifth_lord": fifth_lord, "eighth_lord": eighth_lord})

    scores = {key: _bounded(value) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant, dominant_score = ranked[0]
    secondary, secondary_score = ranked[1]
    margin = dominant_score - secondary_score
    confidence = round(min(0.94, 0.46 + 0.035 * len(evidence) + 0.12 * max(0.0, margin)), 2)

    return {
        "available": True,
        "event": "education_learning",
        "model_version": "v1",
        "dominant_theme": dominant,
        "dominant_theme_label": EDUCATION_THEMES[dominant],
        "dominant_score": dominant_score,
        "secondary_theme": secondary,
        "secondary_theme_label": EDUCATION_THEMES[secondary],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [
            {"theme": theme, "label": EDUCATION_THEMES[theme], "score": score}
            for theme, score in ranked
        ],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": (
            "Known education history, qualifications, exam results and current study status override astrological inference. "
            "Astrology may interpret learning tendencies but must not invent degrees, admissions, scores or completed qualifications."
        ),
        "summary": (
            f"The strongest Education & Learning theme is {EDUCATION_THEMES[dominant]}, followed by "
            f"{EDUCATION_THEMES[secondary]}."
        ),
        "limitation": (
            "This is symbolic learning-pattern analysis. It does not guarantee admission, examination success, grades, scholarships, "
            "degrees, professional licences, employment outcomes or suitability for a specific institution or course."
        ),
    }
