from __future__ import annotations

from typing import Any

from app.astrology.dignity import (
    evaluate_planetary_dignities,
)


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
# INDICATOR HELPER
# =========================================================

def _indicator(
    factor: str,
    category: str,
    strength: float,
    interpretation: str,
    **evidence: Any,
) -> dict[str, Any]:

    result = {
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

    if evidence:

        result[
            "evidence"
        ] = (
            evidence
        )

    return result


# =========================================================
# 5TH / 7TH CONNECTION
# =========================================================

def _analyze_fifth_seventh_connection(
    fifth_lord: str | None,
    seventh_lord: str | None,
    fifth_lord_data: dict[str, Any],
    seventh_lord_data: dict[str, Any],
) -> dict[str, Any]:

    if (
        not fifth_lord
        or not seventh_lord
    ):

        return {
            "connected": False,
            "strength": 0.0,
            "types": [],
        }

    fifth_house = (
        fifth_lord_data.get(
            "house"
        )
    )

    seventh_house = (
        seventh_lord_data.get(
            "house"
        )
    )

    connection_types = []

    strength = 0.0

    # -----------------------------------------------------
    # DIRECT CONNECTIONS
    # -----------------------------------------------------

    if fifth_house == 7:

        connection_types.append(
            "fifth_lord_in_seventh"
        )

        strength += 0.90

    if seventh_house == 5:

        connection_types.append(
            "seventh_lord_in_fifth"
        )

        strength += 0.90

    if (
        fifth_house == 7
        and seventh_house == 5
    ):

        connection_types.append(
            "fifth_seventh_exchange"
        )

        strength += 0.20

    # -----------------------------------------------------
    # SAME LORD
    # -----------------------------------------------------

    if fifth_lord == seventh_lord:

        connection_types.append(
            "same_fifth_and_seventh_lord"
        )

        strength += 0.65

    # -----------------------------------------------------
    # SAME HOUSE
    # -----------------------------------------------------
    #
    # This is meaningful, but weaker than direct placement
    # of the 5th lord in the 7th or vice versa.
    # -----------------------------------------------------

    if (
        fifth_lord != seventh_lord
        and fifth_house is not None
        and seventh_house is not None
        and fifth_house == seventh_house
    ):

        connection_types.append(
            "fifth_and_seventh_lords_same_house"
        )

        strength += 0.45

    return {
        "connected": bool(
            connection_types
        ),

        "strength": round(
            _clamp(
                strength
            ),
            3,
        ),

        "types": (
            connection_types
        ),
    }


# =========================================================
# MAIN ENGINE
# =========================================================

def analyze_love_vs_arranged_marriage_v2(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Estimate whether the natal relationship pattern leans
    toward:

        love / self-initiated marriage
        arranged / family-mediated marriage
        mixed / hybrid marriage pathway

    This is an evidence-ranking model rather than a
    deterministic prediction.
    """

    if not isinstance(
        chart,
        dict,
    ):

        raise ValueError(
            "chart must be a dictionary."
        )

    fifth = (
        _get_house(
            chart,
            5,
        )
    )

    seventh = (
        _get_house(
            chart,
            7,
        )
    )

    second = (
        _get_house(
            chart,
            2,
        )
    )

    ninth = (
        _get_house(
            chart,
            9,
        )
    )

    eleventh = (
        _get_house(
            chart,
            11,
        )
    )

    if not fifth:

        return {
            "available": False,
            "reason": (
                "5th house data is unavailable."
            ),
        }

    if not seventh:

        return {
            "available": False,
            "reason": (
                "7th house data is unavailable."
            ),
        }

    fifth_lord = (
        fifth.get(
            "lord"
        )
    )

    seventh_lord = (
        seventh.get(
            "lord"
        )
    )

    fifth_lord_data = (
        _get_planet(
            chart,
            fifth_lord,
        )
    )

    seventh_lord_data = (
        _get_planet(
            chart,
            seventh_lord,
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

    saturn = (
        _get_planet(
            chart,
            "Saturn",
        )
    )

    dignity_map = (
        _dignity_map(
            chart
        )
    )

    venus_dignity = _safe_dict(
        dignity_map.get(
            "Venus"
        )
    )

    fifth_occupants = (
        _planets_in_house(
            chart,
            5,
        )
    )

    seventh_occupants = (
        _planets_in_house(
            chart,
            7,
        )
    )

    second_occupants = (
        _planets_in_house(
            chart,
            2,
        )
    )

    ninth_occupants = (
        _planets_in_house(
            chart,
            9,
        )
    )

    eleventh_occupants = (
        _planets_in_house(
            chart,
            11,
        )
    )

    connection = (
        _analyze_fifth_seventh_connection(
            fifth_lord,
            seventh_lord,
            fifth_lord_data,
            seventh_lord_data,
        )
    )

    love_score = 0.0

    arranged_score = 0.0

    neutral_score = 0.75

    indicators = []

    # =====================================================
    # 1. 5TH-7TH CONNECTION
    # =====================================================

    connection_strength = (
        _safe_float(
            connection.get(
                "strength"
            )
        )
    )

    if connection_strength > 0:

        contribution = (
            connection_strength
            * 0.90
        )

        love_score += (
            contribution
        )

        indicators.append(
            _indicator(
                "fifth_seventh_connection",
                "love",
                connection_strength,
                (
                    "The 5th house of romance and the "
                    "7th house of marriage are structurally "
                    "connected, supporting the possibility "
                    "that personal attraction develops into "
                    "marriage."
                ),
                connection_types=(
                    connection.get(
                        "types"
                    )
                ),
            )
        )

    # =====================================================
    # 2. 5TH LORD
    # =====================================================

    fifth_lord_house = (
        fifth_lord_data.get(
            "house"
        )
    )

    if fifth_lord_house == 7:

        love_score += 0.80

        indicators.append(
            _indicator(
                "fifth_lord_in_seventh",
                "love",
                0.80,
                (
                    "The 5th lord occupies the 7th house, "
                    "directly connecting romance and marriage."
                ),
            )
        )

    elif fifth_lord_house == 11:

        love_score += 0.35

        indicators.append(
            _indicator(
                "fifth_lord_in_eleventh",
                "love",
                0.35,
                (
                    "The 5th lord in the 11th house can support "
                    "romantic developments through friendships "
                    "or social networks."
                ),
            )
        )

    elif fifth_lord_house == 2:

        arranged_score += 0.35

        indicators.append(
            _indicator(
                "fifth_lord_in_second",
                "arranged",
                0.35,
                (
                    "The 5th lord connects romance with the "
                    "family and lineage house."
                ),
            )
        )

    # =====================================================
    # 3. 7TH LORD
    # =====================================================

    seventh_lord_house = (
        seventh_lord_data.get(
            "house"
        )
    )

    if seventh_lord_house == 5:

        love_score += 0.80

        indicators.append(
            _indicator(
                "seventh_lord_in_fifth",
                "love",
                0.80,
                (
                    "The 7th lord occupies the 5th house, "
                    "strongly linking marriage with romance."
                ),
            )
        )

    elif seventh_lord_house == 11:

        love_score += 0.30

        indicators.append(
            _indicator(
                "seventh_lord_in_eleventh",
                "love",
                0.30,
                (
                    "The 7th lord in the 11th house can link "
                    "partnership with friends and social "
                    "networks."
                ),
            )
        )

    elif seventh_lord_house == 2:

        arranged_score += 0.65

        indicators.append(
            _indicator(
                "seventh_lord_in_second",
                "arranged",
                0.65,
                (
                    "The 7th lord in the 2nd house strongly "
                    "links marriage with family and lineage."
                ),
            )
        )

    elif seventh_lord_house == 9:

        arranged_score += 0.40

        indicators.append(
            _indicator(
                "seventh_lord_in_ninth",
                "arranged",
                0.40,
                (
                    "The 7th lord in the 9th house can increase "
                    "the role of tradition and established "
                    "family values in marriage."
                ),
            )
        )

    # =====================================================
    # 4. VENUS
    # =====================================================

    venus_house = (
        venus.get(
            "house"
        )
    )

    if venus_house == 5:

        love_score += 0.65

        indicators.append(
            _indicator(
                "venus_in_fifth",
                "love",
                0.65,
                (
                    "Venus in the 5th house supports romantic "
                    "attraction and self-initiated relationships."
                ),
            )
        )

    elif venus_house == 7:

        love_score += 0.35

        indicators.append(
            _indicator(
                "venus_in_seventh",
                "love",
                0.35,
                (
                    "Venus in the 7th house strengthens "
                    "personal attraction within partnership."
                ),
            )
        )

    elif venus_house == 11:

        love_score += 0.30

        indicators.append(
            _indicator(
                "venus_in_eleventh",
                "love",
                0.30,
                (
                    "Venus in the 11th can support relationships "
                    "developing through friends and networks."
                ),
            )
        )

    # Dignity makes Venus stronger generally, but does not
    # strongly distinguish love from arranged marriage.

    if (
        venus_dignity.get(
            "dignity"
        )
        in (
            "exalted",
            "own_sign",
        )
    ):

        love_score += 0.10

        neutral_score += 0.15

        indicators.append(
            _indicator(
                "strong_venus_dignity",
                "general",
                0.25,
                (
                    "Strong Venus dignity supports relationship "
                    "capacity and attraction, but by itself does "
                    "not determine whether marriage is love-based "
                    "or arranged."
                ),
                dignity=(
                    venus_dignity.get(
                        "dignity"
                    )
                ),
            )
        )

    # =====================================================
    # 5. RAHU
    # =====================================================

    rahu_house = (
        rahu.get(
            "house"
        )
    )

    if rahu_house == 5:

        love_score += 0.55

        indicators.append(
            _indicator(
                "rahu_in_fifth",
                "love",
                0.55,
                (
                    "Rahu in the 5th house can support "
                    "unconventional or strongly self-directed "
                    "romantic experiences."
                ),
            )
        )

    elif rahu_house == 7:

        love_score += 0.35

        indicators.append(
            _indicator(
                "rahu_in_seventh",
                "love",
                0.35,
                (
                    "Rahu in the 7th can introduce a "
                    "non-traditional element into partnership."
                ),
            )
        )

    elif rahu_house == 11:

        love_score += 0.20

        indicators.append(
            _indicator(
                "rahu_in_eleventh",
                "love",
                0.20,
                (
                    "Rahu in the 11th may support unconventional "
                    "connections through wider networks."
                ),
            )
        )

    # =====================================================
    # 6. FAMILY / TRADITION
    # =====================================================

    jupiter_house = (
        jupiter.get(
            "house"
        )
    )

    saturn_house = (
        saturn.get(
            "house"
        )
    )

    if jupiter_house in (
        2,
        7,
        9,
    ):

        arranged_score += 0.30

        indicators.append(
            _indicator(
                "jupiter_family_tradition",
                "arranged",
                0.30,
                (
                    "Jupiter connected with family, marriage "
                    "or tradition can support structured family "
                    "involvement."
                ),
                house=(
                    jupiter_house
                ),
            )
        )

    if saturn_house in (
        2,
        7,
        9,
    ):

        arranged_score += 0.25

        indicators.append(
            _indicator(
                "saturn_family_structure",
                "arranged",
                0.25,
                (
                    "Saturn connected with family, marriage "
                    "or traditional houses can emphasise duty "
                    "and established structures."
                ),
                house=(
                    saturn_house
                ),
            )
        )

    # =====================================================
    # 7. FAMILY HOUSE OCCUPANTS
    # =====================================================

    family_planets = {
        "Sun",
        "Moon",
        "Jupiter",
        "Saturn",
    }

    second_family_count = sum(
        1
        for planet in second_occupants
        if planet in family_planets
    )

    if second_family_count:

        contribution = min(
            second_family_count
            * 0.12,
            0.36,
        )

        arranged_score += (
            contribution
        )

        indicators.append(
            _indicator(
                "second_house_family_emphasis",
                "arranged",
                contribution,
                (
                    "The 2nd house has family-oriented "
                    "planetary emphasis."
                ),
                occupants=(
                    second_occupants
                ),
            )
        )

    ninth_family_count = sum(
        1
        for planet in ninth_occupants
        if planet in family_planets
    )

    if ninth_family_count:

        contribution = min(
            ninth_family_count
            * 0.10,
            0.30,
        )

        arranged_score += (
            contribution
        )

        indicators.append(
            _indicator(
                "ninth_house_tradition_emphasis",
                "arranged",
                contribution,
                (
                    "The 9th house carries additional emphasis "
                    "connected with tradition or established "
                    "values."
                ),
                occupants=(
                    ninth_occupants
                ),
            )
        )

    # =====================================================
    # 8. KETU IN 7TH
    # =====================================================

    ketu_house = (
        ketu.get(
            "house"
        )
    )

    if ketu_house == 7:

        neutral_score += 0.25

        indicators.append(
            _indicator(
                "ketu_in_seventh",
                "general",
                0.25,
                (
                    "Ketu in the 7th house can complicate or "
                    "individualise partnership expectations. "
                    "It is treated as contextual rather than "
                    "as direct evidence for either love or "
                    "arranged marriage."
                ),
            )
        )

    # =====================================================
    # RAW SCORES
    # =====================================================

    raw_love = round(
        love_score,
        3,
    )

    raw_arranged = round(
        arranged_score,
        3,
    )

    raw_neutral = round(
        neutral_score,
        3,
    )

    # =====================================================
    # BALANCED PROBABILITY MODEL
    # =====================================================
    #
    # Split the neutral evidence evenly across both sides.
    # This prevents:
    #
    #   evidence = love 1.0, arranged 0
    #
    # from becoming:
    #
    #   100% love / 0% arranged
    #
    # =====================================================

    balanced_love = (
        love_score
        + neutral_score * 0.5
    )

    balanced_arranged = (
        arranged_score
        + neutral_score * 0.5
    )

    total = (
        balanced_love
        + balanced_arranged
    )

    if total <= 0:

        love_probability = 0.5

        arranged_probability = 0.5

    else:

        love_probability = (
            balanced_love
            / total
        )

        arranged_probability = (
            balanced_arranged
            / total
        )

    love_probability = round(
        love_probability,
        3,
    )

    arranged_probability = round(
        arranged_probability,
        3,
    )

    margin = round(
        abs(
            love_probability
            - arranged_probability
        ),
        3,
    )

    # =====================================================
    # CLASSIFICATION
    # =====================================================

    if (
        love_probability >= 0.68
        and margin >= 0.25
    ):

        outcome = (
            "love_marriage_leaning"
        )

        label = (
            "Love Marriage Leaning"
        )

    elif (
        arranged_probability >= 0.68
        and margin >= 0.25
    ):

        outcome = (
            "arranged_marriage_leaning"
        )

        label = (
            "Arranged Marriage Leaning"
        )

    else:

        outcome = (
            "mixed_or_hybrid"
        )

        label = (
            "Mixed / Hybrid Pathway"
        )

    # Confidence depends both on separation and amount of
    # directional evidence.

    directional_evidence = (
        love_score
        + arranged_score
    )

    evidence_strength = min(
        directional_evidence
        / 2.5,
        1.0,
    )

    confidence = (
        0.52
        + margin * 0.40
        + evidence_strength * 0.20
    )

    confidence = round(
        min(
            confidence,
            0.88,
        ),
        3,
    )

    # =====================================================
    # INDICATOR RANKING
    # =====================================================

    love_indicators = [
        item
        for item in indicators
        if item.get(
            "category"
        )
        == "love"
    ]

    arranged_indicators = [
        item
        for item in indicators
        if item.get(
            "category"
        )
        == "arranged"
    ]

    general_indicators = [
        item
        for item in indicators
        if item.get(
            "category"
        )
        == "general"
    ]

    for collection in (
        love_indicators,
        arranged_indicators,
        general_indicators,
    ):

        collection.sort(
            key=lambda item: (
                _safe_float(
                    item.get(
                        "strength"
                    )
                )
            ),
            reverse=True,
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    if outcome == (
        "love_marriage_leaning"
    ):

        summary = (
            "The natal evidence leans toward a relationship "
            "developing through personal choice or romantic "
            "involvement before marriage. This is a tendency "
            "rather than an exclusive prediction, and family "
            "participation may still be important."
        )

    elif outcome == (
        "arranged_marriage_leaning"
    ):

        summary = (
            "The natal evidence leans toward greater family "
            "or traditional involvement in the marriage "
            "pathway. Personal choice and attraction can "
            "still remain significant."
        )

    else:

        summary = (
            "The natal evidence does not strongly support a "
            "strict love-versus-arranged distinction. A hybrid "
            "pathway involving both personal choice and family "
            "participation may fit the chart more closely."
        )

    return {
        "available": True,

        "event": (
            "love_vs_arranged"
        ),

        "model_version": (
            "v2"
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

        "summary": (
            summary
        ),

        "scores": {
            "love_raw": (
                raw_love
            ),

            "arranged_raw": (
                raw_arranged
            ),

            "neutral_raw": (
                raw_neutral
            ),

            "balanced_love": round(
                balanced_love,
                3,
            ),

            "balanced_arranged": round(
                balanced_arranged,
                3,
            ),

            "love_probability": (
                love_probability
            ),

            "arranged_probability": (
                arranged_probability
            ),

            "margin": (
                margin
            ),
        },

        "chart_context": {
            "fifth_house": {
                "sign": (
                    fifth.get(
                        "sign"
                    )
                ),

                "lord": (
                    fifth_lord
                ),

                "occupants": (
                    fifth_occupants
                ),
            },

            "seventh_house": {
                "sign": (
                    seventh.get(
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

            "second_house": {
                "sign": (
                    second.get(
                        "sign"
                    )
                ),

                "lord": (
                    second.get(
                        "lord"
                    )
                ),

                "occupants": (
                    second_occupants
                ),
            },

            "ninth_house": {
                "sign": (
                    ninth.get(
                        "sign"
                    )
                ),

                "lord": (
                    ninth.get(
                        "lord"
                    )
                ),

                "occupants": (
                    ninth_occupants
                ),
            },

            "eleventh_house": {
                "sign": (
                    eleventh.get(
                        "sign"
                    )
                ),

                "lord": (
                    eleventh.get(
                        "lord"
                    )
                ),

                "occupants": (
                    eleventh_occupants
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

                "dignity": (
                    venus_dignity.get(
                        "dignity"
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

            "fifth_seventh_connection": (
                connection
            ),
        },

        "love_indicators": (
            love_indicators
        ),

        "arranged_indicators": (
            arranged_indicators
        ),

        "general_indicators": (
            general_indicators
        ),

        "all_indicators": (
            indicators
        ),
    }
