from typing import Any


SIGN_CAREER_THEMES = {
    "Aries": [
        "initiative",
        "independence",
        "competition",
        "execution",
    ],
    "Taurus": [
        "stability",
        "finance",
        "resources",
        "practical value creation",
    ],
    "Gemini": [
        "communication",
        "analysis",
        "information",
        "multi-disciplinary work",
    ],
    "Cancer": [
        "care",
        "public interaction",
        "support",
        "people-oriented work",
    ],
    "Leo": [
        "leadership",
        "visibility",
        "management",
        "creative authority",
    ],
    "Virgo": [
        "analysis",
        "service",
        "process improvement",
        "detail-oriented work",
    ],
    "Libra": [
        "negotiation",
        "partnership",
        "advisory work",
        "relationship management",
    ],
    "Scorpio": [
        "research",
        "investigation",
        "risk",
        "complex problem-solving",
    ],
    "Sagittarius": [
        "knowledge",
        "teaching",
        "consulting",
        "large institutions",
    ],
    "Capricorn": [
        "structure",
        "administration",
        "management",
        "long-term responsibility",
    ],
    "Aquarius": [
        "systems",
        "technology",
        "networks",
        "large organisations",
        "innovation",
    ],
    "Pisces": [
        "creativity",
        "advisory work",
        "service",
        "institutional environments",
    ],
}


PLANET_CAREER_THEMES = {
    "Sun": [
        "leadership",
        "authority",
        "visibility",
        "administration",
    ],
    "Moon": [
        "public interaction",
        "adaptability",
        "care",
        "people-oriented work",
    ],
    "Mars": [
        "initiative",
        "competition",
        "engineering",
        "operations",
    ],
    "Mercury": [
        "analysis",
        "communication",
        "commerce",
        "data",
        "documentation",
    ],
    "Jupiter": [
        "advisory work",
        "finance",
        "teaching",
        "law",
        "knowledge",
    ],
    "Venus": [
        "design",
        "relationships",
        "luxury",
        "creative work",
        "negotiation",
    ],
    "Saturn": [
        "structure",
        "governance",
        "compliance",
        "operations",
        "long-term responsibility",
    ],
    "Rahu": [
        "technology",
        "unconventional work",
        "foreign connections",
        "large networks",
    ],
    "Ketu": [
        "research",
        "specialisation",
        "independent work",
        "technical depth",
    ],
}


HOUSE_CAREER_THEMES = {
    1: [
        "self-directed work",
        "personal leadership",
        "independent professional identity",
    ],
    2: [
        "finance",
        "assets",
        "speech",
        "family-linked resources",
    ],
    3: [
        "communication",
        "sales",
        "writing",
        "entrepreneurial effort",
    ],
    4: [
        "property",
        "education",
        "domestic assets",
        "public support",
    ],
    5: [
        "creativity",
        "strategy",
        "education",
        "intellectual work",
    ],
    6: [
        "service",
        "competition",
        "compliance",
        "problem-solving",
    ],
    7: [
        "business",
        "clients",
        "consulting",
        "partnerships",
    ],
    8: [
        "research",
        "risk",
        "investigation",
        "confidential matters",
    ],
    9: [
        "higher knowledge",
        "consulting",
        "law",
        "international exposure",
    ],
    10: [
        "career",
        "leadership",
        "public responsibility",
        "professional recognition",
    ],
    11: [
        "networks",
        "large organisations",
        "income growth",
        "professional gains",
    ],
    12: [
        "foreign environments",
        "large institutions",
        "behind-the-scenes work",
        "remote or international settings",
    ],
}


