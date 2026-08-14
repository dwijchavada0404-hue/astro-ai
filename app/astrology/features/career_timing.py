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


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _planet_data(
    chart: dict[str, Any],
    planet_name: str,
) -> dict[str, Any]:
    planets = _safe_dict(
        chart.get("planets")
    )

    return _safe_dict(
        planets.get(planet_name)
    )


def _add_indicator(
    indicators: list[dict[str, Any]],
    factor: str,
    planet: str,
    strength: float,
    indicator_type: str,
    interpretation: str,
) -> None:
    indicators.append(
        {
            "factor": factor,
            "planet": planet,
            "strength": strength,
            "type": indicator_type,
            "interpretation": interpretation,
        }
    )


def _add_dignity_indicator(
    indicators: list[dict[str, Any]],
    planet_name: str,
    sign: str | None,
    role: str,
) -> None:
    if not sign:
        return

    dignity = PLANET_DIGNITY.get(
        planet_name,
        {},
    )

    if not dignity:
        return

    if sign == dignity.get("exalted"):

        _add_indicator(
            indicators,
            factor=f"{role}_dignity",
            planet=planet_name,
            strength=0.75,
            indicator_type="positive",
            interpretation=(
                f"{planet_name} is exalted in {sign}, "
                "supporting stronger professional expression "
                "during this period."
            ),
        )

        return

    if sign == dignity.get("debilitated"):

        _add_indicator(
            indicators,
            factor=f"{role}_dignity",
            planet=planet_name,
            strength=0.75,
            indicator_type="challenge",
            interpretation=(
                f"{planet_name} is debilitated in {sign}. "
                "Career matters may still be strongly activated, "
                "but results may require greater effort, patience, "
                "maturity or adjustment."
            ),
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
            planet=planet_name,
            strength=0.65,
            indicator_type="positive",
            interpretation=(
                f"{planet_name} is in its own sign {sign}, "
                "supporting its professional significations."
            ),
        )


