from typing import Any


MARRIAGE_PLANETS = {
    "Venus",
    "Jupiter",
    "Mars",
}


def _get_planet(
    chart: dict[str, Any],
    planet_name: str,
) -> dict[str, Any]:
    """Safely retrieve a planet from the calculated chart."""

    planets = chart.get("planets", {})

    if not isinstance(planets, dict):
        return {}

    planet = planets.get(planet_name)

    if isinstance(planet, dict):
        return planet

    return {}


def _get_house(
    planet: dict[str, Any],
) -> int | None:
    """Safely return the house occupied by a planet."""

    value = planet.get("house")

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_sign(
    planet: dict[str, Any],
) -> str | None:
    """Safely return the sign occupied by a planet."""

    value = planet.get("sign")

    if isinstance(value, str) and value:
        return value

    return None


def _get_seventh_house_analysis(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Retrieve the existing 7th-house analysis.

    This function intentionally reuses the existing marriage
    reasoning engine instead of duplicating 7th-house logic.
    """

    try:
        from .marriage_reasoning import analyze_seventh_house

        result = analyze_seventh_house(chart)

        if isinstance(result, dict):
            return result

    except (ImportError, AttributeError):
        pass

    return {}


def _extract_seventh_lord(
    chart: dict[str, Any],
    seventh_house_analysis: dict[str, Any],
) -> str | None:
    """Extract the 7th lord from existing marriage reasoning."""

    seventh_house = seventh_house_analysis.get(
        "seventh_house",
        {},
    )

    if isinstance(seventh_house, dict):
        for key in (
            "lord",
            "lord_planet",
            "seventh_lord",
        ):
            value = seventh_house.get(key)

            if isinstance(value, str) and value:
                return value

    for key in (
        "seventh_lord",
        "seventh_lord_planet",
        "lord",
    ):
        value = seventh_house_analysis.get(key)

        if isinstance(value, str) and value:
            return value

    indicators = seventh_house_analysis.get(
        "indicators",
        [],
    )

    if isinstance(indicators, list):
        for indicator in indicators:

            if not isinstance(indicator, dict):
                continue

            factor = indicator.get("factor")

            if factor in {
                "seventh_lord",
                "seventh_lord_planet",
            }:
                value = indicator.get("value")

                if isinstance(value, str) and value:
                    return value

    return None


def _analyse_dasha_planet(
    chart: dict[str, Any],
    planet_name: str,
    role: str,
    seventh_lord: str | None,
) -> dict[str, Any]:
    """
    Analyse a Mahadasha or Antardasha planet for marriage
    activation.
    """

    planet = _get_planet(
        chart,
        planet_name,
    )

    house = _get_house(planet)
    sign = _get_sign(planet)

    indicators: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # 7th lord activation
    # ---------------------------------------------------------

    if seventh_lord == planet_name:

        indicators.append(
            {
                "factor": "dasha_seventh_lord_activation",
                "interpretation": (
                    f"{role} lord {planet_name} is the 7th lord, "
                    "creating direct activation of marriage and "
                    "partnership matters during this period."
                ),
                "strength": 0.95 if role == "Antardasha" else 0.9,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # Venus activation
    # ---------------------------------------------------------

    if planet_name == "Venus":

        indicators.append(
            {
                "factor": "dasha_venus_activation",
                "interpretation": (
                    f"{role} lord Venus is a primary marriage "
                    "significator and can activate affection, "
                    "attraction, partnership and relationship "
                    "developments during this period."
                ),
                "strength": 0.9,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # Jupiter activation
    # ---------------------------------------------------------

    if planet_name == "Jupiter":

        indicators.append(
            {
                "factor": "dasha_jupiter_activation",
                "interpretation": (
                    f"{role} lord Jupiter can support growth, "
                    "commitment, stability and partnership "
                    "development during this period."
                ),
                "strength": 0.7,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # Mars activation
    # ---------------------------------------------------------

    if planet_name == "Mars":

        indicators.append(
            {
                "factor": "dasha_mars_activation",
                "interpretation": (
                    f"{role} lord Mars can activate relationship "
                    "matters, particularly when connected with "
                    "the 7th house or 7th lord."
                ),
                "strength": 0.6,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # 7th house
    # ---------------------------------------------------------

    if house == 7:

        indicators.append(
            {
                "factor": "dasha_planet_seventh_house",
                "interpretation": (
                    f"{role} lord {planet_name} is placed in the "
                    "7th house, directly activating partnership "
                    "and marriage themes."
                ),
                "strength": 0.9,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # 5th house
    # ---------------------------------------------------------

    if house == 5:

        indicators.append(
            {
                "factor": "dasha_planet_fifth_house",
                "interpretation": (
                    f"{role} lord {planet_name} is placed in the "
                    "5th house, which can activate romance, "
                    "attraction and emotional connection."
                ),
                "strength": 0.6,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # 11th house
    # ---------------------------------------------------------

    if house == 11:

        indicators.append(
            {
                "factor": "dasha_planet_eleventh_house",
                "interpretation": (
                    f"{role} lord {planet_name} is placed in the "
                    "11th house, which may support fulfilment "
                    "of relationship desires, social connections "
                    "and gains through relationships."
                ),
                "strength": 0.6,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # 12th house
    # ---------------------------------------------------------

    if house == 12:

        indicators.append(
            {
                "factor": "dasha_planet_twelfth_house",
                "interpretation": (
                    f"{role} lord {planet_name} is placed in the "
                    "12th house, introducing themes of distance, "
                    "privacy, relocation, foreign environments "
                    "or expenditure into relationship matters."
                ),
                "strength": 0.5,
                "type": "theme",
            }
        )

    return {
        "planet": planet_name,
        "role": role,
        "house": house,
        "sign": sign,
        "is_seventh_lord": (
            seventh_lord == planet_name
            if seventh_lord
            else False
        ),
        "indicators": indicators,
    }


def _calculate_scores(
    indicators: list[dict[str, Any]],
) -> dict[str, float]:
    """
    Convert individual indicators into structured scores.

    Positive indicators represent marriage-supporting activation.

    Theme indicators represent circumstances or relationship
    conditions that may influence how the period manifests.

    Challenge indicators represent explicitly adverse factors.
    """

    positive_score = 0.0
    theme_score = 0.0
    challenge_score = 0.0

    for indicator in indicators:

        try:
            strength = float(
                indicator.get("strength", 0.0)
            )
        except (TypeError, ValueError):
            strength = 0.0

        indicator_type = indicator.get("type")

        if indicator_type == "positive":
            positive_score += strength

        elif indicator_type == "theme":
            theme_score += strength

        elif indicator_type == "challenge":
            challenge_score += strength

    # Keep scores bounded and predictable.
    positive_score = min(
        round(positive_score, 3),
        1.0,
    )

    theme_score = min(
        round(theme_score, 3),
        1.0,
    )

    challenge_score = min(
        round(challenge_score, 3),
        1.0,
    )

    return {
        "positive_score": positive_score,
        "theme_score": theme_score,
        "challenge_score": challenge_score,
    }


def _determine_outlook(
    positive_score: float,
    theme_score: float,
    challenge_score: float,
) -> str:
    """
    Determine a high-level Dasha marriage outlook.

    This deliberately avoids calling a period 'marriage'
    solely from one indicator.
    """

    if challenge_score >= 0.75:
        return "challenging"

    if positive_score >= 0.75 and challenge_score < 0.5:
        return "strongly_supportive"

    if positive_score >= 0.45 and challenge_score < 0.6:
        return "moderately_supportive"

    if theme_score > 0:
        return "mixed"

    return "neutral"


def _calculate_confidence(
    positive_score: float,
    theme_score: float,
    challenge_score: float,
    indicator_count: int,
) -> float:
    """
    Calculate confidence based on the amount and consistency
    of supporting evidence.
    """

    if indicator_count == 0:
        return 0.5

    evidence_strength = (
        positive_score
        + theme_score
        + challenge_score
    )

    if evidence_strength >= 1.0:
        confidence = 0.8
    elif evidence_strength >= 0.5:
        confidence = 0.7
    else:
        confidence = 0.6

    # Multiple independent indicators increase confidence.
    if indicator_count >= 3:
        confidence += 0.05

    return min(
        round(confidence, 2),
        0.95,
    )


def analyze_current_dasha_for_marriage(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyse the currently active Vimshottari Dasha period
    for marriage-related indications.

    The output is evidence-oriented and intended to be consumed
    by the higher-level marriage prediction/synthesis layer.
    """

    dashas = chart.get(
        "dashas",
        {},
    )

    if not isinstance(dashas, dict):

        return {
            "available": False,
            "reason": (
                "Dasha information is not available."
            ),
            "indicators": [],
        }

    current_period = dashas.get(
        "current_period"
    )

    if not isinstance(current_period, dict):

        return {
            "available": False,
            "reason": (
                "Current Dasha period is not available."
            ),
            "indicators": [],
        }

    mahadasha = current_period.get(
        "mahadasha"
    )

    antardasha = current_period.get(
        "antardasha"
    )

    if not mahadasha or not antardasha:

        return {
            "available": False,
            "reason": (
                "Current Mahadasha or Antardasha "
                "is unavailable."
            ),
            "indicators": [],
        }

    # ---------------------------------------------------------
    # Existing 7th-house reasoning
    # ---------------------------------------------------------

    seventh_house_analysis = (
        _get_seventh_house_analysis(chart)
    )

    seventh_lord = _extract_seventh_lord(
        chart,
        seventh_house_analysis,
    )

    # ---------------------------------------------------------
    # Analyse Mahadasha
    # ---------------------------------------------------------

    mahadasha_analysis = _analyse_dasha_planet(
        chart,
        str(mahadasha),
        "Mahadasha",
        seventh_lord,
    )

    # ---------------------------------------------------------
    # Analyse Antardasha
    # ---------------------------------------------------------

    antardasha_analysis = _analyse_dasha_planet(
        chart,
        str(antardasha),
        "Antardasha",
        seventh_lord,
    )

    # ---------------------------------------------------------
    # Combine indicators
    # ---------------------------------------------------------

    indicators: list[dict[str, Any]] = []

    indicators.extend(
        mahadasha_analysis.get(
            "indicators",
            [],
        )
    )

    indicators.extend(
        antardasha_analysis.get(
            "indicators",
            [],
        )
    )

    # ---------------------------------------------------------
    # Venus combination
    # ---------------------------------------------------------

    if (
        mahadasha == "Venus"
        and antardasha == "Venus"
    ):

        indicators.append(
            {
                "factor": "venus_venus_period",
                "interpretation": (
                    "Venus is active as both Mahadasha and "
                    "Antardasha lord, creating particularly "
                    "strong activation of relationship and "
                    "partnership themes."
                ),
                "strength": 1.0,
                "type": "positive",
            }
        )

    elif (
        mahadasha == "Venus"
        or antardasha == "Venus"
    ):

        indicators.append(
            {
                "factor": "venus_dasha_activation",
                "interpretation": (
                    "Venus is active in the current Dasha "
                    "sequence. As a primary relationship "
                    "significator, this can increase the "
                    "importance of affection, attraction, "
                    "partnership and marriage-related "
                    "developments."
                ),
                "strength": 0.9,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # Double 7th-lord activation
    # ---------------------------------------------------------

    if seventh_lord:

        if (
            mahadasha == seventh_lord
            and antardasha == seventh_lord
        ):

            indicators.append(
                {
                    "factor": "seventh_lord_double_activation",
                    "interpretation": (
                        f"Both the Mahadasha and Antardasha "
                        f"lords are {seventh_lord}, the 7th lord. "
                        "This creates particularly strong "
                        "activation of marriage and partnership "
                        "matters."
                    ),
                    "strength": 1.0,
                    "type": "positive",
                }
            )

    # ---------------------------------------------------------
    # Score current period
    # ---------------------------------------------------------

    scores = _calculate_scores(
        indicators
    )

    positive_score = scores[
        "positive_score"
    ]

    theme_score = scores[
        "theme_score"
    ]

    challenge_score = scores[
        "challenge_score"
    ]

    outlook = _determine_outlook(
        positive_score,
        theme_score,
        challenge_score,
    )

    confidence = _calculate_confidence(
        positive_score,
        theme_score,
        challenge_score,
        len(indicators),
    )

    # ---------------------------------------------------------
    # Return structured result
    # ---------------------------------------------------------

    return {
        "available": True,
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "mahadasha_start": current_period.get(
            "mahadasha_start"
        ),
        "mahadasha_end": current_period.get(
            "mahadasha_end"
        ),
        "antardasha_start": current_period.get(
            "antardasha_start"
        ),
        "antardasha_end": current_period.get(
            "antardasha_end"
        ),
        "seventh_lord": seventh_lord,
        "outlook": outlook,
        "confidence": confidence,
        "scores": {
            "positive_score": positive_score,
            "theme_score": theme_score,
            "challenge_score": challenge_score,
        },
        "mahadasha_analysis": mahadasha_analysis,
        "antardasha_analysis": antardasha_analysis,
        "indicators": indicators,
    }