from typing import Any


PLANET_DIGNITY = {
    "Sun": {
        "exalted": "Aries",
        "debilitated": "Libra",
        "own_signs": {"Leo"},
    },
    "Moon": {
        "exalted": "Taurus",
        "debilitated": "Scorpio",
        "own_signs": {"Cancer"},
    },
    "Mars": {
        "exalted": "Capricorn",
        "debilitated": "Cancer",
        "own_signs": {"Aries", "Scorpio"},
    },
    "Mercury": {
        "exalted": "Virgo",
        "debilitated": "Pisces",
        "own_signs": {"Gemini", "Virgo"},
    },
    "Jupiter": {
        "exalted": "Cancer",
        "debilitated": "Capricorn",
        "own_signs": {"Sagittarius", "Pisces"},
    },
    "Venus": {
        "exalted": "Pisces",
        "debilitated": "Virgo",
        "own_signs": {"Taurus", "Libra"},
    },
    "Saturn": {
        "exalted": "Libra",
        "debilitated": "Aries",
        "own_signs": {"Capricorn", "Aquarius"},
    },
}


CAREER_PLANET_ROLES = {
    "Sun": (
        "leadership, authority, recognition "
        "and public visibility"
    ),
    "Mercury": (
        "analysis, communication, commerce, "
        "data and documentation"
    ),
    "Jupiter": (
        "knowledge, advisory work, finance, "
        "guidance and judgment"
    ),
    "Venus": (
        "relationships, negotiation, creativity "
        "and value-oriented work"
    ),
    "Mars": (
        "initiative, execution, competition, "
        "operations and technical action"
    ),
    "Saturn": (
        "structure, governance, discipline, "
        "compliance and long-term responsibility"
    ),
}


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _get_dignity(
    planet_name: str,
    sign: str | None,
) -> dict[str, Any]:
    """
    Determine simple sign dignity for a planet.

    This intentionally uses only:
    - exaltation
    - debilitation
    - own sign

    More advanced dignity logic can be added later.
    """

    rules = PLANET_DIGNITY.get(
        planet_name,
        {},
    )

    if not sign or not rules:
        return {
            "dignity": "neutral",
            "strength": 0.5,
        }

    if sign == rules.get("exalted"):
        return {
            "dignity": "exalted",
            "strength": 1.0,
        }

    if sign == rules.get("debilitated"):
        return {
            "dignity": "debilitated",
            "strength": 0.25,
        }

    own_signs = rules.get(
        "own_signs",
        set(),
    )

    if sign in own_signs:
        return {
            "dignity": "own_sign",
            "strength": 0.85,
        }

    return {
        "dignity": "neutral",
        "strength": 0.5,
    }