def _analyze_period_planet(
    chart: dict[str, Any],
    planet_name: str,
    role: str,
    tenth_lord: str | None,
) -> list[dict[str, Any]]:
    """
    Analyse one Mahadasha or Antardasha lord
    for career relevance.
    """

    indicators: list[
        dict[str, Any]
    ] = []

    planet = _planet_data(
        chart,
        planet_name,
    )

    if not planet:
        return indicators

    house = planet.get("house")
    sign = planet.get("sign")

    # -----------------------------------------------------
    # 10TH LORD
    # -----------------------------------------------------

    if (
        tenth_lord
        and planet_name == tenth_lord
    ):

        _add_indicator(
            indicators,
            factor=f"{role}_tenth_lord",
            planet=planet_name,
            strength=1.0,
            indicator_type="positive",
            interpretation=(
                f"{planet_name} is the 10th lord, creating "
                "direct activation of career, professional "
                "direction and public responsibilities."
            ),
        )

    # -----------------------------------------------------
    # DIGNITY
    # -----------------------------------------------------

    _add_dignity_indicator(
        indicators,
        planet_name,
        sign,
        role,
    )

    # -----------------------------------------------------
    # HOUSE PLACEMENT
    # -----------------------------------------------------

    if house == 10:

        _add_indicator(
            indicators,
            factor=f"{role}_tenth_house",
            planet=planet_name,
            strength=0.9,
            indicator_type="positive",
            interpretation=(
                f"{planet_name} is placed in the 10th house, "
                "strongly activating career, public work "
                "and professional identity."
            ),
        )

    elif house == 11:

        _add_indicator(
            indicators,
            factor=f"{role}_eleventh_house",
            planet=planet_name,
            strength=0.7,
            indicator_type="positive",
            interpretation=(
                f"{planet_name} is placed in the 11th house, "
                "supporting professional gains, networks, "
                "recognition and fulfilment of career objectives."
            ),
        )

    elif house == 6:

        _add_indicator(
            indicators,
            factor=f"{role}_sixth_house",
            planet=planet_name,
            strength=0.6,
            indicator_type="positive",
            interpretation=(
                f"{planet_name} is placed in the 6th house, "
                "supporting work, service, competition, "
                "problem-solving and professional responsibilities."
            ),
        )

    elif house == 2:

        _add_indicator(
            indicators,
            factor=f"{role}_second_house",
            planet=planet_name,
            strength=0.55,
            indicator_type="positive",
            interpretation=(
                f"{planet_name} is placed in the 2nd house, "
                "connecting this period with income, resources "
                "and financial development."
            ),
        )

    elif house == 12:

        _add_indicator(
            indicators,
            factor=f"{role}_twelfth_house",
            planet=planet_name,
            strength=0.4,
            indicator_type="context",
            interpretation=(
                f"{planet_name} is placed in the 12th house, "
                "introducing themes of large institutions, "
                "foreign or international environments, remote "
                "settings, expenditure or behind-the-scenes work."
            ),
        )

    # -----------------------------------------------------
    # PLANET-SPECIFIC CAREER ACTIVATION
    # -----------------------------------------------------

    if planet_name == "Mercury":

        _add_indicator(
            indicators,
            factor=f"{role}_mercury",
            planet=planet_name,
            strength=0.55,
            indicator_type="supportive_theme",
            interpretation=(
                "Mercury activation supports analysis, "
                "communication, documentation, commerce, "
                "data and information-oriented work."
            ),
        )

    elif planet_name == "Sun":

        _add_indicator(
            indicators,
            factor=f"{role}_sun",
            planet=planet_name,
            strength=0.5,
            indicator_type="supportive_theme",
            interpretation=(
                "Sun activation supports authority, leadership, "
                "visibility and professional recognition."
            ),
        )

    elif planet_name == "Jupiter":

        _add_indicator(
            indicators,
            factor=f"{role}_jupiter",
            planet=planet_name,
            strength=0.5,
            indicator_type="supportive_theme",
            interpretation=(
                "Jupiter activation supports learning, judgment, "
                "finance, advisory responsibilities and "
                "professional expansion."
            ),
        )

    elif planet_name == "Venus":

        _add_indicator(
            indicators,
            factor=f"{role}_venus",
            planet=planet_name,
            strength=0.5,
            indicator_type="supportive_theme",
            interpretation=(
                "Venus activation supports professional "
                "relationships, negotiation, value creation, "
                "networks and gains."
            ),
        )

    elif planet_name == "Mars":

        _add_indicator(
            indicators,
            factor=f"{role}_mars",
            planet=planet_name,
            strength=0.5,
            indicator_type="supportive_theme",
            interpretation=(
                "Mars activation strengthens initiative, "
                "execution, competition, operations and "
                "action-oriented professional development."
            ),
        )

    elif planet_name == "Saturn":

        _add_indicator(
            indicators,
            factor=f"{role}_saturn",
            planet=planet_name,
            strength=0.5,
            indicator_type="supportive_theme",
            interpretation=(
                "Saturn activation emphasises responsibility, "
                "structure, governance, discipline and gradual "
                "professional development."
            ),
        )

    elif planet_name == "Rahu":

        _add_indicator(
            indicators,
            factor=f"{role}_rahu",
            planet=planet_name,
            strength=0.45,
            indicator_type="context",
            interpretation=(
                "Rahu activation may bring ambition, unusual "
                "opportunities, technology, foreign exposure "
                "or rapid professional change."
            ),
        )

    elif planet_name == "Ketu":

        _add_indicator(
            indicators,
            factor=f"{role}_ketu",
            planet=planet_name,
            strength=0.45,
            indicator_type="context",
            interpretation=(
                "Ketu activation may emphasise specialisation, "
                "research, independence, detachment from existing "
                "career patterns or behind-the-scenes work."
            ),
        )

    return indicators


def _score_indicators(
    indicators: list[dict[str, Any]],
) -> dict[str, float]:

    positive = 0.0
    supportive_theme = 0.0
    challenge = 0.0
    context = 0.0

    for indicator in indicators:

        strength = _safe_float(
            indicator.get("strength")
        )

        indicator_type = indicator.get(
            "type"
        )

        if indicator_type == "positive":
            positive += strength

        elif indicator_type == "supportive_theme":
            supportive_theme += strength

        elif indicator_type == "challenge":
            challenge += strength

        elif indicator_type == "context":
            context += strength

    return {
        "positive": round(
            positive,
            2,
        ),
        "supportive_theme": round(
            supportive_theme,
            2,
        ),
        "challenge": round(
            challenge,
            2,
        ),
        "context": round(
            context,
            2,
        ),
    }


