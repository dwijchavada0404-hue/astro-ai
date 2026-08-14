from typing import Any


CAREER_PLANET_ROLES = {
    "Saturn": (
        "structure, responsibility, governance, discipline "
        "and long-term professional development"
    ),
    "Mercury": (
        "analysis, communication, commerce, data "
        "and documentation"
    ),
    "Sun": (
        "authority, leadership, recognition "
        "and professional visibility"
    ),
    "Jupiter": (
        "knowledge, finance, advisory work, judgment "
        "and professional expansion"
    ),
    "Mars": (
        "initiative, execution, competition, operations "
        "and technical action"
    ),
    "Venus": (
        "relationships, negotiation, value creation, "
        "networks and professional gains"
    ),
    "Rahu": (
        "ambition, unconventional opportunities, technology, "
        "foreign exposure and rapid change"
    ),
    "Ketu": (
        "specialisation, independence, detachment, research "
        "and behind-the-scenes work"
    ),
    "Moon": (
        "public interaction, adaptability, responsiveness "
        "and changing professional circumstances"
    ),
}


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


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _get_planet(
    chart: dict[str, Any],
    planet: str,
) -> dict[str, Any]:
    planets = _safe_dict(
        chart.get("planets")
    )

    return _safe_dict(
        planets.get(planet)
    )


def _add_indicator(
    indicators: list[dict[str, Any]],
    factor: str,
    planet: str,
    interpretation: str,
    strength: float,
    indicator_type: str,
) -> None:
    indicators.append(
        {
            "factor": factor,
            "planet": planet,
            "interpretation": interpretation,
            "strength": strength,
            "type": indicator_type,
        }
    )


def _add_dignity_indicator(
    indicators: list[dict[str, Any]],
    planet: str,
    sign: str | None,
    role: str,
) -> None:
    """
    Add simple dignity evidence for the active Dasha lord.

    This does not cancel career activation.
    It only describes whether results may flow more easily
    or require additional effort and adjustment.
    """

    if not sign:
        return

    dignity = PLANET_DIGNITY.get(
        planet,
        {},
    )

    if not dignity:
        return

    if sign == dignity.get("exalted"):

        _add_indicator(
            indicators,
            factor=f"{role}_dignity",
            planet=planet,
            interpretation=(
                f"{planet} is exalted in {sign}, strengthening "
                "its ability to produce its career-related "
                "results during this period."
            ),
            strength=0.75,
            indicator_type="positive",
        )

        return

    if sign == dignity.get("debilitated"):

        _add_indicator(
            indicators,
            factor=f"{role}_dignity",
            planet=planet,
            interpretation=(
                f"{planet} is debilitated in {sign}. Its period "
                "may strongly activate professional matters while "
                "also requiring greater effort, patience, maturity "
                "or adjustment."
            ),
            strength=0.75,
            indicator_type="challenge",
        )

        return

    own_signs = dignity.get(
        "own_signs",
        set(),
    )

    if sign in own_signs:

        _add_indicator(
            indicators,
            factor=f"{role}_dignity",
            planet=planet,
            interpretation=(
                f"{planet} is in its own sign {sign}, supporting "
                "its ability to express its career-related "
                "significations."
            ),
            strength=0.65,
            indicator_type="positive",
        )


