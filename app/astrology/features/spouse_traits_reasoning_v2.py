from __future__ import annotations

from typing import Any

from app.astrology.dignity import (
    evaluate_planetary_dignities,
)


# =========================================================
# SIGN / PLANET TRAIT MAPS
# =========================================================

SIGN_ELEMENTS = {
    "Aries": "fire",
    "Taurus": "earth",
    "Gemini": "air",
    "Cancer": "water",
    "Leo": "fire",
    "Virgo": "earth",
    "Libra": "air",
    "Scorpio": "water",
    "Sagittarius": "fire",
    "Capricorn": "earth",
    "Aquarius": "air",
    "Pisces": "water",
}


SIGN_MODALITIES = {
    "Aries": "movable",
    "Taurus": "fixed",
    "Gemini": "dual",
    "Cancer": "movable",
    "Leo": "fixed",
    "Virgo": "dual",
    "Libra": "movable",
    "Scorpio": "fixed",
    "Sagittarius": "dual",
    "Capricorn": "movable",
    "Aquarius": "fixed",
    "Pisces": "dual",
}


SIGN_CORE_TRAITS = {
    "Aries": [
        "independent",
        "direct",
        "active",
        "self-driven",
    ],
    "Taurus": [
        "stable",
        "practical",
        "patient",
        "grounded",
    ],
    "Gemini": [
        "communicative",
        "curious",
        "adaptable",
        "mentally active",
    ],
    "Cancer": [
        "sensitive",
        "protective",
        "caring",
        "family-oriented",
    ],
    "Leo": [
        "confident",
        "expressive",
        "warm",
        "proud",
    ],
    "Virgo": [
        "analytical",
        "practical",
        "reserved",
        "detail-oriented",
    ],
    "Libra": [
        "diplomatic",
        "social",
        "balanced",
        "relationship-oriented",
    ],
    "Scorpio": [
        "intense",
        "private",
        "loyal",
        "emotionally deep",
    ],
    "Sagittarius": [
        "optimistic",
        "independent",
        "philosophical",
        "adventurous",
    ],
    "Capricorn": [
        "responsible",
        "mature",
        "disciplined",
        "practical",
        "reserved",
    ],
    "Aquarius": [
        "independent",
        "intellectual",
        "unconventional",
        "socially aware",
    ],
    "Pisces": [
        "sensitive",
        "empathetic",
        "imaginative",
        "gentle",
    ],
}