THEME_GROUPS = {
    "analysis_and_information": {
        "analysis",
        "data",
        "documentation",
        "information",
        "research",
        "investigation",
        "technical depth",
        "complex problem-solving",
    },
    "systems_and_technology": {
        "systems",
        "technology",
        "innovation",
        "large networks",
        "networks",
    },
    "governance_and_structure": {
        "structure",
        "governance",
        "compliance",
        "administration",
        "long-term responsibility",
        "operations",
        "management",
    },
    "communication_and_commerce": {
        "communication",
        "commerce",
        "sales",
        "writing",
        "negotiation",
        "relationship management",
    },
    "institutional_and_global": {
        "large organisations",
        "large institutions",
        "institutional environments",
        "foreign environments",
        "foreign connections",
        "international exposure",
        "remote or international settings",
        "behind-the-scenes work",
    },
    "leadership_and_visibility": {
        "leadership",
        "authority",
        "visibility",
        "professional recognition",
        "public responsibility",
        "personal leadership",
    },
    "advisory_and_knowledge": {
        "advisory work",
        "consulting",
        "teaching",
        "law",
        "knowledge",
        "higher knowledge",
        "strategy",
    },
    "finance_and_resources": {
        "finance",
        "assets",
        "resources",
        "income growth",
        "professional gains",
        "practical value creation",
    },
    "independence_and_execution": {
        "initiative",
        "independence",
        "competition",
        "execution",
        "entrepreneurial effort",
        "self-directed work",
        "independent professional identity",
    },
}


SOURCE_WEIGHTS = {
    "tenth_house_sign": 1.0,
    "tenth_lord": 1.2,
    "tenth_lord_house": 1.1,
    "tenth_house_occupant": 1.3,
}


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []

    for value in values:
        if value not in result:
            result.append(value)

    return result


def _add_evidence(
    evidence: list[dict[str, Any]],
    factor: str,
    source: Any,
    themes: list[str],
    interpretation: str,
) -> None:
    if not themes:
        return

    evidence.append(
        {
            "factor": factor,
            "source": source,
            "weight": SOURCE_WEIGHTS.get(
                factor,
                1.0,
            ),
            "themes": themes,
            "interpretation": interpretation,
        }
    )


