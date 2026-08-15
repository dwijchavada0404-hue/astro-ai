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
        planet_data_raw,
    ) in planets.items():

        planet_data = _safe_dict(
            planet_data_raw
        )

        if (
            planet_data.get(
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
# CONNECTION HELPERS
# =========================================================

def _lords_are_connected(
    fifth_lord: str | None,
    seventh_lord: str | None,
    fifth_lord_data: dict[str, Any],
    seventh_lord_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Detect simple structural 5th-7th relationships using
    house placement.

    This version intentionally uses only relationships that
    can be established reliably from the current chart
    structure.

    Later versions can add planetary aspects, conjunction
    orb logic and Navamsha confirmation.
    """

    if (
        not fifth_lord
        or not seventh_lord
    ):
        return {
            "connected": False,
            "strength": 0.0,
            "types": [],
        }

    fifth_lord_house = (
        fifth_lord_data.get(
            "house"
        )
    )

    seventh_lord_house = (
        seventh_lord_data.get(
            "house"
        )
    )

    connection_types = []

    strength = 0.0

    # 5th lord in 7th house.
    if fifth_lord_house == 7:

        connection_types.append(
            "fifth_lord_in_seventh"
        )

        strength += 1.0

    # 7th lord in 5th house.
    if seventh_lord_house == 5:

        connection_types.append(
            "seventh_lord_in_fifth"
        )

        strength += 1.0

    # Mutual exchange: 5th lord occupies 7th house and
    # 7th lord occupies 5th house.
    if (
        fifth_lord_house == 7
        and seventh_lord_house == 5
    ):

        connection_types.append(
            "fifth_seventh_mutual_exchange"
        )

        strength += 0.5

    # Same planet owns both houses.
    if fifth_lord == seventh_lord:

        connection_types.append(
            "same_fifth_and_seventh_lord"
        )

        strength += 0.8

    # Both lords occupying the same house is a conjunction-
    # style structural connection in whole-sign house logic.
    if (
        fifth_lord_house is not None
        and seventh_lord_house is not None
        and fifth_lord_house
        == seventh_lord_house
        and fifth_lord
        != seventh_lord
    ):

        connection_types.append(
            "fifth_and_seventh_lords_same_house"
        )

        strength += 0.65

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
# INDICATOR HELPERS
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
        ] = evidence

    return result


# =========================================================
# MAIN REASONING ENGINE
# =========================================================

def analyze_love_vs_arranged_marriage(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate natal-chart evidence associated with:

        love / self-initiated marriage
        arranged / family-mediated marriage
        mixed / hybrid pathway

    This is a transparent evidence engine rather than a
    deterministic prediction.

    The first version uses only chart structures already
    available in AstroAI:

        5th house and 5th lord
        7th house and 7th lord
        2nd and 11th family/social houses
        Venus
        Jupiter
        Rahu
        planetary dignity
        direct 5th-7th house/lord relationships
    """

    if not isinstance(
        chart,
        dict,
    ):
        raise ValueError(
            "chart must be a dictionary."
        )

    fifth_house = (
        _get_house(
            chart,
            5,
        )
    )

    seventh_house = (
        _get_house(
            chart,
            7,
        )
    )

    second_house = (
        _get_house(
            chart,
            2,
        )
    )

    eleventh_house = (
        _get_house(
            chart,
            11,
        )
    )

    if not fifth_house:

        return {
            "available": False,
            "reason": (
                "5th house data is unavailable."
            ),
        }

    if not seventh_house:

        return {
            "available": False,
            "reason": (
                "7th house data is unavailable."
            ),
        }

    fifth_lord = (
        fifth_house.get(
            "lord"
        )
    )

    seventh_lord = (
        seventh_house.get(
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

    eleventh_occupants = (
        _planets_in_house(
            chart,
            11,
        )
    )

    connection = (
        _lords_are_connected(
            fifth_lord,
            seventh_lord,
            fifth_lord_data,
            seventh_lord_data,
        )
    )

    love_score = 0.0

    arranged_score = 0.0

    indicators = []

    # =====================================================
    # 1. DIRECT 5TH-7TH CONNECTION
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
            1.25
            * connection_strength
        )

        love_score += (
            contribution
        )

        indicators.append(
            _indicator(
                "fifth_seventh_connection",
                "love",
                min(
                    contribution
                    / 1.25,
                    1.0,
                ),
                (
                    "A direct structural connection between "
                    "the 5th house of romance and the 7th "
                    "house of partnership supports a pathway "
                    "in which personal attraction may develop "
                    "into marriage."
                ),
                connection_types=(
                    connection.get(
                        "types"
                    )
                ),
            )
        )

    # =====================================================
    # 2. 5TH LORD PLACEMENT
    # =====================================================

    fifth_lord_house = (
        fifth_lord_data.get(
            "house"
        )
    )

    if fifth_lord_house == 7:

        love_score += 1.0

        indicators.append(
            _indicator(
                "fifth_lord_in_seventh",
                "love",
                1.0,
                (
                    "The 5th lord is placed in the 7th house, "
                    "directly linking romance with committed "
                    "partnership."
                ),
                fifth_lord=(
                    fifth_lord
                ),
            )
        )

    elif fifth_lord_house == 11:

        love_score += 0.55

        indicators.append(
            _indicator(
                "fifth_lord_in_eleventh",
                "love",
                0.55,
                (
                    "The 5th lord in the 11th house can connect "
                    "romance with friendships, social networks "
                    "and fulfilment of personal relationship "
                    "desires."
                ),
                fifth_lord=(
                    fifth_lord
                ),
            )
        )

    elif fifth_lord_house == 2:

        arranged_score += 0.50

        indicators.append(
            _indicator(
                "fifth_lord_in_second",
                "arranged",
                0.50,
                (
                    "The 5th lord in the 2nd house can bring "
                    "romantic matters into the sphere of family "
                    "and lineage."
                ),
                fifth_lord=(
                    fifth_lord
                ),
            )
        )

    # =====================================================
    # 3. 7TH LORD PLACEMENT
    # =====================================================

    seventh_lord_house = (
        seventh_lord_data.get(
            "house"
        )
    )

    if seventh_lord_house == 5:

        love_score += 1.0

        indicators.append(
            _indicator(
                "seventh_lord_in_fifth",
                "love",
                1.0,
                (
                    "The 7th lord is placed in the 5th house, "
                    "strongly connecting marriage with romance, "
                    "personal affection and self-chosen "
                    "relationship development."
                ),
                seventh_lord=(
                    seventh_lord
                ),
            )
        )

    elif seventh_lord_house == 11:

        love_score += 0.45

        indicators.append(
            _indicator(
                "seventh_lord_in_eleventh",
                "love",
                0.45,
                (
                    "The 7th lord in the 11th house may connect "
                    "partnership with friendships, networks and "
                    "social-circle introductions."
                ),
                seventh_lord=(
                    seventh_lord
                ),
            )
        )

    elif seventh_lord_house == 2:

        arranged_score += 0.80

        indicators.append(
            _indicator(
                "seventh_lord_in_second",
                "arranged",
                0.80,
                (
                    "The 7th lord in the 2nd house strongly "
                    "connects marriage with family, lineage "
                    "and household considerations."
                ),
                seventh_lord=(
                    seventh_lord
                ),
            )
        )

    elif seventh_lord_house == 9:

        arranged_score += 0.45

        indicators.append(
            _indicator(
                "seventh_lord_in_ninth",
                "arranged",
                0.45,
                (
                    "The 7th lord in the 9th house can connect "
                    "marriage with tradition, family values "
                    "and established cultural frameworks."
                ),
                seventh_lord=(
                    seventh_lord
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

    venus_dignity = _safe_dict(
        dignity_map.get(
            "Venus"
        )
    )

    if venus_house == 5:

        love_score += 0.90

        indicators.append(
            _indicator(
                "venus_in_fifth",
                "love",
                0.90,
                (
                    "Venus in the 5th house strongly supports "
                    "romantic attraction, affection and "
                    "self-initiated relationship development."
                ),
            )
        )

    elif venus_house == 7:

        love_score += 0.70

        arranged_score += 0.20

        indicators.append(
            _indicator(
                "venus_in_seventh",
                "love",
                0.70,
                (
                    "Venus in the 7th house strengthens "
                    "attraction and partnership themes and may "
                    "support a personally meaningful union."
                ),
            )
        )

    elif venus_house == 11:

        love_score += 0.60

        indicators.append(
            _indicator(
                "venus_in_eleventh",
                "love",
                0.60,
                (
                    "Venus in the 11th house can support "
                    "relationships emerging through friendship, "
                    "social circles and networks."
                ),
            )
        )

    if (
        venus_dignity.get(
            "dignity"
        )
        in (
            "exalted",
            "own_sign",
        )
    ):

        love_score += 0.30

        indicators.append(
            _indicator(
                "strong_venus_dignity",
                "love",
                0.30,
                (
                    "Strong Venus dignity supports attraction, "
                    "affection and personal relationship choice."
                ),
                dignity=(
                    venus_dignity.get(
                        "dignity"
                    )
                ),
            )
        )

    # =====================================================
    # 5. RAHU / UNCONVENTIONAL RELATIONSHIP SIGNALS
    # =====================================================

    rahu_house = (
        rahu.get(
            "house"
        )
    )

    if rahu_house == 5:

        love_score += 0.75

        indicators.append(
            _indicator(
                "rahu_in_fifth",
                "love",
                0.75,
                (
                    "Rahu in the 5th house can increase "
                    "unconventional attraction, intense romance "
                    "or relationships that depart from expected "
                    "social patterns."
                ),
            )
        )

    elif rahu_house == 7:

        love_score += 0.55

        indicators.append(
            _indicator(
                "rahu_in_seventh",
                "love",
                0.55,
                (
                    "Rahu in the 7th house can indicate an "
                    "unconventional or non-traditional element "
                    "in partnership choice."
                ),
            )
        )

    elif rahu_house == 11:

        love_score += 0.35

        indicators.append(
            _indicator(
                "rahu_in_eleventh",
                "love",
                0.35,
                (
                    "Rahu in the 11th house may support unusual "
                    "connections through wider social networks."
                ),
            )
        )

    # =====================================================
    # 6. ROMANTIC HOUSE OCCUPANTS
    # =====================================================

    if "Venus" in fifth_occupants:

        love_score += 0.45

    if "Moon" in fifth_occupants:

        love_score += 0.25

        indicators.append(
            _indicator(
                "moon_in_fifth",
                "love",
                0.25,
                (
                    "Moon in the 5th house can increase emotional "
                    "investment in romance and personal attachment."
                ),
            )
        )

    if "Mercury" in fifth_occupants:

        love_score += 0.20

        indicators.append(
            _indicator(
                "mercury_in_fifth",
                "love",
                0.20,
                (
                    "Mercury in the 5th house may support romantic "
                    "development through communication and "
                    "friendship."
                ),
            )
        )

    # =====================================================
    # 7. FAMILY / TRADITIONAL SUPPORT
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

        arranged_score += 0.45

        indicators.append(
            _indicator(
                "jupiter_family_marriage_support",
                "arranged",
                0.45,
                (
                    "Jupiter influencing a family, partnership "
                    "or traditional house can support marriage "
                    "within established family or cultural "
                    "frameworks."
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

        arranged_score += 0.35

        indicators.append(
            _indicator(
                "saturn_traditional_structure",
                "arranged",
                0.35,
                (
                    "Saturn connected with family, partnership "
                    "or tradition can emphasise structure, duty "
                    "and conventional decision-making."
                ),
                house=(
                    saturn_house
                ),
            )
        )

    if second_occupants:

        family_planets = {
            "Jupiter",
            "Saturn",
            "Sun",
            "Moon",
        }

        family_count = sum(
            1
            for planet
            in second_occupants
            if planet
            in family_planets
        )

        if family_count:

            contribution = min(
                family_count
                * 0.15,
                0.45,
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
                        "The 2nd house carries additional "
                        "family-oriented planetary emphasis, "
                        "which can increase family involvement "
                        "in marriage decisions."
                    ),
                    occupants=(
                        second_occupants
                    ),
                )
            )

    # =====================================================
    # 8. SOCIAL NETWORK / FRIENDSHIP PATHWAY
    # =====================================================

    if "Venus" in eleventh_occupants:

        love_score += 0.30

    if "Mercury" in eleventh_occupants:

        love_score += 0.20

    if "Rahu" in eleventh_occupants:

        love_score += 0.20

    # =====================================================
    # NORMALISATION
    # =====================================================

    raw_love_score = round(
        love_score,
        3,
    )

    raw_arranged_score = round(
        arranged_score,
        3,
    )

    total = (
        love_score
        + arranged_score
    )

    if total <= 0:

        love_probability = 0.5

        arranged_probability = 0.5

    else:

        love_probability = (
            love_score
            / total
        )

        arranged_probability = (
            arranged_score
            / total
        )

    love_probability = round(
        _clamp(
            love_probability
        ),
        3,
    )

    arranged_probability = round(
        _clamp(
            arranged_probability
        ),
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
        love_probability >= 0.70
        and margin >= 0.30
    ):

        outcome = (
            "love_marriage_more_likely"
        )

        label = (
            "Love Marriage More Likely"
        )

        confidence = min(
            0.90,
            0.62
            + margin * 0.60,
        )

    elif (
        arranged_probability >= 0.70
        and margin >= 0.30
    ):

        outcome = (
            "arranged_marriage_more_likely"
        )

        label = (
            "Arranged Marriage More Likely"
        )

        confidence = min(
            0.90,
            0.62
            + margin * 0.60,
        )

    else:

        outcome = (
            "mixed_or_hybrid"
        )

        label = (
            "Mixed / Hybrid Pathway"
        )

        confidence = (
            0.72
            if total > 0
            else 0.50
        )

    confidence = round(
        _clamp(
            confidence
        ),
        3,
    )

    # =====================================================
    # EVIDENCE RANKING
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

    love_indicators.sort(
        key=lambda item: (
            _safe_float(
                item.get(
                    "strength"
                )
            )
        ),
        reverse=True,
    )

    arranged_indicators.sort(
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
    # USER-FACING SUMMARY
    # =====================================================

    if outcome == (
        "love_marriage_more_likely"
    ):

        summary = (
            "The natal evidence leans more strongly toward "
            "a self-initiated or love-based relationship "
            "developing into marriage, although family "
            "involvement may still influence the final union."
        )

    elif outcome == (
        "arranged_marriage_more_likely"
    ):

        summary = (
            "The natal evidence leans more strongly toward "
            "family-mediated or conventionally structured "
            "marriage, although personal attraction and "
            "choice may still remain important."
        )

    else:

        summary = (
            "The natal evidence is mixed, suggesting a hybrid "
            "pathway may be more appropriate than a strict "
            "love-versus-arranged classification. Personal "
            "choice and family involvement may both play "
            "meaningful roles."
        )

    return {
        "available": True,

        "event": (
            "love_vs_arranged"
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
                raw_love_score
            ),

            "arranged_raw": (
                raw_arranged_score
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
                    fifth_house.get(
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

            "second_house": {
                "sign": (
                    second_house.get(
                        "sign"
                    )
                ),

                "lord": (
                    second_house.get(
                        "lord"
                    )
                ),

                "occupants": (
                    second_occupants
                ),
            },

            "eleventh_house": {
                "sign": (
                    eleventh_house.get(
                        "sign"
                    )
                ),

                "lord": (
                    eleventh_house.get(
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

        "all_indicators": (
            indicators
        ),
    }