def _analyse_planet(
    chart: dict[str, Any],
    planet_name: str,
) -> dict[str, Any]:
    """
    Analyse one career-relevant planet.
    """

    planets = _safe_dict(
        chart.get("planets")
    )

    planet = _safe_dict(
        planets.get(planet_name)
    )

    if not planet:
        return {
            "available": False,
            "planet": planet_name,
        }

    sign = planet.get("sign")
    house = planet.get("house")
    retrograde = bool(
        planet.get("retrograde")
    )

    dignity = _get_dignity(
        planet_name,
        sign,
    )

    indicators: list[
        dict[str, Any]
    ] = []

    role = CAREER_PLANET_ROLES.get(
        planet_name
    )

    if role:
        indicators.append(
            {
                "factor": "career_planet_role",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} contributes themes of "
                    f"{role} to professional life."
                ),
                "strength": 0.5,
                "type": "theme",
            }
        )

    dignity_name = dignity.get(
        "dignity"
    )

    dignity_strength = float(
        dignity.get(
            "strength",
            0.5,
        )
    )

    if dignity_name == "exalted":
        indicators.append(
            {
                "factor": "career_planet_dignity",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is exalted in {sign}, "
                    "strengthening its ability to contribute "
                    "constructively to career-related matters."
                ),
                "strength": dignity_strength,
                "type": "positive",
            }
        )

    elif dignity_name == "own_sign":
        indicators.append(
            {
                "factor": "career_planet_dignity",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is in its own sign {sign}, "
                    "giving it strong capacity to express its "
                    "professional significations."
                ),
                "strength": dignity_strength,
                "type": "positive",
            }
        )

    elif dignity_name == "debilitated":
        indicators.append(
            {
                "factor": "career_planet_dignity",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is debilitated in {sign}, "
                    "which may require greater maturity, effort "
                    "or adjustment before its professional "
                    "significations operate smoothly."
                ),
                "strength": 0.75,
                "type": "challenge",
            }
        )

    # ---------------------------------------------------------
    # HOUSE-BASED CAREER CONTEXT
    # ---------------------------------------------------------

    if house == 10:
        indicators.append(
            {
                "factor": "career_planet_tenth_house",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is placed in the 10th house, "
                    "making its themes especially visible in "
                    "career, professional identity and public work."
                ),
                "strength": 0.9,
                "type": "positive",
            }
        )

    elif house == 11:
        indicators.append(
            {
                "factor": "career_planet_eleventh_house",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is placed in the 11th house, "
                    "linking its professional themes with gains, "
                    "networks, large groups and fulfilment of "
                    "career objectives."
                ),
                "strength": 0.65,
                "type": "positive",
            }
        )

    elif house == 12:
        indicators.append(
            {
                "factor": "career_planet_twelfth_house",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is placed in the 12th house, "
                    "linking its professional themes with large "
                    "institutions, foreign environments, remote "
                    "settings or behind-the-scenes work."
                ),
                "strength": 0.55,
                "type": "theme",
            }
        )

    elif house == 6:
        indicators.append(
            {
                "factor": "career_planet_sixth_house",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is placed in the 6th house, "
                    "connecting its professional themes with "
                    "service, competition, problem-solving, "
                    "compliance or operational responsibilities."
                ),
                "strength": 0.6,
                "type": "theme",
            }
        )

    # ---------------------------------------------------------
    # RETROGRADE
    # ---------------------------------------------------------

    if retrograde:
        indicators.append(
            {
                "factor": "career_planet_retrograde",
                "planet": planet_name,
                "interpretation": (
                    f"{planet_name} is retrograde, which may make "
                    "its professional themes more internalised, "
                    "reconsidered or developed through repeated "
                    "experience."
                ),
                "strength": 0.4,
                "type": "theme",
            }
        )

    return {
        "available": True,
        "planet": planet_name,
        "sign": sign,
        "house": house,
        "retrograde": retrograde,
        "longitude": planet.get(
            "longitude"
        ),
        "nakshatra": planet.get(
            "nakshatra"
        ),
        "dignity": dignity,
        "indicators": indicators,
    }


def analyze_career_planets(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyse the main career-relevant planets.

    Current scope:
    - Saturn
    - Mercury
    - Sun
    - Jupiter
    - Mars
    - Venus

    The output is intended for later synthesis with
    10th-house career reasoning.
    """

    planets_to_analyse = [
        "Saturn",
        "Mercury",
        "Sun",
        "Jupiter",
        "Mars",
        "Venus",
    ]

    results: dict[
        str,
        dict[str, Any],
    ] = {}

    indicators: list[
        dict[str, Any]
    ] = []

    positive_score = 0.0
    challenge_score = 0.0
    theme_score = 0.0

    for planet_name in planets_to_analyse:

        result = _analyse_planet(
            chart,
            planet_name,
        )

        results[
            planet_name
        ] = result

        if not result.get(
            "available"
        ):
            continue

        for indicator in result.get(
            "indicators",
            [],
        ):

            if not isinstance(
                indicator,
                dict,
            ):
                continue

            indicators.append(
                indicator
            )

            strength = float(
                indicator.get(
                    "strength",
                    0.0,
                )
            )

            indicator_type = (
                indicator.get(
                    "type"
                )
            )

            if indicator_type == "positive":
                positive_score += strength

            elif indicator_type == "challenge":
                challenge_score += strength

            elif indicator_type == "theme":
                theme_score += strength

    return {
        "available": True,
        "planets": results,
        "scores": {
            "positive_score": round(
                positive_score,
                2,
            ),
            "challenge_score": round(
                challenge_score,
                2,
            ),
            "theme_score": round(
                theme_score,
                2,
            ),
        },
        "indicators": indicators,
    }