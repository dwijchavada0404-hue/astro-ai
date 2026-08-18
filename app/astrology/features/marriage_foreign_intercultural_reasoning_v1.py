from __future__ import annotations

from typing import Any

from app.astrology.dignity import (
    evaluate_planetary_dignities,
)


# =========================================================
# CONSTANTS
# =========================================================

FOREIGN_HOUSES = {
    9,
    12,
}

RELATIONSHIP_HOUSES = {
    5,
    7,
}

FOREIGN_SIGNS = {
    "Sagittarius",
    "Pisces",
    "Aquarius",
}

MOVABLE_SIGNS = {
    "Aries",
    "Cancer",
    "Libra",
    "Capricorn",
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


def _safe_list(
    value: Any,
) -> list[Any]:

    if isinstance(
        value,
        list,
    ):
        return value

    return []


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


def _get_house(
    chart: dict[str, Any],
    house_number: int,
) -> dict[str, Any]:

    return _safe_dict(
        _safe_dict(
            chart.get(
                "houses"
            )
        ).get(
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

    return _safe_dict(
        _safe_dict(
            chart.get(
                "planets"
            )
        ).get(
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

        if data.get(
            "house"
        ) == house_number:

            result.append(
                str(
                    planet_name
                )
            )

    return result


def _dignity_map(
    chart: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    return {
        str(
            item.get(
                "planet"
            )
        ): item
        for item in evaluate_planetary_dignities(
            chart
        )
        if isinstance(
            item,
            dict,
        )
        and item.get(
            "planet"
        )
    }


# =========================================================
# EVIDENCE HELPERS
# =========================================================

def _add_indicator(
    indicators: list[dict[str, Any]],
    factor: str,
    category: str,
    strength: float,
    interpretation: str,
    details: dict[str, Any] | None = None,
) -> None:

    item = {
        "factor": (
            factor
        ),
        "category": (
            category
        ),
        "strength": round(
            _clamp(
                strength
            ),
            3,
        ),
        "interpretation": (
            interpretation
        ),
    }

    if details:

        item[
            "details"
        ] = (
            details
        )

    indicators.append(
        item
    )


def _indicator_score(
    indicators: list[dict[str, Any]],
) -> float:

    if not indicators:

        return 0.0

    total = sum(
        _safe_float(
            item.get(
                "strength"
            )
        )
        for item in indicators
    )

    return round(
        total,
        3,
    )


# =========================================================
# CONNECTION CHECKS
# =========================================================

def _same_house_connection(
    first_data: dict[str, Any],
    second_data: dict[str, Any],
) -> bool:

    first_house = (
        first_data.get(
            "house"
        )
    )

    second_house = (
        second_data.get(
            "house"
        )
    )

    return (
        first_house is not None
        and second_house is not None
        and first_house
        == second_house
    )


def _house_lord_connection(
    chart: dict[str, Any],
    relationship_lord: str | None,
    foreign_house_number: int,
) -> bool:

    if not relationship_lord:

        return False

    relationship_lord_data = (
        _get_planet(
            chart,
            relationship_lord,
        )
    )

    return (
        relationship_lord_data.get(
            "house"
        )
        == foreign_house_number
    )


# =========================================================
# CLASSIFICATION
# =========================================================

def _classify_support(
    support_score: float,
) -> tuple[
    str,
    str,
]:

    if support_score >= 0.78:

        return (
            "strongly_supported",
            "Strong Foreign / Intercultural Potential",
        )

    if support_score >= 0.60:

        return (
            "supported",
            "Foreign / Intercultural Potential",
        )

    if support_score >= 0.40:

        return (
            "mixed",
            "Mixed Foreign / Local Pattern",
        )

    return (
        "weakly_supported",
        "Primarily Local / Conventional Pattern",
    )


# =========================================================
# SUMMARY
# =========================================================

def _build_summary(
    outcome: str,
    strongest_factors: list[str],
) -> str:

    if outcome == (
        "strongly_supported"
    ):

        base = (
            "The natal relationship pattern shows strong "
            "support for a spouse or significant relationship "
            "connected with a different region, culture, "
            "nationality or international environment."
        )

    elif outcome == (
        "supported"
    ):

        base = (
            "The natal relationship pattern contains meaningful "
            "foreign or intercultural indicators. A spouse from "
            "a different region, culture or international "
            "environment is reasonably supported."
        )

    elif outcome == (
        "mixed"
    ):

        base = (
            "The natal chart shows some foreign or intercultural "
            "relationship indicators, but they are not dominant. "
            "Both local and cross-cultural relationship pathways "
            "remain plausible."
        )

    else:

        base = (
            "The currently modelled natal indicators do not "
            "strongly emphasise a foreign or intercultural spouse "
            "connection. This does not rule it out, but other "
            "relationship patterns are more prominent."
        )

    if strongest_factors:

        factor_text = ", ".join(
            strongest_factors[
                :3
            ]
        )

        base += (
            " The strongest supporting themes are "
            f"{factor_text}."
        )

    return base


# =========================================================
# MAIN ENGINE
# =========================================================

def analyze_foreign_intercultural_relationship_v1(
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
            "event": (
                "foreign_intercultural_connection"
            ),
            "model_version": (
                "v1"
            ),
            "reason": (
                "7th house data is unavailable."
            ),
        }

    fifth_house = (
        _get_house(
            chart,
            5,
        )
    )

    ninth_house = (
        _get_house(
            chart,
            9,
        )
    )

    twelfth_house = (
        _get_house(
            chart,
            12,
        )
    )

    planets = _safe_dict(
        chart.get(
            "planets"
        )
    )

    dignity_map = (
        _dignity_map(
            chart
        )
    )

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

    fifth_lord = (
        fifth_house.get(
            "lord"
        )
        if fifth_house
        else None
    )

    fifth_lord_data = (
        _get_planet(
            chart,
            fifth_lord,
        )
    )

    ninth_lord = (
        ninth_house.get(
            "lord"
        )
        if ninth_house
        else None
    )

    ninth_lord_data = (
        _get_planet(
            chart,
            ninth_lord,
        )
    )

    twelfth_lord = (
        twelfth_house.get(
            "lord"
        )
        if twelfth_house
        else None
    )

    twelfth_lord_data = (
        _get_planet(
            chart,
            twelfth_lord,
        )
    )

    rahu = (
        _get_planet(
            chart,
            "Rahu",
        )
    )

    ketu = (
        _get_planet(
            chart,
            "Ketu",
        )
    )

    venus = (
        _get_planet(
            chart,
            "Venus",
        )
    )

    jupiter = (
        _get_planet(
            chart,
            "Jupiter",
        )
    )

    seventh_occupants = (
        _planets_in_house(
            chart,
            7,
        )
    )

    ninth_occupants = (
        _planets_in_house(
            chart,
            9,
        )
    )

    twelfth_occupants = (
        _planets_in_house(
            chart,
            12,
        )
    )

    indicators: list[
        dict[str, Any]
    ] = []

    # =====================================================
    # PRIMARY: 7TH LORD IN FOREIGN HOUSES
    # =====================================================

    if seventh_lord_data.get(
        "house"
    ) in FOREIGN_HOUSES:

        house_number = int(
            seventh_lord_data[
                "house"
            ]
        )

        _add_indicator(
            indicators,
            (
                "seventh_lord_in_foreign_house"
            ),
            (
                "primary"
            ),
            0.90,
            (
                f"The 7th lord {seventh_lord} is placed in "
                f"the {house_number}th house, directly linking "
                "partnership matters with long-distance, foreign "
                "or cross-cultural environments."
            ),
            {
                "planet": (
                    seventh_lord
                ),
                "house": (
                    house_number
                ),
                "sign": (
                    seventh_lord_data.get(
                        "sign"
                    )
                ),
            },
        )

    # =====================================================
    # PRIMARY: RAHU AND 7TH HOUSE
    # =====================================================

    if rahu.get(
        "house"
    ) == 7:

        _add_indicator(
            indicators,
            (
                "rahu_in_seventh"
            ),
            (
                "primary"
            ),
            0.85,
            (
                "Rahu occupies the 7th house, supporting "
                "unconventional, cross-cultural, non-local or "
                "socially atypical partnership themes."
            ),
            {
                "house": 7,
                "sign": (
                    rahu.get(
                        "sign"
                    )
                ),
            },
        )

    # =====================================================
    # PRIMARY: 7TH LORD WITH RAHU
    # =====================================================

    if _same_house_connection(
        seventh_lord_data,
        rahu,
    ):

        _add_indicator(
            indicators,
            (
                "seventh_lord_rahu_connection"
            ),
            (
                "primary"
            ),
            0.85,
            (
                "The 7th lord is connected with Rahu by house "
                "placement, strengthening unconventional, foreign "
                "or intercultural relationship possibilities."
            ),
            {
                "seventh_lord": (
                    seventh_lord
                ),
                "house": (
                    seventh_lord_data.get(
                        "house"
                    )
                ),
            },
        )

    # =====================================================
    # PRIMARY: 7TH LORD / 9TH LORD CONNECTION
    # =====================================================

    if (
        seventh_lord
        and ninth_lord
        and (
            _same_house_connection(
                seventh_lord_data,
                ninth_lord_data,
            )
            or _house_lord_connection(
                chart,
                seventh_lord,
                9,
            )
        )
    ):

        _add_indicator(
            indicators,
            (
                "seventh_ninth_connection"
            ),
            (
                "primary"
            ),
            0.78,
            (
                "The marriage axis is linked with the 9th-house "
                "axis of long-distance travel, different cultures "
                "and broader world exposure."
            ),
            {
                "seventh_lord": (
                    seventh_lord
                ),
                "ninth_lord": (
                    ninth_lord
                ),
            },
        )

    # =====================================================
    # PRIMARY: 7TH LORD / 12TH LORD CONNECTION
    # =====================================================

    if (
        seventh_lord
        and twelfth_lord
        and (
            _same_house_connection(
                seventh_lord_data,
                twelfth_lord_data,
            )
            or _house_lord_connection(
                chart,
                seventh_lord,
                12,
            )
        )
    ):

        _add_indicator(
            indicators,
            (
                "seventh_twelfth_connection"
            ),
            (
                "primary"
            ),
            0.82,
            (
                "The marriage axis is linked with the 12th-house "
                "axis of foreign residence, distance and life away "
                "from the familiar environment."
            ),
            {
                "seventh_lord": (
                    seventh_lord
                ),
                "twelfth_lord": (
                    twelfth_lord
                ),
            },
        )

    # =====================================================
    # SECONDARY: 5TH LORD FOREIGN CONNECTION
    # =====================================================

    if fifth_lord_data.get(
        "house"
    ) in FOREIGN_HOUSES:

        _add_indicator(
            indicators,
            (
                "fifth_lord_in_foreign_house"
            ),
            (
                "secondary"
            ),
            0.62,
            (
                "The 5th lord of romance is placed in a foreign "
                "or long-distance house, supporting romantic "
                "connections across geography or culture."
            ),
            {
                "planet": (
                    fifth_lord
                ),
                "house": (
                    fifth_lord_data.get(
                        "house"
                    )
                ),
            },
        )

    # =====================================================
    # SECONDARY: VENUS FOREIGN CONNECTION
    # =====================================================

    if venus.get(
        "house"
    ) in FOREIGN_HOUSES:

        _add_indicator(
            indicators,
            (
                "venus_in_foreign_house"
            ),
            (
                "secondary"
            ),
            0.58,
            (
                "Venus is placed in a foreign or long-distance "
                "house, adding support for attraction or partnership "
                "themes involving travel, distance or different "
                "cultural environments."
            ),
            {
                "house": (
                    venus.get(
                        "house"
                    )
                ),
                "sign": (
                    venus.get(
                        "sign"
                    )
                ),
            },
        )

    # =====================================================
    # SECONDARY: JUPITER FOREIGN CONNECTION
    # =====================================================

    if jupiter.get(
        "house"
    ) in FOREIGN_HOUSES:

        _add_indicator(
            indicators,
            (
                "jupiter_in_foreign_house"
            ),
            (
                "secondary"
            ),
            0.50,
            (
                "Jupiter occupies a foreign or long-distance house, "
                "adding broader cultural, educational or international "
                "exposure to the relationship environment."
            ),
            {
                "house": (
                    jupiter.get(
                        "house"
                    )
                ),
                "sign": (
                    jupiter.get(
                        "sign"
                    )
                ),
            },
        )

    # =====================================================
    # SECONDARY: RAHU IN FOREIGN HOUSES
    # =====================================================

    if rahu.get(
        "house"
    ) in FOREIGN_HOUSES:

        _add_indicator(
            indicators,
            (
                "rahu_in_foreign_house"
            ),
            (
                "secondary"
            ),
            0.60,
            (
                "Rahu occupies a foreign or long-distance house, "
                "strengthening non-local, international or culturally "
                "different life experiences."
            ),
            {
                "house": (
                    rahu.get(
                        "house"
                    )
                ),
                "sign": (
                    rahu.get(
                        "sign"
                    )
                ),
            },
        )

    # =====================================================
    # CONTEXT: 7TH SIGN
    # =====================================================

    seventh_sign = str(
        seventh_house.get(
            "sign",
            "",
        )
        or ""
    )

    if seventh_sign in FOREIGN_SIGNS:

        _add_indicator(
            indicators,
            (
                "seventh_house_foreign_sign"
            ),
            (
                "context"
            ),
            0.30,
            (
                f"The 7th house falls in {seventh_sign}, which "
                "adds a secondary theme of broader worldview, "
                "distance or unconventional social exposure."
            ),
            {
                "sign": (
                    seventh_sign
                ),
            },
        )

    elif seventh_sign in MOVABLE_SIGNS:

        _add_indicator(
            indicators,
            (
                "seventh_house_movable_sign"
            ),
            (
                "context"
            ),
            0.20,
            (
                f"The 7th house falls in the movable sign "
                f"{seventh_sign}, adding some flexibility, movement "
                "or relocation potential to partnership matters."
            ),
            {
                "sign": (
                    seventh_sign
                ),
            },
        )

    # =====================================================
    # CONTEXT: KETU IN 7TH
    # =====================================================

    if ketu.get(
        "house"
    ) == 7:

        _add_indicator(
            indicators,
            (
                "ketu_in_seventh"
            ),
            (
                "context"
            ),
            0.22,
            (
                "Ketu in the 7th can make partnership expectations "
                "less conventional or more individualised. It is "
                "treated as contextual rather than direct proof of "
                "a foreign spouse."
            ),
            {
                "sign": (
                    ketu.get(
                        "sign"
                    )
                ),
            },
        )

    # =====================================================
    # DIGNITY CONTEXT
    # =====================================================

    seventh_lord_dignity = (
        _safe_dict(
            dignity_map.get(
                str(
                    seventh_lord
                )
            )
        )
    )

    seventh_dignity_name = (
        seventh_lord_dignity.get(
            "dignity"
        )
    )

    # =====================================================
    # SCORING
    # =====================================================

    primary_indicators = [
        item
        for item in indicators
        if item.get(
            "category"
        ) == "primary"
    ]

    secondary_indicators = [
        item
        for item in indicators
        if item.get(
            "category"
        ) == "secondary"
    ]

    context_indicators = [
        item
        for item in indicators
        if item.get(
            "category"
        ) == "context"
    ]

    primary_raw = (
        _indicator_score(
            primary_indicators
        )
    )

    secondary_raw = (
        _indicator_score(
            secondary_indicators
        )
    )

    context_raw = (
        _indicator_score(
            context_indicators
        )
    )

    primary_normalised = min(
        primary_raw / 1.70,
        1.0,
    )

    secondary_normalised = min(
        secondary_raw / 1.40,
        1.0,
    )

    context_normalised = min(
        context_raw / 0.70,
        1.0,
    )

    support_score = (
        primary_normalised * 0.68
        + secondary_normalised * 0.24
        + context_normalised * 0.08
    )

    # Require some relationship-specific evidence before
    # allowing purely general foreign indicators to score highly.
    relationship_specific = any(
        item.get(
            "factor"
        )
        in (
            "seventh_lord_in_foreign_house",
            "rahu_in_seventh",
            "seventh_lord_rahu_connection",
            "seventh_ninth_connection",
            "seventh_twelfth_connection",
            "fifth_lord_in_foreign_house",
        )
        for item in indicators
    )

    if (
        not relationship_specific
        and support_score > 0.52
    ):

        support_score = (
            0.52
        )

    support_score = round(
        _clamp(
            support_score
        ),
        3,
    )

    (
        outcome,
        label,
    ) = (
        _classify_support(
            support_score
        )
    )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    evidence_count = len(
        indicators
    )

    primary_count = len(
        primary_indicators
    )

    confidence = (
        0.54
        + min(
            primary_count,
            3,
        )
        * 0.08
        + min(
            evidence_count,
            6,
        )
        * 0.025
    )

    if seventh_dignity_name in (
        "exalted",
        "own_sign",
    ):

        confidence += (
            0.04
        )

    confidence = round(
        _clamp(
            confidence,
            0.50,
            0.88,
        ),
        3,
    )

    # =====================================================
    # STRONGEST FACTORS
    # =====================================================

    ranked_indicators = sorted(
        indicators,
        key=lambda item: (
            _safe_float(
                item.get(
                    "strength"
                )
            )
        ),
        reverse=True,
    )

    strongest_factors = [
        str(
            item.get(
                "interpretation",
                "",
            )
        )
        for item in ranked_indicators[
            :3
        ]
        if item.get(
            "interpretation"
        )
    ]

    summary = (
        _build_summary(
            outcome,
            strongest_factors,
        )
    )

    return {
        "available": True,

        "event": (
            "foreign_intercultural_connection"
        ),

        "model_version": (
            "v1"
        ),

        "outcome": (
            outcome
        ),

        "label": (
            label
        ),

        "confidence": (
            confidence
        ),

        "support_score": (
            support_score
        ),

        "probability_level": (
            outcome
        ),

        "summary": (
            summary
        ),

        "scores": {
            "primary_raw": (
                primary_raw
            ),
            "secondary_raw": (
                secondary_raw
            ),
            "context_raw": (
                context_raw
            ),
            "primary_normalised": round(
                primary_normalised,
                3,
            ),
            "secondary_normalised": round(
                secondary_normalised,
                3,
            ),
            "context_normalised": round(
                context_normalised,
                3,
            ),
            "support_score": (
                support_score
            ),
        },

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
                "occupants": (
                    seventh_occupants
                ),
            },

            "seventh_lord": {
                "planet": (
                    seventh_lord
                ),
                "house": (
                    seventh_lord_data.get(
                        "house"
                    )
                ),
                "sign": (
                    seventh_lord_data.get(
                        "sign"
                    )
                ),
                "dignity": (
                    seventh_dignity_name
                ),
            },

            "fifth_house": {
                "sign": (
                    fifth_house.get(
                        "sign"
                    )
                    if fifth_house
                    else None
                ),
                "lord": (
                    fifth_lord
                ),
            },

            "fifth_lord": {
                "planet": (
                    fifth_lord
                ),
                "house": (
                    fifth_lord_data.get(
                        "house"
                    )
                ),
                "sign": (
                    fifth_lord_data.get(
                        "sign"
                    )
                ),
            },

            "ninth_house": {
                "sign": (
                    ninth_house.get(
                        "sign"
                    )
                    if ninth_house
                    else None
                ),
                "lord": (
                    ninth_lord
                ),
                "occupants": (
                    ninth_occupants
                ),
            },

            "ninth_lord": {
                "planet": (
                    ninth_lord
                ),
                "house": (
                    ninth_lord_data.get(
                        "house"
                    )
                ),
                "sign": (
                    ninth_lord_data.get(
                        "sign"
                    )
                ),
            },

            "twelfth_house": {
                "sign": (
                    twelfth_house.get(
                        "sign"
                    )
                    if twelfth_house
                    else None
                ),
                "lord": (
                    twelfth_lord
                ),
                "occupants": (
                    twelfth_occupants
                ),
            },

            "twelfth_lord": {
                "planet": (
                    twelfth_lord
                ),
                "house": (
                    twelfth_lord_data.get(
                        "house"
                    )
                ),
                "sign": (
                    twelfth_lord_data.get(
                        "sign"
                    )
                ),
            },

            "rahu": {
                "house": (
                    rahu.get(
                        "house"
                    )
                ),
                "sign": (
                    rahu.get(
                        "sign"
                    )
                ),
            },

            "ketu": {
                "house": (
                    ketu.get(
                        "house"
                    )
                ),
                "sign": (
                    ketu.get(
                        "sign"
                    )
                ),
            },

            "venus": {
                "house": (
                    venus.get(
                        "house"
                    )
                ),
                "sign": (
                    venus.get(
                        "sign"
                    )
                ),
            },

            "jupiter": {
                "house": (
                    jupiter.get(
                        "house"
                    )
                ),
                "sign": (
                    jupiter.get(
                        "sign"
                    )
                ),
            },
        },

        "primary_indicators": (
            primary_indicators
        ),

        "secondary_indicators": (
            secondary_indicators
        ),

        "context_indicators": (
            context_indicators
        ),

        "indicators": (
            indicators
        ),
    }
