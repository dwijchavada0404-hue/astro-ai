from __future__ import annotations

from typing import Any

from app.astrology.dignity import (
    evaluate_planetary_dignities,
)


# =========================================================
# CONSTANTS
# =========================================================

PLANET_PROFESSION_THEMES = {
    "Sun": [
        "leadership",
        "management",
        "government or administration",
        "public-facing responsibility",
    ],
    "Moon": [
        "people-oriented work",
        "care or service",
        "public interaction",
        "hospitality or support functions",
    ],
    "Mars": [
        "technical work",
        "engineering",
        "operations",
        "entrepreneurial activity",
        "execution-oriented roles",
    ],
    "Mercury": [
        "communication",
        "analysis",
        "commerce",
        "technology",
        "consulting",
    ],
    "Jupiter": [
        "advisory work",
        "finance",
        "education",
        "law",
        "management",
    ],
    "Venus": [
        "design",
        "creative industries",
        "luxury or lifestyle sectors",
        "relationship-oriented business",
        "client-facing work",
    ],
    "Saturn": [
        "structured corporate work",
        "operations",
        "engineering or infrastructure",
        "compliance",
        "long-term management",
    ],
    "Rahu": [
        "technology",
        "foreign-linked work",
        "digital industries",
        "unconventional sectors",
        "large networks",
    ],
    "Ketu": [
        "specialised work",
        "research",
        "technical depth",
        "independent expertise",
    ],
}