def _analyze_dasha_lord(
    chart: dict[str, Any],
    planet: str,
    role: str,
    tenth_lord: str | None,
) -> list[dict[str, Any]]:
    """
    Analyse one Dasha lord for career relevance.

    This uses existing chart placements only.
    It does not calculate new astronomical data.
    """

    indicators: list[
        dict[str, Any]
    ] = []

    data = _get_planet(
        chart,
        planet,
    )

    if not data:
        return indicators

    house = data.get("house")
    sign = data.get("sign")

    role_text = CAREER_PLANET_ROLES.get(
        planet
    )

    if role_text:

        _add_indicator(
            indicators,
            factor=f"{role}_planet_role",
            planet=planet,
            interpretation=(
                f"{planet} as the {role.replace('_', ' ')} "
                f"activates themes of {role_text}."
            ),
            strength=0.35,
            indicator_type="theme",
        )

    # -----------------------------------------------------
    # PLANETARY DIGNITY
    # -----------------------------------------------------

    _add_dignity_indicator(
        indicators,
        planet,
        sign,
        role,
    )

    # -----------------------------------------------------
    # 10TH LORD ACTIVATION
    # -----------------------------------------------------

    if (
        tenth_lord
        and planet == tenth_lord
    ):

        _add_indicator(
            indicators,
            factor=f"{role}_tenth_lord",
            planet=planet,
            interpretation=(
                f"{planet} is the 10th lord, so its activation "
                "directly emphasises career, professional direction "
                "and public responsibilities."
            ),
            strength=1.0,
            indicator_type="positive",
        )

    # -----------------------------------------------------
    # CAREER HOUSES
    # -----------------------------------------------------

    if house == 10:

        _add_indicator(
            indicators,
            factor=f"{role}_tenth_house",
            planet=planet,
            interpretation=(
                f"{planet} is placed in the 10th house, making "
                "this period especially relevant to career, "
                "professional identity and public work."
            ),
            strength=0.9,
            indicator_type="positive",
        )

    elif house == 11:

        _add_indicator(
            indicators,
            factor=f"{role}_eleventh_house",
            planet=planet,
            interpretation=(
                f"{planet} is placed in the 11th house, linking "
                "this period with professional gains, networks, "
                "recognition and fulfilment of career objectives."
            ),
            strength=0.7,
            indicator_type="positive",
        )

    elif house == 6:

        _add_indicator(
            indicators,
            factor=f"{role}_sixth_house",
            planet=planet,
            interpretation=(
                f"{planet} is placed in the 6th house, activating "
                "work, service, competition, problem-solving "
                "and day-to-day professional responsibilities."
            ),
            strength=0.6,
            indicator_type="positive",
        )

    elif house == 2:

        _add_indicator(
            indicators,
            factor=f"{role}_second_house",
            planet=planet,
            interpretation=(
                f"{planet} is placed in the 2nd house, connecting "
                "the period with income, accumulated resources "
                "and financial development."
            ),
            strength=0.55,
            indicator_type="positive",
        )

    elif house == 12:

        _add_indicator(
            indicators,
            factor=f"{role}_twelfth_house",
            planet=planet,
            interpretation=(
                f"{planet} is placed in the 12th house, connecting "
                "career developments with large institutions, "
                "foreign or international environments, remote "
                "settings, expenditure or behind-the-scenes work."
            ),
            strength=0.55,
            indicator_type="theme",
        )

    # -----------------------------------------------------
    # IMPORTANT PLANET-SPECIFIC ACTIVATIONS
    # -----------------------------------------------------

    if planet == "Sun":

        _add_indicator(
            indicators,
            factor=f"{role}_sun",
            planet=planet,
            interpretation=(
                "Sun activation can increase themes of authority, "
                "leadership, visibility and recognition."
            ),
            strength=0.45,
            indicator_type="theme",
        )

    elif planet == "Mercury":

        _add_indicator(
            indicators,
            factor=f"{role}_mercury",
            planet=planet,
            interpretation=(
                "Mercury activation can strengthen analysis, "
                "communication, documentation, commerce and "
                "information-oriented professional activity."
            ),
            strength=0.45,
            indicator_type="theme",
        )

    elif planet == "Saturn":

        _add_indicator(
            indicators,
            factor=f"{role}_saturn",
            planet=planet,
            interpretation=(
                "Saturn activation emphasises responsibility, "
                "discipline, structure and gradual professional "
                "development."
            ),
            strength=0.45,
            indicator_type="theme",
        )

    elif planet == "Jupiter":

        _add_indicator(
            indicators,
            factor=f"{role}_jupiter",
            planet=planet,
            interpretation=(
                "Jupiter activation can support learning, judgment, "
                "advisory responsibilities and professional expansion."
            ),
            strength=0.45,
            indicator_type="theme",
        )

    elif planet == "Mars":

        _add_indicator(
            indicators,
            factor=f"{role}_mars",
            planet=planet,
            interpretation=(
                "Mars activation increases initiative, execution, "
                "competition and action-oriented professional themes."
            ),
            strength=0.45,
            indicator_type="theme",
        )

    elif planet == "Venus":

        _add_indicator(
            indicators,
            factor=f"{role}_venus",
            planet=planet,
            interpretation=(
                "Venus activation can support negotiation, "
                "professional relationships, networks, value "
                "creation and gains."
            ),
            strength=0.45,
            indicator_type="theme",
        )

    elif planet == "Rahu":

        _add_indicator(
            indicators,
            factor=f"{role}_rahu",
            planet=planet,
            interpretation=(
                "Rahu activation may bring ambition, unconventional "
                "career opportunities, foreign exposure, technology "
                "or rapid professional change."
            ),
            strength=0.5,
            indicator_type="theme",
        )

    elif planet == "Ketu":

        _add_indicator(
            indicators,
            factor=f"{role}_ketu",
            planet=planet,
            interpretation=(
                "Ketu activation may emphasise specialisation, "
                "independent work, research, detachment from existing "
                "professional patterns or behind-the-scenes activity."
            ),
            strength=0.5,
            indicator_type="theme",
        )

    # -----------------------------------------------------
    # SIGN CONTEXT
    # -----------------------------------------------------

    if sign:

        _add_indicator(
            indicators,
            factor=f"{role}_sign",
            planet=planet,
            interpretation=(
                f"{planet} operates from {sign} during this "
                "career analysis."
            ),
            strength=0.2,
            indicator_type="theme",
        )

    return indicators