PLANET_CORE_TRAITS = {
    "Sun": [
        "confident",
        "self-respecting",
        "visible",
    ],
    "Moon": [
        "caring",
        "emotionally responsive",
        "sensitive",
    ],
    "Mars": [
        "assertive",
        "energetic",
        "decisive",
    ],
    "Mercury": [
        "communicative",
        "analytical",
        "curious",
    ],
    "Jupiter": [
        "principled",
        "supportive",
        "growth-oriented",
    ],
    "Venus": [
        "affectionate",
        "harmonious",
        "relationship-oriented",
    ],
    "Saturn": [
        "serious",
        "disciplined",
        "patient",
        "responsible",
    ],
    "Rahu": [
        "unconventional",
        "ambitious",
        "boundary-crossing",
    ],
    "Ketu": [
        "private",
        "independent",
        "detached",
        "inward-looking",
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
# TRAIT / EVIDENCE HELPERS
# =========================================================

def _trait_item(
    trait: str,
    source: str,
    tier: str,
    weight: float,
) -> dict[str, Any]:

    return {
        "trait": trait,
        "source": source,
        "tier": tier,
        "weight": round(
            _clamp(
                weight
            ),
            3,
        ),
    }


def _evidence(
    factor: str,
    dimension: str,
    tier: str,
    strength: float,
    interpretation: str,
    **details: Any,
) -> dict[str, Any]:

    result = {
        "factor": factor,
        "dimension": dimension,
        "tier": tier,
        "strength": round(
            _clamp(
                strength
            ),
            3,
        ),
        "interpretation": interpretation,
    }

    if details:
        result[
            "details"
        ] = details

    return result


def _dimension_confidence(
    primary_strength: float,
    secondary_strength: float,
    has_evidence: bool,
) -> float:

    if not has_evidence:
        return 0.0

    value = (
        0.45
        + primary_strength * 0.40
        + secondary_strength * 0.15
    )

    return round(
        _clamp(
            value,
            0.45,
            0.92,
        ),
        3,
    )


def _rank_traits(
    items: list[dict[str, Any]],
) -> list[str]:

    score_map: dict[str, float] = {}

    for item in items:

        trait = str(
            item.get(
                "trait",
                "",
            )
        )

        weight = _safe_float(
            item.get(
                "weight"
            )
        )

        if not trait:
            continue

        score_map[
            trait
        ] = (
            score_map.get(
                trait,
                0.0,
            )
            + weight
        )

    ranked = sorted(
        score_map.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        trait
        for trait, _
        in ranked
    ]


def _join_traits(
    traits: list[str],
) -> str:

    if not traits:
        return ""

    if len(
        traits
    ) == 1:
        return traits[
            0
        ]

    if len(
        traits
    ) == 2:
        return (
            f"{traits[0]} and {traits[1]}"
        )

    return (
        ", ".join(
            traits[:-1]
        )
        + f", and {traits[-1]}"
    )


# =========================================================
# MAIN ENGINE
# =========================================================

def analyze_spouse_traits_v2(
    chart: dict[str, Any],
) -> dict[str, Any]:

    if not isinstance(
        chart,
        dict,
    ):
        raise ValueError(
            "chart must be a dictionary."
        )

    seventh = (
        _get_house(
            chart,
            7,
        )
    )

    if not seventh:

        return {
            "available": False,
            "reason": (
                "7th house data is unavailable."
            ),
        }

    seventh_sign = (
        seventh.get(
            "sign"
        )
    )

    seventh_lord = (
        seventh.get(
            "lord"
        )
    )

    seventh_lord_data = (
        _get_planet(
            chart,
            seventh_lord,
        )
    )

    seventh_occupants = (
        _planets_in_house(
            chart,
            7,
        )
    )

    venus = (
        _get_planet(
            chart,
            "Venus",
        )
    )

    moon = (
        _get_planet(
            chart,
            "Moon",
        )
    )

    mercury = (
        _get_planet(
            chart,
            "Mercury",
        )
    )

    jupiter = (
        _get_planet(
            chart,
            "Jupiter",
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

    venus_dignity = (
        _safe_dict(
            dignity_map.get(
                "Venus"
            )
        )
    )

    evidence = []

    trait_items = {
        "core_personality": [],
        "temperament": [],
        "emotional_style": [],
        "communication_style": [],
        "career_orientation": [],
        "social_background": [],
        "relationship_behaviour": [],
        "unconventional_traits": [],
    }

    # =====================================================
    # PRIMARY: 7TH SIGN
    # =====================================================

    sign_traits = (
        SIGN_CORE_TRAITS.get(
            str(
                seventh_sign
            ),
            [],
        )
    )

    for trait in sign_traits:

        trait_items[
            "core_personality"
        ].append(
            _trait_item(
                trait,
                "seventh_house_sign",
                "primary",
                1.0,
            )
        )

    seventh_element = (
        SIGN_ELEMENTS.get(
            str(
                seventh_sign
            )
        )
    )

    seventh_modality = (
        SIGN_MODALITIES.get(
            str(
                seventh_sign
            )
        )
    )

    element_traits = {
        "earth": [
            "grounded",
            "realistic",
            "practical",
        ],
        "water": [
            "sensitive",
            "emotionally deep",
        ],
        "fire": [
            "active",
            "direct",
            "independent",
        ],
        "air": [
            "communicative",
            "intellectual",
            "social",
        ],
    }

    for trait in element_traits.get(
        seventh_element,
        [],
    ):

        trait_items[
            "temperament"
        ].append(
            _trait_item(
                trait,
                "seventh_house_element",
                "primary",
                0.85,
            )
        )

    evidence.append(
        _evidence(
            "seventh_house_sign",
            "core_personality",
            "primary",
            1.0,
            (
                f"The 7th house falls in {seventh_sign}, "
                "making this the primary baseline for the "
                "spouse profile."
            ),
            sign=seventh_sign,
            element=seventh_element,
            modality=seventh_modality,
        )
    )

    # =====================================================
    # PRIMARY: 7TH LORD
    # =====================================================

    seventh_lord_sign = (
        seventh_lord_data.get(
            "sign"
        )
    )

    seventh_lord_house = (
        seventh_lord_data.get(
            "house"
        )
    )

    seventh_lord_nakshatra = (
        _safe_dict(
            seventh_lord_data.get(
                "nakshatra"
            )
        )
    )

    for trait in PLANET_CORE_TRAITS.get(
        str(
            seventh_lord
        ),
        [],
    ):

        trait_items[
            "core_personality"
        ].append(
            _trait_item(
                trait,
                "seventh_lord_planet",
                "primary",
                0.90,
            )
        )

    for trait in SIGN_CORE_TRAITS.get(
        str(
            seventh_lord_sign
        ),
        [],
    )[:3]:

        trait_items[
            "core_personality"
        ].append(
            _trait_item(
                trait,
                "seventh_lord_sign",
                "primary",
                0.75,
            )
        )

    evidence.append(
        _evidence(
            "seventh_lord_profile",
            "core_personality",
            "primary",
            0.95,
            (
                f"The 7th lord {seventh_lord} is placed in "
                f"{seventh_lord_sign}, adding both planetary "
                "and sign qualities to the spouse profile."
            ),
            planet=seventh_lord,
            sign=seventh_lord_sign,
            house=seventh_lord_house,
            nakshatra=(
                seventh_lord_nakshatra.get(
                    "name"
                )
            ),
        )
    )

    # =====================================================
    # PRIMARY: 7TH LORD HOUSE
    # =====================================================

    if seventh_lord_house == 10:

        for trait in (
            "career-focused",
            "ambitious",
            "responsibility-oriented",
            "professionally visible",
        ):

            trait_items[
                "career_orientation"
            ].append(
                _trait_item(
                    trait,
                    "seventh_lord_in_tenth",
                    "primary",
                    0.90,
                )
            )

        evidence.append(
            _evidence(
                "seventh_lord_in_tenth",
                "career_orientation",
                "primary",
                0.90,
                (
                    "The 7th lord is placed in the 10th house, "
                    "strongly linking the spouse pattern with "
                    "career, ambition, responsibility and "
                    "public life."
                ),
            )
        )

    elif seventh_lord_house == 9:

        for trait in (
            "educated",
            "principled",
            "culturally aware",
        ):

            trait_items[
                "social_background"
            ].append(
                _trait_item(
                    trait,
                    "seventh_lord_in_ninth",
                    "primary",
                    0.75,
                )
            )

    elif seventh_lord_house == 11:

        for trait in (
            "socially connected",
            "network-oriented",
        ):

            trait_items[
                "social_background"
            ].append(
                _trait_item(
                    trait,
                    "seventh_lord_in_eleventh",
                    "primary",
                    0.70,
                )
            )

    elif seventh_lord_house == 12:

        for trait in (
            "private background",
            "possible foreign or distant connection",
        ):

            trait_items[
                "social_background"
            ].append(
                _trait_item(
                    trait,
                    "seventh_lord_in_twelfth",
                    "primary",
                    0.70,
                )
            )

    # =====================================================
    # PRIMARY: DIGNITY
    # =====================================================

    seventh_dignity = (
        seventh_lord_dignity.get(
            "dignity"
        )
    )

    if seventh_dignity in (
        "exalted",
        "own_sign",
    ):

        for trait in (
            "reliable in commitment",
            "stable in partnership",
        ):

            trait_items[
                "relationship_behaviour"
            ].append(
                _trait_item(
                    trait,
                    "seventh_lord_dignity",
                    "primary",
                    0.75,
                )
            )

    elif seventh_dignity == "debilitated":

        for trait in (
            "patience and adjustment",
            "balancing stability with independence",
        ):

            trait_items[
                "relationship_behaviour"
            ].append(
                _trait_item(
                    trait,
                    "seventh_lord_dignity",
                    "primary",
                    0.70,
                )
            )

        evidence.append(
            _evidence(
                "seventh_lord_dignity",
                "relationship_behaviour",
                "primary",
                0.70,
                (
                    "The 7th lord is debilitated. This is "
                    "treated as a partnership pattern involving "
                    "patience, adjustment and a need to balance "
                    "stability with independence."
                ),
                dignity=seventh_dignity,
            )
        )

    # =====================================================
    # PRIMARY: 7TH OCCUPANTS
    # =====================================================

    for planet in seventh_occupants:

        if planet == "Ketu":

            for trait in (
                "private",
                "independent",
                "may need personal space",
                "less conventionally expressive",
            ):

                trait_items[
                    "unconventional_traits"
                ].append(
                    _trait_item(
                        trait,
                        "ketu_in_seventh",
                        "primary",
                        0.85,
                    )
                )

            for trait in (
                "private",
                "independent",
            ):

                trait_items[
                    "relationship_behaviour"
                ].append(
                    _trait_item(
                        trait,
                        "ketu_in_seventh",
                        "primary",
                        0.70,
                    )
                )

            evidence.append(
                _evidence(
                    "ketu_in_seventh",
                    "unconventional_traits",
                    "primary",
                    0.85,
                    (
                        "Ketu occupies the 7th house, adding "
                        "privacy, independence, personal-space "
                        "needs and a less conventional quality "
                        "to partnership expression."
                    ),
                )
            )

        elif planet == "Rahu":

            for trait in (
                "unconventional",
                "boundary-crossing",
                "socially different",
            ):

                trait_items[
                    "unconventional_traits"
                ].append(
                    _trait_item(
                        trait,
                        "rahu_in_seventh",
                        "primary",
                        0.85,
                    )
                )

        elif planet == "Venus":

            for trait in (
                "affectionate",
                "relationship-oriented",
            ):

                trait_items[
                    "relationship_behaviour"
                ].append(
                    _trait_item(
                        trait,
                        "venus_in_seventh",
                        "primary",
                        0.80,
                    )
                )

        elif planet == "Moon":

            for trait in (
                "emotionally expressive",
                "caring",
            ):

                trait_items[
                    "emotional_style"
                ].append(
                    _trait_item(
                        trait,
                        "moon_in_seventh",
                        "primary",
                        0.80,
                    )
                )

        elif planet == "Mercury":

            for trait in (
                "communicative",
                "mentally active",
            ):

                trait_items[
                    "communication_style"
                ].append(
                    _trait_item(
                        trait,
                        "mercury_in_seventh",
                        "primary",
                        0.80,
                    )
                )

    # =====================================================
    # SECONDARY: VENUS
    # =====================================================

    venus_sign = (
        venus.get(
            "sign"
        )
    )

    venus_house = (
        venus.get(
            "house"
        )
    )

    if (
        venus_dignity.get(
            "dignity"
        )
        == "exalted"
    ):

        for trait in (
            "affectionate",
            "romantic",
            "empathetic",
        ):

            trait_items[
                "relationship_behaviour"
            ].append(
                _trait_item(
                    trait,
                    "venus_exalted",
                    "secondary",
                    0.60,
                )
            )

        evidence.append(
            _evidence(
                "venus_exalted",
                "relationship_behaviour",
                "secondary",
                0.60,
                (
                    "Exalted Venus acts as a secondary "
                    "modifier supporting affection, warmth "
                    "and relationship sensitivity."
                ),
                sign=venus_sign,
                house=venus_house,
            )
        )

    # =====================================================
    # SECONDARY: MOON
    # =====================================================

    moon_sign = (
        moon.get(
            "sign"
        )
    )

    if moon_sign:

        for trait in SIGN_CORE_TRAITS.get(
            str(
                moon_sign
            ),
            [],
        )[:3]:

            trait_items[
                "emotional_style"
            ].append(
                _trait_item(
                    trait,
                    "moon_sign_modifier",
                    "secondary",
                    0.45,
                )
            )

        evidence.append(
            _evidence(
                "moon_sign_modifier",
                "emotional_style",
                "secondary",
                0.45,
                (
                    f"The Moon in {moon_sign} adds secondary "
                    "emotional qualities to the partner and "
                    "relationship profile."
                ),
                sign=moon_sign,
                house=(
                    moon.get(
                        "house"
                    )
                ),
            )
        )

    # =====================================================
    # SECONDARY: MERCURY
    # =====================================================

    mercury_sign = (
        mercury.get(
            "sign"
        )
    )

    if mercury_sign:

        mercury_traits = (
            SIGN_CORE_TRAITS.get(
                str(
                    mercury_sign
                ),
                [],
            )[:2]
        )

        mercury_traits += [
            "communicative",
            "analytical",
        ]

        for trait in _unique(
            mercury_traits
        ):

            trait_items[
                "communication_style"
            ].append(
                _trait_item(
                    trait,
                    "mercury_modifier",
                    "secondary",
                    0.40,
                )
            )

        evidence.append(
            _evidence(
                "mercury_modifier",
                "communication_style",
                "secondary",
                0.40,
                (
                    f"Mercury in {mercury_sign} adds a "
                    "secondary communication-style modifier."
                ),
                sign=mercury_sign,
                house=(
                    mercury.get(
                        "house"
                    )
                ),
            )
        )

    # =====================================================
    # SECONDARY: JUPITER
    # =====================================================

    jupiter_house = (
        jupiter.get(
            "house"
        )
    )

    jupiter_sign = (
        jupiter.get(
            "sign"
        )
    )

    if jupiter_house == 10:

        for trait in (
            "growth-oriented",
            "leadership-capable",
        ):

            trait_items[
                "career_orientation"
            ].append(
                _trait_item(
                    trait,
                    "jupiter_in_tenth",
                    "secondary",
                    0.45,
                )
            )

        evidence.append(
            _evidence(
                "jupiter_in_tenth",
                "career_orientation",
                "secondary",
                0.45,
                (
                    "Jupiter in the 10th acts as a secondary "
                    "modifier supporting professional growth "
                    "and leadership."
                ),
                sign=jupiter_sign,
            )
        )

    # =====================================================
    # RANK DIMENSIONS
    # =====================================================

    profile = {}

    confidence_by_dimension = {}

    for (
        dimension,
        items,
    ) in trait_items.items():

        profile[
            dimension
        ] = (
            _rank_traits(
                items
            )
        )

        primary_strength = min(
            sum(
                _safe_float(
                    item.get(
                        "weight"
                    )
                )
                for item in items
                if item.get(
                    "tier"
                )
                == "primary"
            ),
            1.0,
        )

        secondary_strength = min(
            sum(
                _safe_float(
                    item.get(
                        "weight"
                    )
                )
                for item in items
                if item.get(
                    "tier"
                )
                == "secondary"
            ),
            1.0,
        )

        confidence_by_dimension[
            dimension
        ] = (
            _dimension_confidence(
                primary_strength,
                secondary_strength,
                bool(
                    items
                ),
            )
        )

    # =====================================================
    # BLENDED / CONTRADICTORY TRAITS
    # =====================================================

    blends = []

    core = (
        profile[
            "core_personality"
        ]
    )

    unconventional = (
        profile[
            "unconventional_traits"
        ]
    )

    relationship = (
        profile[
            "relationship_behaviour"
        ]
    )

    if (
        "reserved" in core
        and "direct" in core
    ):

        blends.append(
            {
                "theme": (
                    "reserved_but_direct"
                ),
                "interpretation": (
                    "The spouse pattern combines a reserved "
                    "or serious exterior with a more direct, "
                    "independent streak once engaged."
                ),
            }
        )

    if (
        "responsible" in core
        and (
            "independent" in core
            or "independent"
            in unconventional
        )
    ):

        blends.append(
            {
                "theme": (
                    "responsible_but_independent"
                ),
                "interpretation": (
                    "Responsibility and commitment are present, "
                    "while autonomy and personal space may also "
                    "be important."
                ),
            }
        )

    if (
        "private" in unconventional
        and (
            "affectionate" in relationship
            or "romantic" in relationship
        )
    ):

        blends.append(
            {
                "theme": (
                    "private_but_affectionate"
                ),
                "interpretation": (
                    "The profile may appear private or reserved "
                    "externally while still showing warmth and "
                    "affection in close relationships."
                ),
            }
        )

    # =====================================================
    # NATURAL-LANGUAGE SUMMARY
    # =====================================================

    summary_parts = []

    core_top = (
        profile[
            "core_personality"
        ][:5]
    )

    if core_top:

        summary_parts.append(
            (
                "The spouse profile leans toward someone "
                + _join_traits(
                    core_top
                )
            )
        )

    career_top = (
        profile[
            "career_orientation"
        ][:2]
    )

    if career_top:

        summary_parts.append(
            (
                "Professionally, they may be "
                + _join_traits(
                    career_top
                )
            )
        )

    emotional_top = (
        profile[
            "emotional_style"
        ][:2]
    )

    if emotional_top:

        summary_parts.append(
            (
                "Emotionally, they may be "
                + _join_traits(
                    emotional_top
                )
            )
        )

    relationship_top = (
        profile[
            "relationship_behaviour"
        ][:2]
    )

    if relationship_top:

        summary_parts.append(
            (
                "In partnership, themes of "
                + _join_traits(
                    relationship_top
                )
                + " may be important"
            )
        )

    if blends:

        summary_parts.append(
            blends[
                0
            ][
                "interpretation"
            ]
        )

    summary = (
        ". ".join(
            part.rstrip(
                "."
            )
            for part in summary_parts
            if part
        )
        + "."
    )

    # =====================================================
    # OVERALL CONFIDENCE
    # =====================================================
    #
    # Only dimensions that contain actual evidence should
    # influence the aggregate score.
    # =====================================================

    dimension_weights = {
        "core_personality": 0.35,
        "career_orientation": 0.20,
        "relationship_behaviour": 0.20,
        "emotional_style": 0.10,
        "communication_style": 0.05,
        "unconventional_traits": 0.10,
    }

    weighted_total = 0.0

    weight_total = 0.0

    for (
        dimension,
        weight,
    ) in dimension_weights.items():

        confidence = (
            confidence_by_dimension.get(
                dimension,
                0.0,
            )
        )

        if confidence <= 0:
            continue

        weighted_total += (
            confidence
            * weight
        )

        weight_total += weight

    if weight_total:

        overall_confidence = round(
            weighted_total
            / weight_total,
            3,
        )

    else:

        overall_confidence = 0.45

    return {
        "available": True,

        "event": (
            "spouse_traits"
        ),

        "model_version": (
            "v2.1"
        ),

        "confidence": (
            overall_confidence
        ),

        "summary": (
            summary
        ),

        "profile": (
            profile
        ),

        "confidence_by_dimension": (
            confidence_by_dimension
        ),

        "blended_traits": (
            blends
        ),

        "chart_context": {
            "seventh_house": {
                "sign": (
                    seventh_sign
                ),

                "lord": (
                    seventh_lord
                ),

                "element": (
                    seventh_element
                ),

                "modality": (
                    seventh_modality
                ),

                "occupants": (
                    seventh_occupants
                ),
            },

            "seventh_lord": {
                "planet": (
                    seventh_lord
                ),

                "sign": (
                    seventh_lord_sign
                ),

                "house": (
                    seventh_lord_house
                ),

                "nakshatra": (
                    seventh_lord_nakshatra
                ),

                "dignity": (
                    seventh_dignity
                ),
            },

            "venus": {
                "sign": (
                    venus_sign
                ),

                "house": (
                    venus_house
                ),

                "dignity": (
                    venus_dignity.get(
                        "dignity"
                    )
                ),
            },

            "moon": {
                "sign": (
                    moon_sign
                ),

                "house": (
                    moon.get(
                        "house"
                    )
                ),
            },

            "mercury": {
                "sign": (
                    mercury_sign
                ),

                "house": (
                    mercury.get(
                        "house"
                    )
                ),
            },

            "jupiter": {
                "sign": (
                    jupiter_sign
                ),

                "house": (
                    jupiter_house
                ),
            },
        },

        "trait_evidence": (
            trait_items
        ),

        "evidence": (
            evidence
        ),
    }