def _build_theme_scores(
    evidence: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Score broad career themes from multiple independent
    sources of evidence.
    """

    group_scores: dict[str, dict[str, Any]] = {}

    for group_name, group_terms in THEME_GROUPS.items():

        score = 0.0
        support_sources: list[str] = []
        matched_terms: list[str] = []

        for item in evidence:

            factor = item.get("factor")

            themes = _safe_list(
                item.get("themes")
            )

            matched = [
                theme
                for theme in themes
                if theme in group_terms
            ]

            if not matched:
                continue

            weight = float(
                item.get("weight", 1.0)
            )

            score += weight

            if factor not in support_sources:
                support_sources.append(
                    str(factor)
                )

            for theme in matched:
                if theme not in matched_terms:
                    matched_terms.append(
                        theme
                    )

        group_scores[group_name] = {
            "score": round(score, 2),
            "support_count": len(
                support_sources
            ),
            "sources": support_sources,
            "matched_themes": matched_terms,
        }

    return group_scores


def _rank_theme_groups(
    group_scores: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Rank broad career themes by weighted support and
    independent evidence count.
    """

    ranked = []

    for theme, details in group_scores.items():

        score = float(
            details.get(
                "score",
                0.0,
            )
        )

        support_count = int(
            details.get(
                "support_count",
                0,
            )
        )

        if score <= 0:
            continue

        ranked.append(
            {
                "theme": theme,
                "score": score,
                "support_count": support_count,
                "sources": details.get(
                    "sources",
                    [],
                ),
                "matched_themes": details.get(
                    "matched_themes",
                    [],
                ),
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["score"],
            -item["support_count"],
            item["theme"],
        )
    )

    return ranked


def _build_professional_direction(
    ranked_groups: list[dict[str, Any]],
) -> str:
    """
    Create a high-level career direction summary from
    the strongest grouped signals.
    """

    if not ranked_groups:
        return (
            "The available career indicators do not yet "
            "produce a strong professional direction."
        )

    strongest = [
        item["theme"]
        for item in ranked_groups[:3]
    ]

    readable = {
        "analysis_and_information": (
            "analysis, information handling and problem-solving"
        ),
        "systems_and_technology": (
            "systems, technology and network-oriented work"
        ),
        "governance_and_structure": (
            "governance, structure, compliance and operations"
        ),
        "communication_and_commerce": (
            "communication, commerce and documentation"
        ),
        "institutional_and_global": (
            "large institutions, global environments or "
            "behind-the-scenes professional settings"
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
            "independent execution, initiative and competition"
        ),
    }

    phrases = [
        readable.get(
            theme,
            theme.replace("_", " "),
        )
        for theme in strongest
    ]

    if len(phrases) == 1:
        body = phrases[0]

    elif len(phrases) == 2:
        body = (
            f"{phrases[0]} and {phrases[1]}"
        )

    else:
        body = (
            f"{phrases[0]}, {phrases[1]}, "
            f"and {phrases[2]}"
        )

    return (
        "The strongest career pattern currently points toward "
        f"{body}."
    )


def interpret_career(
    career_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert 10th-house reasoning into weighted
    professional themes.

    Multiple independent chart factors supporting the
    same broad theme increase its strength.
    """

    if not career_analysis.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career reasoning is unavailable."
            ),
        }

    tenth_house = _safe_dict(
        career_analysis.get(
            "tenth_house"
        )
    )

    tenth_lord = _safe_dict(
        career_analysis.get(
            "tenth_lord"
        )
    )

    tenth_sign = tenth_house.get(
        "sign"
    )

    tenth_lord_name = tenth_lord.get(
        "planet"
    )

    tenth_lord_house = tenth_lord.get(
        "house"
    )

    occupants = _safe_list(
        tenth_house.get(
            "occupants"
        )
    )

    all_themes: list[str] = []
    evidence: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # 10TH HOUSE SIGN
    # ---------------------------------------------------------

    sign_themes = SIGN_CAREER_THEMES.get(
        tenth_sign,
        [],
    )

    all_themes.extend(
        sign_themes
    )

    _add_evidence(
        evidence=evidence,
        factor="tenth_house_sign",
        source=tenth_sign,
        themes=sign_themes,
        interpretation=(
            f"An {tenth_sign} 10th house emphasises "
            + ", ".join(sign_themes)
            + " in professional life."
        ),
    )

    # ---------------------------------------------------------
    # 10TH LORD
    # ---------------------------------------------------------

    lord_themes = PLANET_CAREER_THEMES.get(
        tenth_lord_name,
        [],
    )

    all_themes.extend(
        lord_themes
    )

    _add_evidence(
        evidence=evidence,
        factor="tenth_lord",
        source=tenth_lord_name,
        themes=lord_themes,
        interpretation=(
            f"With {tenth_lord_name} ruling the 10th house, "
            "professional development may involve "
            + ", ".join(lord_themes)
            + "."
        ),
    )

    # ---------------------------------------------------------
    # 10TH LORD HOUSE
    # ---------------------------------------------------------

    lord_house_themes = HOUSE_CAREER_THEMES.get(
        tenth_lord_house,
        [],
    )

    all_themes.extend(
        lord_house_themes
    )

    _add_evidence(
        evidence=evidence,
        factor="tenth_lord_house",
        source=tenth_lord_house,
        themes=lord_house_themes,
        interpretation=(
            f"The 10th lord in the {tenth_lord_house}th house "
            "connects career with "
            + ", ".join(lord_house_themes)
            + "."
        ),
    )

    # ---------------------------------------------------------
    # PLANETS OCCUPYING THE 10TH HOUSE
    # ---------------------------------------------------------

    occupant_details: list[
        dict[str, Any]
    ] = []

    for planet in occupants:

        if not isinstance(
            planet,
            str,
        ):
            continue

        planet_themes = (
            PLANET_CAREER_THEMES.get(
                planet,
                [],
            )
        )

        all_themes.extend(
            planet_themes
        )

        occupant_details.append(
            {
                "planet": planet,
                "themes": planet_themes,
            }
        )

        _add_evidence(
            evidence=evidence,
            factor="tenth_house_occupant",
            source=planet,
            themes=planet_themes,
            interpretation=(
                f"{planet} in the 10th house adds "
                + ", ".join(
                    planet_themes
                )
                + " to professional expression."
            ),
        )

    # ---------------------------------------------------------
    # WEIGHTED GROUP SCORING
    # ---------------------------------------------------------

    group_scores = (
        _build_theme_scores(
            evidence
        )
    )

    ranked_groups = (
        _rank_theme_groups(
            group_scores
        )
    )

    professional_direction = (
        _build_professional_direction(
            ranked_groups
        )
    )

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    return {
        "available": True,
        "tenth_house_sign": tenth_sign,
        "tenth_lord": tenth_lord_name,
        "tenth_lord_house": tenth_lord_house,
        "tenth_house_occupants": occupants,
        "occupant_details": occupant_details,
        "career_themes": _unique(
            all_themes
        ),
        "theme_groups": ranked_groups,
        "professional_direction": (
            professional_direction
        ),
        "evidence": evidence,
    }