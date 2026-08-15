from __future__ import annotations

from typing import Any

from app.astrology.dignity import (
    evaluate_planetary_dignities,
)


# =========================================================
# SIGN ATTRIBUTES
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


SIGN_TRAITS = {
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
        "comfort-oriented",
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
        "family-oriented",
        "emotionally receptive",
    ],
    "Leo": [
        "confident",
        "expressive",
        "proud",
        "warm",
    ],
    "Virgo": [
        "analytical",
        "practical",
        "detail-oriented",
        "reserved",
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
        "independent",
        "optimistic",
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


PLANET_TRAITS = {
    "Sun": [
        "confident",
        "self-respecting",
        "visible",
    ],
    "Moon": [
        "emotionally responsive",
        "caring",
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
        "aesthetic",
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
        "detached",
        "independent",
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


def _safe_list(
    value: Any,
) -> list[Any]:

    if isinstance(
        value,
        list,
    ):
        return value

    return []


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


def _evidence(
    factor: str,
    dimension: str,
    strength: float,
    interpretation: str,
    **details: Any,
) -> dict[str, Any]:

    result = {
        "factor": factor,
        "dimension": dimension,
        "strength": round(
            min(
                max(
                    float(
                        strength
                    ),
                    0.0,
                ),
                1.0,
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


# =========================================================
# MAIN ENGINE
# =========================================================

def analyze_spouse_traits_v1(
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

    evidence = []

    core_traits = []

    temperament = []

    emotional_style = []

    communication_style = []

    career_orientation = []

    social_background = []

    relationship_behaviour = []

    unconventional_traits = []

    # =====================================================
    # 1. 7TH SIGN — BASE SPOUSE PROFILE
    # =====================================================

    sign_traits = (
        SIGN_TRAITS.get(
            str(
                seventh_sign
            ),
            [],
        )
    )

    core_traits.extend(
        sign_traits
    )

    element = (
        SIGN_ELEMENTS.get(
            str(
                seventh_sign
            )
        )
    )

    modality = (
        SIGN_MODALITIES.get(
            str(
                seventh_sign
            )
        )
    )

    if element == "earth":

        temperament.extend(
            [
                "grounded",
                "practical",
                "realistic",
            ]
        )

    elif element == "water":

        temperament.extend(
            [
                "sensitive",
                "emotionally deep",
            ]
        )

    elif element == "fire":

        temperament.extend(
            [
                "active",
                "direct",
                "independent",
            ]
        )

    elif element == "air":

        temperament.extend(
            [
                "communicative",
                "social",
                "intellectual",
            ]
        )

    evidence.append(
        _evidence(
            "seventh_house_sign",
            "core_personality",
            1.0,
            (
                f"The 7th house falls in {seventh_sign}, "
                "making this sign the primary baseline "
                "for spouse personality."
            ),
            sign=seventh_sign,
            element=element,
            modality=modality,
        )
    )

    # =====================================================
    # 2. 7TH LORD — STRONG PERSONALITY MODIFIER
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

    core_traits.extend(
        PLANET_TRAITS.get(
            str(
                seventh_lord
            ),
            [],
        )
    )

    if seventh_lord_sign:

        core_traits.extend(
            SIGN_TRAITS.get(
                str(
                    seventh_lord_sign
                ),
                [],
            )[:3]
        )

    evidence.append(
        _evidence(
            "seventh_lord_profile",
            "core_personality",
            0.95,
            (
                f"The 7th lord {seventh_lord} is placed in "
                f"{seventh_lord_sign}, adding the qualities "
                "of both the planet and sign to the spouse "
                "profile."
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
    # 3. 7TH LORD HOUSE — LIFE / CAREER ORIENTATION
    # =====================================================

    if seventh_lord_house == 10:

        career_orientation.extend(
            [
                "career-focused",
                "ambitious",
                "professionally visible",
                "responsibility-oriented",
            ]
        )

        evidence.append(
            _evidence(
                "seventh_lord_in_tenth",
                "career_orientation",
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

        social_background.extend(
            [
                "educated",
                "principled",
                "culturally aware",
            ]
        )

    elif seventh_lord_house == 11:

        social_background.extend(
            [
                "socially connected",
                "network-oriented",
            ]
        )

    elif seventh_lord_house == 12:

        social_background.extend(
            [
                "private",
                "internationally oriented",
                "distance-related",
            ]
        )

        unconventional_traits.append(
            "possible foreign or distant connection"
        )

    # =====================================================
    # 4. 7TH LORD DIGNITY
    # =====================================================

    dignity = (
        seventh_lord_dignity.get(
            "dignity"
        )
    )

    if dignity in (
        "exalted",
        "own_sign",
    ):

        relationship_behaviour.extend(
            [
                "reliable",
                "stable in commitment",
            ]
        )

    elif dignity == "debilitated":

        relationship_behaviour.extend(
            [
                "may require time to mature in relationships",
                "can carry internal tension around partnership",
            ]
        )

        evidence.append(
            _evidence(
                "seventh_lord_dignity",
                "relationship_behaviour",
                0.70,
                (
                    "The 7th lord has reduced dignity, which "
                    "may make the spouse pattern more complex "
                    "or require greater maturity in partnership."
                ),
                dignity=dignity,
            )
        )

    # =====================================================
    # 5. 7TH HOUSE OCCUPANTS
    # =====================================================

    for planet in seventh_occupants:

        traits = (
            PLANET_TRAITS.get(
                planet,
                [],
            )
        )

        relationship_behaviour.extend(
            traits
        )

        if planet == "Ketu":

            unconventional_traits.extend(
                [
                    "private",
                    "independent",
                    "not strongly conventional",
                    "may need personal space",
                ]
            )

            evidence.append(
                _evidence(
                    "ketu_in_seventh",
                    "unconventional_traits",
                    0.80,
                    (
                        "Ketu occupies the 7th house, adding "
                        "privacy, independence and a less "
                        "conventional quality to the spouse "
                        "and relationship pattern."
                    ),
                )
            )

        elif planet == "Rahu":

            unconventional_traits.extend(
                [
                    "unconventional",
                    "socially different",
                    "boundary-crossing",
                ]
            )

        elif planet == "Venus":

            relationship_behaviour.extend(
                [
                    "affectionate",
                    "relationship-oriented",
                ]
            )

        elif planet == "Moon":

            emotional_style.extend(
                [
                    "emotionally expressive",
                    "caring",
                ]
            )

        elif planet == "Mercury":

            communication_style.extend(
                [
                    "talkative",
                    "intellectual",
                    "communicative",
                ]
            )

    # =====================================================
    # 6. VENUS — RELATIONSHIP STYLE MODIFIER
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

    venus_dignity = (
        _safe_dict(
            dignity_map.get(
                "Venus"
            )
        )
    )

    if venus_sign:

        relationship_behaviour.extend(
            SIGN_TRAITS.get(
                str(
                    venus_sign
                ),
                [],
            )[:3]
        )

    if venus_dignity.get(
        "dignity"
    ) == "exalted":

        relationship_behaviour.extend(
            [
                "affectionate",
                "romantic",
                "empathetic",
            ]
        )

        evidence.append(
            _evidence(
                "venus_exalted",
                "relationship_behaviour",
                0.75,
                (
                    "Exalted Venus strengthens warmth, "
                    "affection, empathy and relationship "
                    "sensitivity in the overall partner pattern."
                ),
                sign=venus_sign,
                house=venus_house,
            )
        )

    # =====================================================
    # 7. MOON — EMOTIONAL MODIFIER
    # =====================================================

    moon_sign = (
        moon.get(
            "sign"
        )
    )

    if moon_sign:

        emotional_style.extend(
            SIGN_TRAITS.get(
                str(
                    moon_sign
                ),
                [],
            )[:3]
        )

        evidence.append(
            _evidence(
                "moon_sign_modifier",
                "emotional_style",
                0.45,
                (
                    f"The Moon in {moon_sign} contributes "
                    "secondary emotional qualities to the "
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
    # 8. MERCURY — COMMUNICATION MODIFIER
    # =====================================================

    mercury_sign = (
        mercury.get(
            "sign"
        )
    )

    if mercury_sign:

        communication_style.extend(
            SIGN_TRAITS.get(
                str(
                    mercury_sign
                ),
                [],
            )[:3]
        )

        communication_style.extend(
            PLANET_TRAITS[
                "Mercury"
            ][:2]
        )

    # =====================================================
    # 9. JUPITER — VALUES / SOCIAL BACKGROUND MODIFIER
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

        career_orientation.extend(
            [
                "growth-oriented",
                "professionally ambitious",
                "leadership-capable",
            ]
        )

    if jupiter_sign:

        social_background.extend(
            SIGN_TRAITS.get(
                str(
                    jupiter_sign
                ),
                [],
            )[:2]
        )

    # =====================================================
    # 10. NORMALISE OUTPUT
    # =====================================================

    core_traits = (
        _unique(
            core_traits
        )
    )

    temperament = (
        _unique(
            temperament
        )
    )

    emotional_style = (
        _unique(
            emotional_style
        )
    )

    communication_style = (
        _unique(
            communication_style
        )
    )

    career_orientation = (
        _unique(
            career_orientation
        )
    )

    social_background = (
        _unique(
            social_background
        )
    )

    relationship_behaviour = (
        _unique(
            relationship_behaviour
        )
    )

    unconventional_traits = (
        _unique(
            unconventional_traits
        )
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    strongest_traits = (
        core_traits[:5]
    )

    if career_orientation:

        strongest_traits.extend(
            career_orientation[:2]
        )

    strongest_traits = (
        _unique(
            strongest_traits
        )
    )

    summary = (
        "The spouse profile leans toward someone "
        + ", ".join(
            strongest_traits[:7]
        )
        + "."
    )

    return {
        "available": True,

        "event": (
            "spouse_traits"
        ),

        "model_version": (
            "v1"
        ),

        "confidence": (
            0.82
        ),

        "summary": (
            summary
        ),

        "profile": {
            "core_personality": (
                core_traits
            ),

            "temperament": (
                temperament
            ),

            "emotional_style": (
                emotional_style
            ),

            "communication_style": (
                communication_style
            ),

            "career_orientation": (
                career_orientation
            ),

            "social_background": (
                social_background
            ),

            "relationship_behaviour": (
                relationship_behaviour
            ),

            "unconventional_traits": (
                unconventional_traits
            ),
        },

        "chart_context": {
            "seventh_house": {
                "sign": (
                    seventh_sign
                ),

                "lord": (
                    seventh_lord
                ),

                "element": (
                    element
                ),

                "modality": (
                    modality
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
                    dignity
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

        "evidence": (
            evidence
        ),
    }