def _calculate_period_score(
    scores: dict[str, float],
) -> float:
    """
    Calculate one ranking score.

    Positive activation matters most.

    Supportive themes add meaningful but lower-weight support.

    Challenges reduce ease of results.

    Contextual signals describe environment and therefore
    receive only a small ranking contribution.
    """

    positive = scores.get(
        "positive",
        0.0,
    )

    supportive = scores.get(
        "supportive_theme",
        0.0,
    )

    challenge = scores.get(
        "challenge",
        0.0,
    )

    context = scores.get(
        "context",
        0.0,
    )

    score = (
        positive
        + supportive * 0.75
        - challenge * 0.75
        + context * 0.15
    )

    return round(
        max(
            0.0,
            score,
        ),
        2,
    )


def _classify_period(
    score: float,
    scores: dict[str, float],
) -> str:

    positive = scores.get(
        "positive",
        0.0,
    )

    challenge = scores.get(
        "challenge",
        0.0,
    )

    if (
        score >= 1.8
        and positive >= 0.9
    ):
        return "strongly_supportive"

    if score >= 1.0:
        return "supportive"

    if (
        challenge > positive
        and challenge >= 0.7
    ):
        return "challenging"

    if score >= 0.45:
        return "mixed"

    return "weak"


def _analyze_one_period(
    chart: dict[str, Any],
    mahadasha: str,
    antardasha: str,
    start: Any,
    end: Any,
    tenth_lord: str | None,
) -> dict[str, Any]:

    md_indicators = (
        _analyze_period_planet(
            chart,
            mahadasha,
            "mahadasha",
            tenth_lord,
        )
    )

    ad_indicators = (
        _analyze_period_planet(
            chart,
            antardasha,
            "antardasha",
            tenth_lord,
        )
    )

    indicators = (
        md_indicators
        + ad_indicators
    )

    scores = _score_indicators(
        indicators
    )

    score = _calculate_period_score(
        scores
    )

    outlook = _classify_period(
        score,
        scores,
    )

    return {
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "score": score,
        "outlook": outlook,
        "scores": scores,
        "indicators": indicators,
        "start": start,
        "end": end,
    }


def analyze_career_timing(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Rank all available Vimshottari Mahadasha/Antardasha
    periods for career relevance.

    No Dasha dates are recalculated here.

    All dates come directly from chart["dashas"], which keeps
    this layer consistent with the core Dasha engine.
    """

    dashas = _safe_dict(
        chart.get("dashas")
    )

    mahadashas = _safe_list(
        dashas.get("mahadashas")
    )

    if not mahadashas:

        return {
            "available": False,
            "reason": (
                "Vimshottari Dasha periods are unavailable."
            ),
            "periods": [],
            "top_periods": [],
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

    periods: list[
        dict[str, Any]
    ] = []

    for mahadasha in mahadashas:

        md_planet = mahadasha.get(
            "planet"
        )

        if not isinstance(
            md_planet,
            str,
        ):
            continue

        antardashas = _safe_list(
            mahadasha.get(
                "antardashas"
            )
        )

        for antardasha in antardashas:

            ad_planet = antardasha.get(
                "planet"
            )

            if not isinstance(
                ad_planet,
                str,
            ):
                continue

            period = _analyze_one_period(
                chart=chart,
                mahadasha=md_planet,
                antardasha=ad_planet,
                start=antardasha.get(
                    "start"
                ),
                end=antardasha.get(
                    "end"
                ),
                tenth_lord=tenth_lord,
            )

            periods.append(
                period
            )

    periods.sort(
        key=lambda item: (
            -_safe_float(
                item.get("score")
            ),
            str(
                item.get(
                    "start",
                    "",
                )
            ),
        )
    )

    for index, period in enumerate(
        periods,
        start=1,
    ):
        period["rank"] = index

    top_periods = periods[:10]

    return {
        "available": True,
        "tenth_lord": tenth_lord,
        "total_periods": len(
            periods
        ),
        "periods": periods,
        "top_periods": top_periods,
    }