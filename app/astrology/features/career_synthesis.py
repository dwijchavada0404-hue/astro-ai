from typing import Any


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_interpretations(
    indicators: Any,
    allowed_types: set[str] | None = None,
    limit: int = 6,
) -> list[str]:
    """
    Extract unique human-readable interpretations.
    """

    results: list[str] = []

    for indicator in _safe_list(
        indicators
    ):
        indicator_type = indicator.get(
            "type"
        )

        if (
            allowed_types is not None
            and indicator_type not in allowed_types
        ):
            continue

        interpretation = indicator.get(
            "interpretation"
        )

        if not isinstance(
            interpretation,
            str,
        ):
            continue

        interpretation = (
            interpretation.strip()
        )

        if (
            interpretation
            and interpretation
            not in results
        ):
            results.append(
                interpretation
            )

        if len(results) >= limit:
            break

    return results


def _build_dominant_themes(
    career_interpretation: dict[str, Any],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Return the strongest grouped professional themes.

    The grouped interpretation layer has already combined
    multiple chart signals, so we preserve that ranking here.
    """

    groups = _safe_list(
        career_interpretation.get(
            "theme_groups"
        )
    )

    return groups[:limit]


def _build_work_environment(
    dominant_themes: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Separate work-environment indications from
    core professional-function indications.
    """

    institutional = None

    for theme in dominant_themes:

        if (
            theme.get("theme")
            == "institutional_and_global"
        ):
            institutional = theme
            break

    if not institutional:
        return {
            "active": False,
            "summary": (
                "No strong institutional or global "
                "work-environment pattern is currently dominant."
            ),
        }

    matched = institutional.get(
        "matched_themes",
        [],
    )

    return {
        "active": True,
        "score": _safe_float(
            institutional.get(
                "score"
            )
        ),
        "support_count": institutional.get(
            "support_count"
        ),
        "summary": (
            "The chart shows a meaningful work-environment "
            "connection with large organisations, institutional "
            "settings, foreign or international exposure, remote "
            "work, or behind-the-scenes responsibilities. "
            "This describes the likely professional environment "
            "more than a specific occupation."
        ),
        "themes": matched,
    }


def _build_core_function(
    dominant_themes: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Identify the strongest professional-function themes.

    Institutional/global themes are excluded here because
    they describe environment rather than the core type of work.
    """

    function_groups = [
        item
        for item in dominant_themes
        if item.get("theme")
        != "institutional_and_global"
    ]

    top = function_groups[:3]

    readable = {
        "analysis_and_information": (
            "analysis, information handling, data, "
            "documentation and problem-solving"
        ),
        "systems_and_technology": (
            "systems, technology, networks and innovation"
        ),
        "governance_and_structure": (
            "governance, compliance, structure and operations"
        ),
        "communication_and_commerce": (
            "communication, commerce and documentation"
        ),
        "leadership_and_visibility": (
            "leadership, authority and professional visibility"
        ),
        "advisory_and_knowledge": (
            "advisory, knowledge and consulting-oriented work"
        ),
        "finance_and_resources": (
            "finance, resources and value creation"
        ),
        "independence_and_execution": (
            "initiative, independent execution and competition"
        ),
    }

    phrases = [
        readable.get(
            item.get("theme"),
            str(
                item.get("theme", "")
            ).replace("_", " "),
        )
        for item in top
    ]

    if not phrases:
        summary = (
            "No sufficiently strong professional-function "
            "pattern is currently available."
        )

    elif len(phrases) == 1:
        summary = (
            "The strongest professional-function pattern "
            f"centres on {phrases[0]}."
        )

    elif len(phrases) == 2:
        summary = (
            "The strongest professional-function pattern "
            f"combines {phrases[0]} with {phrases[1]}."
        )

    else:
        summary = (
            "The strongest professional-function pattern "
            f"combines {phrases[0]}, {phrases[1]}, "
            f"and {phrases[2]}."
        )

    return {
        "summary": summary,
        "themes": top,
    }


def _build_career_strengths(
    career_planets: dict[str, Any],
) -> list[str]:
    """
    Extract positive planetary career evidence.
    """

    return _extract_interpretations(
        career_planets.get(
            "indicators"
        ),
        allowed_types={"positive"},
        limit=6,
    )


def _build_career_challenges(
    career_planets: dict[str, Any],
) -> list[str]:
    """
    Extract challenge signals without overstating them.
    """

    return _extract_interpretations(
        career_planets.get(
            "indicators"
        ),
        allowed_types={"challenge"},
        limit=5,
    )


def _calculate_outlook(
    career_planets: dict[str, Any],
    dominant_themes: list[dict[str, Any]],
) -> tuple[str, float]:
    """
    Build a conservative overall career outlook.

    Planetary positives and challenges are considered,
    but strong 10th-house theme convergence also matters.
    """

    scores = _safe_dict(
        career_planets.get(
            "scores"
        )
    )

    positive_score = _safe_float(
        scores.get(
            "positive_score"
        )
    )

    challenge_score = _safe_float(
        scores.get(
            "challenge_score"
        )
    )

    convergent_groups = [
        group
        for group in dominant_themes
        if int(
            group.get(
                "support_count",
                0,
            )
        ) >= 2
    ]

    convergence_bonus = (
        0.4
        if convergent_groups
        else 0.0
    )

    net_score = (
        positive_score
        - challenge_score
        + convergence_bonus
    )

    if net_score >= 2.5:
        outlook = "favourable"
        confidence = 0.85

    elif net_score >= 1.0:
        outlook = "generally_favourable"
        confidence = 0.75

    elif challenge_score > positive_score:
        outlook = "mixed"
        confidence = 0.65

    else:
        outlook = "developing"
        confidence = 0.6

    return outlook, confidence


def synthesize_career(
    career_reasoning: dict[str, Any],
    career_interpretation: dict[str, Any],
    career_planets: dict[str, Any],
) -> dict[str, Any]:
    """
    Combine the major career-analysis layers.

    Inputs:
    - 10th-house reasoning
    - grouped career interpretation
    - career planetary strength analysis

    This function does not calculate new planetary positions.
    """

    if not career_reasoning.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career reasoning is unavailable."
            ),
        }

    if not career_interpretation.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career interpretation is unavailable."
            ),
        }

    if not career_planets.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career planetary analysis is unavailable."
            ),
        }

    dominant_themes = (
        _build_dominant_themes(
            career_interpretation
        )
    )

    work_environment = (
        _build_work_environment(
            dominant_themes
        )
    )

    core_function = (
        _build_core_function(
            dominant_themes
        )
    )

    career_strengths = (
        _build_career_strengths(
            career_planets
        )
    )

    career_challenges = (
        _build_career_challenges(
            career_planets
        )
    )

    outlook, confidence = (
        _calculate_outlook(
            career_planets,
            dominant_themes,
        )
    )

    if outlook == "favourable":
        summary = (
            "The chart shows a favourable career pattern, "
            "with multiple supportive professional indicators "
            "and a clear concentration of career themes."
        )

    elif outlook == "generally_favourable":
        summary = (
            "The chart is generally supportive of career growth, "
            "although some planetary factors may require patience, "
            "adjustment or sustained effort."
        )

    elif outlook == "mixed":
        summary = (
            "The career pattern is mixed, with meaningful strengths "
            "alongside challenges that may affect the pace or ease "
            "of professional development."
        )

    else:
        summary = (
            "The career pattern appears developmental, suggesting "
            "that professional direction may strengthen gradually "
            "through experience and maturity."
        )

    tenth_house = _safe_dict(
        career_reasoning.get(
            "tenth_house"
        )
    )

    tenth_lord = _safe_dict(
        career_reasoning.get(
            "tenth_lord"
        )
    )

    return {
        "available": True,
        "outlook": outlook,
        "confidence": confidence,
        "summary": summary,
        "tenth_house": {
            "sign": tenth_house.get(
                "sign"
            ),
            "lord": tenth_house.get(
                "lord"
            ),
            "occupants": tenth_house.get(
                "occupants",
                [],
            ),
        },
        "tenth_lord": {
            "planet": tenth_lord.get(
                "planet"
            ),
            "house": tenth_lord.get(
                "house"
            ),
            "sign": tenth_lord.get(
                "sign"
            ),
        },
        "professional_direction": (
            career_interpretation.get(
                "professional_direction"
            )
        ),
        "core_professional_function": (
            core_function
        ),
        "work_environment": (
            work_environment
        ),
        "dominant_themes": (
            dominant_themes
        ),
        "strengths": (
            career_strengths
        ),
        "challenges": (
            career_challenges
        ),
        "planetary_scores": (
            career_planets.get(
                "scores",
                {},
            )
        ),
    }