HOUSE_PROFESSION_THEMES = {
    1: [
        "independent or self-directed work",
        "personal leadership",
    ],
    2: [
        "finance",
        "banking",
        "family business",
        "speech or advisory work",
    ],
    3: [
        "communication",
        "sales",
        "media",
        "entrepreneurial activity",
    ],
    4: [
        "property",
        "real estate",
        "education",
        "domestic or infrastructure sectors",
    ],
    5: [
        "education",
        "creativity",
        "strategy",
        "advisory work",
    ],
    6: [
        "service",
        "healthcare",
        "operations",
        "compliance or dispute-related work",
    ],
    7: [
        "business",
        "consulting",
        "client-facing work",
        "partnership-based professions",
    ],
    8: [
        "research",
        "risk",
        "investigation",
        "insurance",
        "specialised finance",
    ],
    9: [
        "law",
        "education",
        "consulting",
        "international work",
        "advisory professions",
    ],
    10: [
        "management",
        "leadership",
        "corporate responsibility",
        "public professional visibility",
    ],
    11: [
        "large organisations",
        "networks",
        "technology",
        "commerce",
        "income-oriented professions",
    ],
    12: [
        "foreign-linked work",
        "multinational environments",
        "hospitals or institutions",
        "research",
        "behind-the-scenes work",
    ],
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_dict(
    value: Any,
) -> dict[str, Any]:

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _unique(
    values: list[str],
) -> list[str]:

    result = []

    for value in values:

        if (
            value
            and value not in result
        ):
            result.append(
                value
            )

    return result


# =========================================================
# CHART HELPERS
# =========================================================

def _get_house(
    chart: dict[str, Any],
    house_number: int,
) -> dict[str, Any]:

    houses = _safe_dict(
        chart.get(
            "houses"
        )
    )

    return _safe_dict(
        houses.get(
            str(
                house_number
            )
        )
    )


def _get_planet(
    chart: dict[str, Any],
    planet: str | None,
) -> dict[str, Any]:

    if not planet:
        return {}

    planets = _safe_dict(
        chart.get(
            "planets"
        )
    )

    return _safe_dict(
        planets.get(
            planet
        )
    )


def _planets_in_house(
    chart: dict[str, Any],
    house_number: int,
) -> list[str]:

    planets = _safe_dict(
        chart.get(
            "planets"
        )
    )

    result = []

    for (
        planet_name,
        raw_data,
    ) in planets.items():

        data = _safe_dict(
            raw_data
        )

        if (
            data.get(
                "house"
            )
            == house_number
        ):
            result.append(
                str(
                    planet_name
                )
            )

    return result


def _dignity_map(
    chart: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    dignities = (
        evaluate_planetary_dignities(
            chart
        )
    )

    return {
        str(
            item.get(
                "planet"
            )
        ): item
        for item in dignities
        if isinstance(
            item,
            dict,
        )
        and item.get(
            "planet"
        )
    }


# =========================================================
# PROFESSION HOUSE
# =========================================================

def _spouse_profession_house_number() -> int:
    """
    The spouse is represented by the 7th house.

    The spouse's profession is traditionally studied from
    the 10th house counted from the 7th.

    Counting inclusively:

        7 -> 1
        8 -> 2
        ...
        4 -> 10

    Therefore the natal 4th house acts as the spouse's
    professional house.
    """

    return 4


# =========================================================
# EVIDENCE HELPERS
# =========================================================

def _indicator(
    factor: str,
    category: str,
    strength: float,
    interpretation: str,
    themes: list[str],
    **details: Any,
) -> dict[str, Any]:

    result = {
        "factor": factor,
        "category": category,
        "strength": round(
            _clamp(
                strength
            ),
            3,
        ),
        "interpretation": interpretation,
        "themes": (
            themes
        ),
    }

    if details:

        result[
            "details"
        ] = details

    return result


def _rank_themes(
    indicators: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    scores: dict[str, float] = {}

    sources: dict[
        str,
        list[str],
    ] = {}

    for indicator in indicators:

        strength = _safe_float(
            indicator.get(
                "strength"
            )
        )

        factor = str(
            indicator.get(
                "factor",
                "",
            )
        )

        themes = indicator.get(
            "themes",
            [],
        )

        if not isinstance(
            themes,
            list,
        ):
            continue

        for theme in themes:

            theme_name = str(
                theme
            )

            if not theme_name:
                continue

            scores[
                theme_name
            ] = (
                scores.get(
                    theme_name,
                    0.0,
                )
                + strength
            )

            sources.setdefault(
                theme_name,
                [],
            )

            if (
                factor
                and factor
                not in sources[
                    theme_name
                ]
            ):
                sources[
                    theme_name
                ].append(
                    factor
                )

    if not scores:

        return []

    maximum = max(
        scores.values()
    )

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            item[
                1
            ]
        ),
        reverse=True,
    )

    return [
        {
            "theme": theme,
            "raw_score": round(
                score,
                3,
            ),
            "relative_strength": round(
                score / maximum,
                3,
            ),
            "sources": (
                sources.get(
                    theme,
                    [],
                )
            ),
        }
        for (
            theme,
            score,
        ) in ranked
    ]


# =========================================================
# MAIN ENGINE
# =========================================================

def analyze_spouse_profession_v1(
    chart: dict[str, Any],
) -> dict[str, Any]:

    if not isinstance(
        chart,
        dict,
    ):
        raise ValueError(
            "chart must be a dictionary."
        )

    seventh_house = (
        _get_house(
            chart,
            7,
        )
    )

    if not seventh_house:

        return {
            "available": False,
            "reason": (
                "7th house data is unavailable."
            ),
        }

    profession_house_number = (
        _spouse_profession_house_number()
    )

    profession_house = (
        _get_house(
            chart,
            profession_house_number,
        )
    )

    if not profession_house:

        return {
            "available": False,
            "reason": (
                "The spouse profession house data "
                "is unavailable."
            ),
        }

    seventh_lord = (
        seventh_house.get(
            "lord"
        )
    )

    seventh_lord_data = (
        _get_planet(
            chart,
            seventh_lord,
        )
    )

    profession_lord = (
        profession_house.get(
            "lord"
        )
    )

    profession_lord_data = (
        _get_planet(
            chart,
            profession_lord,
        )
    )

    profession_occupants = (
        _planets_in_house(
            chart,
            profession_house_number,
        )
    )

    dignity_map = (
        _dignity_map(
            chart
        )
    )

    seventh_lord_dignity = (
        _safe_dict(
            dignity_map.get(
                str(
                    seventh_lord
                )
            )
        )
    )

    profession_lord_dignity = (
        _safe_dict(
            dignity_map.get(
                str(
                    profession_lord
                )
            )
        )
    )

    indicators = []

    # =====================================================
    # PRIMARY: 10TH FROM THE 7TH
    # =====================================================

    profession_sign = (
        profession_house.get(
            "sign"
        )
    )

    profession_lord_house = (
        profession_lord_data.get(
            "house"
        )
    )

    profession_lord_sign = (
        profession_lord_data.get(
            "sign"
        )
    )

    profession_lord_themes = (
        PLANET_PROFESSION_THEMES.get(
            str(
                profession_lord
            ),
            [],
        )
    )

    indicators.append(
        _indicator(
            "spouse_tenth_lord",
            "primary",
            1.0,
            (
                f"The spouse's professional house is the "
                f"natal {profession_house_number}th house, "
                f"ruled by {profession_lord}. The nature "
                "of this lord forms the primary profession "
                "indicator."
            ),
            profession_lord_themes,
            profession_house=(
                profession_house_number
            ),
            profession_sign=(
                profession_sign
            ),
            profession_lord=(
                profession_lord
            ),
        )
    )

    # =====================================================
    # PRIMARY: PROFESSION LORD PLACEMENT
    # =====================================================

    if profession_lord_house:

        house_themes = (
            HOUSE_PROFESSION_THEMES.get(
                int(
                    profession_lord_house
                ),
                [],
            )
        )

        indicators.append(
            _indicator(
                "spouse_tenth_lord_house",
                "primary",
                0.95,
                (
                    f"The spouse's profession lord "
                    f"{profession_lord} is placed in the "
                    f"{profession_lord_house}th natal house. "
                    "This modifies the likely professional "
                    "environment and work themes."
                ),
                house_themes,
                lord=(
                    profession_lord
                ),
                house=(
                    profession_lord_house
                ),
                sign=(
                    profession_lord_sign
                ),
            )
        )

    # =====================================================
    # PRIMARY: OCCUPANTS OF SPOUSE PROFESSION HOUSE
    # =====================================================

    for planet in profession_occupants:

        planet_themes = (
            PLANET_PROFESSION_THEMES.get(
                planet,
                [],
            )
        )

        indicators.append(
            _indicator(
                "planet_in_spouse_tenth",
                "primary",
                0.85,
                (
                    f"{planet} occupies the spouse's "
                    "professional house and therefore adds "
                    "its occupational themes directly."
                ),
                planet_themes,
                planet=planet,
                profession_house=(
                    profession_house_number
                ),
            )
        )

    # =====================================================
    # SECONDARY: 7TH LORD
    # =====================================================

    seventh_lord_house = (
        seventh_lord_data.get(
            "house"
        )
    )

    seventh_lord_sign = (
        seventh_lord_data.get(
            "sign"
        )
    )

    seventh_lord_themes = (
        PLANET_PROFESSION_THEMES.get(
            str(
                seventh_lord
            ),
            [],
        )
    )

    indicators.append(
        _indicator(
            "seventh_lord_professional_modifier",
            "secondary",
            0.65,
            (
                f"The 7th lord {seventh_lord} acts as a "
                "secondary modifier for the spouse's broad "
                "professional style."
            ),
            seventh_lord_themes,
            planet=(
                seventh_lord
            ),
            house=(
                seventh_lord_house
            ),
            sign=(
                seventh_lord_sign
            ),
        )
    )

    if seventh_lord_house:

        secondary_house_themes = (
            HOUSE_PROFESSION_THEMES.get(
                int(
                    seventh_lord_house
                ),
                [],
            )
        )

        indicators.append(
            _indicator(
                "seventh_lord_house_professional_modifier",
                "secondary",
                0.55,
                (
                    f"The 7th lord is located in the "
                    f"{seventh_lord_house}th house, providing "
                    "additional context about the spouse's "
                    "professional orientation."
                ),
                secondary_house_themes,
                house=(
                    seventh_lord_house
                ),
            )
        )

    # =====================================================
    # DIGNITY CONTEXT
    # =====================================================

    profession_lord_dignity_name = (
        profession_lord_dignity.get(
            "dignity"
        )
    )

    profession_lord_dignity_strength = (
        _safe_float(
            profession_lord_dignity.get(
                "strength"
            ),
            0.5,
        )
    )

    if profession_lord_dignity_name in (
        "exalted",
        "own_sign",
    ):

        indicators.append(
            _indicator(
                "spouse_profession_lord_dignity",
                "support",
                0.55,
                (
                    "The spouse profession lord has strong "
                    "planetary dignity, increasing confidence "
                    "in the professional themes it represents."
                ),
                [
                    "professional stability",
                    "strong career capacity",
                ],
                dignity=(
                    profession_lord_dignity_name
                ),
            )
        )

    elif (
        profession_lord_dignity_name
        == "debilitated"
    ):

        indicators.append(
            _indicator(
                "spouse_profession_lord_dignity",
                "context",
                0.35,
                (
                    "The spouse profession lord is debilitated. "
                    "This may describe a less linear career path "
                    "or a profession requiring adaptation rather "
                    "than identifying a specific occupation."
                ),
                [
                    "career adjustment",
                    "non-linear professional development",
                ],
                dignity=(
                    profession_lord_dignity_name
                ),
            )
        )

    # =====================================================
    # RANK THEMES
    # =====================================================

    ranked_themes = (
        _rank_themes(
            indicators
        )
    )

    strongest_themes = [
        item[
            "theme"
        ]
        for item in ranked_themes[
            :6
        ]
    ]

    # =====================================================
    # BROAD CAREER STYLE
    # =====================================================

    style = []

    combined_text = " ".join(
        strongest_themes
    ).lower()

    if any(
        token in combined_text
        for token in (
            "management",
            "leadership",
            "corporate",
            "responsibility",
        )
    ):

        style.append(
            "structured and responsibility-oriented"
        )

    if any(
        token in combined_text
        for token in (
            "technical",
            "engineering",
            "technology",
            "operations",
        )
    ):

        style.append(
            "technical or execution-oriented"
        )

    if any(
        token in combined_text
        for token in (
            "finance",
            "banking",
            "commerce",
            "advisory",
            "consulting",
        )
    ):

        style.append(
            "commercial, analytical or advisory"
        )

    if any(
        token in combined_text
        for token in (
            "foreign",
            "international",
            "multinational",
        )
    ):

        style.append(
            "potentially international or foreign-linked"
        )

    style = (
        _unique(
            style
        )
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    if strongest_themes:

        top_text = ", ".join(
            strongest_themes[
                :4
            ]
        )

        summary = (
            "The strongest spouse-profession indicators "
            f"point toward themes such as {top_text}. "
            "These should be read as broad occupational "
            "patterns rather than as a prediction of one "
            "specific job title."
        )

    else:

        summary = (
            "The chart does not produce a sufficiently "
            "specific spouse-profession pattern from the "
            "currently modelled evidence."
        )

    primary_strength = sum(
        _safe_float(
            item.get(
                "strength"
            )
        )
        for item in indicators
        if item.get(
            "category"
        )
        == "primary"
    )

    support_strength = sum(
        _safe_float(
            item.get(
                "strength"
            )
        )
        for item in indicators
        if item.get(
            "category"
        )
        in (
            "secondary",
            "support",
        )
    )

    confidence = round(
        _clamp(
            (
                0.48
                + min(
                    primary_strength,
                    2.0,
                )
                * 0.15
                + min(
                    support_strength,
                    1.5,
                )
                * 0.08
            ),
            0.45,
            0.88,
        ),
        3,
    )

    return {
        "available": True,

        "event": (
            "spouse_profession"
        ),

        "model_version": (
            "v1"
        ),

        "confidence": (
            confidence
        ),

        "summary": (
            summary
        ),

        "strongest_themes": (
            strongest_themes
        ),

        "career_style": (
            style
        ),

        "ranked_themes": (
            ranked_themes
        ),

        "chart_context": {
            "seventh_house": {
                "sign": (
                    seventh_house.get(
                        "sign"
                    )
                ),
                "lord": (
                    seventh_lord
                ),
            },

            "seventh_lord": {
                "planet": (
                    seventh_lord
                ),
                "house": (
                    seventh_lord_house
                ),
                "sign": (
                    seventh_lord_sign
                ),
                "dignity": (
                    seventh_lord_dignity.get(
                        "dignity"
                    )
                ),
            },

            "spouse_profession_house": {
                "natal_house": (
                    profession_house_number
                ),
                "sign": (
                    profession_sign
                ),
                "lord": (
                    profession_lord
                ),
                "occupants": (
                    profession_occupants
                ),
            },

            "spouse_profession_lord": {
                "planet": (
                    profession_lord
                ),
                "house": (
                    profession_lord_house
                ),
                "sign": (
                    profession_lord_sign
                ),
                "dignity": (
                    profession_lord_dignity_name
                ),
                "dignity_strength": (
                    profession_lord_dignity_strength
                ),
            },
        },

        "indicators": (
            indicators
        ),
    }