def _calculate_scores(
    indicators: list[dict[str, Any]],
) -> dict[str, float]:

    positive_score = 0.0
    challenge_score = 0.0
    theme_score = 0.0

    for indicator in indicators:

        strength = _safe_float(
            indicator.get("strength")
        )

        indicator_type = indicator.get(
            "type"
        )

        if indicator_type == "positive":
            positive_score += strength

        elif indicator_type in {
            "challenge",
            "negative",
            "challenging",
        }:
            challenge_score += strength

        elif indicator_type == "theme":
            theme_score += strength

    return {
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
    }


def _classify_outlook(
    scores: dict[str, float],
) -> str:

    positive = scores.get(
        "positive_score",
        0.0,
    )

    challenge = scores.get(
        "challenge_score",
        0.0,
    )

    theme = scores.get(
        "theme_score",
        0.0,
    )

    net = positive - challenge

    if (
        positive >= 1.5
        and net >= 1.0
    ):
        return "strongly_supportive"

    if (
        positive >= 0.7
        and net >= 0.25
    ):
        return "supportive"

    if (
        positive > 0
        and challenge > 0
    ):
        return "mixed"

    if challenge > positive:
        return "challenging"

    if theme >= 1.0:
        return "active"

    return "neutral"


def analyze_current_dasha_for_career(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyse the chart's current Vimshottari
    Mahadasha/Antardasha for career relevance.

    The current period is read directly from chart["dashas"].
    Therefore this layer cannot independently invent or
    shift Dasha dates.
    """

    dashas = _safe_dict(
        chart.get("dashas")
    )

    current = _safe_dict(
        dashas.get("current_period")
    )

    if not current:

        return {
            "available": False,
            "reason": (
                "Current Vimshottari Dasha period "
                "is unavailable."
            ),
        }

    mahadasha = current.get(
        "mahadasha"
    )

    antardasha = current.get(
        "antardasha"
    )

    if not (
        isinstance(mahadasha, str)
        and isinstance(antardasha, str)
    ):

        return {
            "available": False,
            "reason": (
                "Current Mahadasha or Antardasha "
                "lord is unavailable."
            ),
        }

    houses = _safe_dict(
        chart.get("houses")
    )

    tenth_house = _safe_dict(
        houses.get("10")
    )

    tenth_lord = tenth_house.get(
        "lord"
    )

    md_indicators = _analyze_dasha_lord(
        chart,
        mahadasha,
        "mahadasha",
        tenth_lord,
    )

    ad_indicators = _analyze_dasha_lord(
        chart,
        antardasha,
        "antardasha",
        tenth_lord,
    )

    indicators = (
        md_indicators
        + ad_indicators
    )

    scores = _calculate_scores(
        indicators
    )

    outlook = _classify_outlook(
        scores
    )

    total_signal = (
        scores["positive_score"]
        + scores["challenge_score"]
        + scores["theme_score"]
    )

    if total_signal >= 3.0:
        confidence = 0.85

    elif total_signal >= 2.0:
        confidence = 0.8

    elif total_signal >= 1.0:
        confidence = 0.7

    elif total_signal > 0:
        confidence = 0.65

    else:
        confidence = 0.5

    return {
        "available": True,
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "mahadasha_start": current.get(
            "mahadasha_start"
        ),
        "mahadasha_end": current.get(
            "mahadasha_end"
        ),
        "antardasha_start": current.get(
            "antardasha_start"
        ),
        "antardasha_end": current.get(
            "antardasha_end"
        ),
        "tenth_lord": tenth_lord,
        "outlook": outlook,
        "confidence": confidence,
        "scores": scores,
        "mahadasha_indicators": (
            md_indicators
        ),
        "antardasha_indicators": (
            ad_indicators
        ),
        "indicators": indicators,
    }