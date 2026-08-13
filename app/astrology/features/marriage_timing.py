from typing import Any


def _get_planet(
    chart: dict[str, Any],
    planet_name: str,
) -> dict[str, Any]:
    """Safely retrieve a planet from the chart."""

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
    """Safely retrieve a planet's house."""

    value = planet.get("house")

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_seventh_lord(
    chart: dict[str, Any],
) -> str | None:
    """
    Reuse the existing 7th-house reasoning engine to determine
    the 7th lord.
    """

    try:
        from .marriage_reasoning import analyze_seventh_house

        analysis = analyze_seventh_house(chart)

    except (ImportError, AttributeError):
        return None

    if not isinstance(analysis, dict):
        return None

    seventh_house = analysis.get(
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
        value = analysis.get(key)

        if isinstance(value, str) and value:
            return value

    return None


def _score_dasha_pair(
    chart: dict[str, Any],
    mahadasha: str,
    antardasha: str,
    seventh_lord: str | None,
) -> dict[str, Any]:
    """
    Score one Mahadasha / Antardasha combination.

    This is deliberately an evidence-based scoring layer.
    It does not declare that a particular period guarantees
    marriage.
    """

    indicators: list[dict[str, Any]] = []

    md_planet = _get_planet(
        chart,
        mahadasha,
    )

    ad_planet = _get_planet(
        chart,
        antardasha,
    )

    md_house = _get_house(md_planet)
    ad_house = _get_house(ad_planet)

    # ---------------------------------------------------------
    # Mahadasha 7th lord activation
    # ---------------------------------------------------------

    if seventh_lord == mahadasha:

        indicators.append(
            {
                "factor": "mahadasha_seventh_lord",
                "planet": mahadasha,
                "strength": 1.0,
                "type": "positive",
                "interpretation": (
                    f"Mahadasha lord {mahadasha} is the 7th lord, "
                    "creating strong activation of marriage and "
                    "partnership matters."
                ),
            }
        )

    # ---------------------------------------------------------
    # Antardasha 7th lord activation
    # ---------------------------------------------------------

    if seventh_lord == antardasha:

        indicators.append(
            {
                "factor": "antardasha_seventh_lord",
                "planet": antardasha,
                "strength": 1.0,
                "type": "positive",
                "interpretation": (
                    f"Antardasha lord {antardasha} is the 7th lord, "
                    "creating strong activation of marriage and "
                    "partnership matters."
                ),
            }
        )

    # ---------------------------------------------------------
    # Venus activation
    # ---------------------------------------------------------

    if mahadasha == "Venus":

        indicators.append(
            {
                "factor": "mahadasha_venus",
                "planet": "Venus",
                "strength": 0.9,
                "type": "positive",
                "interpretation": (
                    "Venus Mahadasha strongly activates "
                    "relationship, attraction and partnership "
                    "themes."
                ),
            }
        )

    if antardasha == "Venus":

        indicators.append(
            {
                "factor": "antardasha_venus",
                "planet": "Venus",
                "strength": 0.9,
                "type": "positive",
                "interpretation": (
                    "Venus Antardasha activates relationship, "
                    "attraction and partnership themes."
                ),
            }
        )

    # ---------------------------------------------------------
    # Jupiter activation
    # ---------------------------------------------------------

    if mahadasha == "Jupiter":

        indicators.append(
            {
                "factor": "mahadasha_jupiter",
                "planet": "Jupiter",
                "strength": 0.7,
                "type": "positive",
                "interpretation": (
                    "Jupiter Mahadasha can support growth, "
                    "commitment and stability in partnership."
                ),
            }
        )

    if antardasha == "Jupiter":

        indicators.append(
            {
                "factor": "antardasha_jupiter",
                "planet": "Jupiter",
                "strength": 0.7,
                "type": "positive",
                "interpretation": (
                    "Jupiter Antardasha can support growth, "
                    "commitment and stability in partnership."
                ),
            }
        )

    # ---------------------------------------------------------
    # 7th-house placement
    # ---------------------------------------------------------

    if md_house == 7:

        indicators.append(
            {
                "factor": "mahadasha_planet_in_seventh",
                "planet": mahadasha,
                "strength": 0.9,
                "type": "positive",
                "interpretation": (
                    f"Mahadasha lord {mahadasha} is placed in "
                    "the 7th house."
                ),
            }
        )

    if ad_house == 7:

        indicators.append(
            {
                "factor": "antardasha_planet_in_seventh",
                "planet": antardasha,
                "strength": 0.9,
                "type": "positive",
                "interpretation": (
                    f"Antardasha lord {antardasha} is placed in "
                    "the 7th house."
                ),
            }
        )

    # ---------------------------------------------------------
    # 5th house — romance
    # ---------------------------------------------------------

    if md_house == 5:

        indicators.append(
            {
                "factor": "mahadasha_planet_in_fifth",
                "planet": mahadasha,
                "strength": 0.5,
                "type": "supportive_theme",
                "interpretation": (
                    f"Mahadasha lord {mahadasha} is placed in "
                    "the 5th house, supporting romance and "
                    "emotional connection."
                ),
            }
        )

    if ad_house == 5:

        indicators.append(
            {
                "factor": "antardasha_planet_in_fifth",
                "planet": antardasha,
                "strength": 0.5,
                "type": "supportive_theme",
                "interpretation": (
                    f"Antardasha lord {antardasha} is placed in "
                    "the 5th house, supporting romance and "
                    "emotional connection."
                ),
            }
        )

    # ---------------------------------------------------------
    # 11th house — fulfilment
    # ---------------------------------------------------------

    if md_house == 11:

        indicators.append(
            {
                "factor": "mahadasha_planet_in_eleventh",
                "planet": mahadasha,
                "strength": 0.5,
                "type": "supportive_theme",
                "interpretation": (
                    f"Mahadasha lord {mahadasha} is placed in "
                    "the 11th house, supporting fulfilment "
                    "and relationship gains."
                ),
            }
        )

    if ad_house == 11:

        indicators.append(
            {
                "factor": "antardasha_planet_in_eleventh",
                "planet": antardasha,
                "strength": 0.5,
                "type": "supportive_theme",
                "interpretation": (
                    f"Antardasha lord {antardasha} is placed in "
                    "the 11th house, supporting fulfilment "
                    "and relationship gains."
                ),
            }
        )

    # ---------------------------------------------------------
    # 12th house — distance / relocation
    # ---------------------------------------------------------

    if md_house == 12:

        indicators.append(
            {
                "factor": "mahadasha_planet_in_twelfth",
                "planet": mahadasha,
                "strength": 0.3,
                "type": "context",
                "interpretation": (
                    f"Mahadasha lord {mahadasha} is placed in "
                    "the 12th house, introducing themes of "
                    "distance, relocation, privacy or foreign "
                    "environments."
                ),
            }
        )

    if ad_house == 12:

        indicators.append(
            {
                "factor": "antardasha_planet_in_twelfth",
                "planet": antardasha,
                "strength": 0.3,
                "type": "context",
                "interpretation": (
                    f"Antardasha lord {antardasha} is placed in "
                    "the 12th house, introducing themes of "
                    "distance, relocation, privacy or foreign "
                    "environments."
                ),
            }
        )

    # ---------------------------------------------------------
    # Calculate score
    # ---------------------------------------------------------

    positive_score = sum(
        float(i["strength"])
        for i in indicators
        if i["type"] == "positive"
    )

    supportive_score = sum(
        float(i["strength"])
        for i in indicators
        if i["type"] == "supportive_theme"
    )

    context_score = sum(
        float(i["strength"])
        for i in indicators
        if i["type"] == "context"
    )

    # Strong activations are deliberately capped.
    positive_score = min(
        round(positive_score, 2),
        2.0,
    )

    supportive_score = min(
        round(supportive_score, 2),
        1.0,
    )

    context_score = min(
        round(context_score, 2),
        1.0,
    )

    # ---------------------------------------------------------
    # Overall score
    # ---------------------------------------------------------

    overall_score = (
        positive_score
        + supportive_score
        - (context_score * 0.25)
    )

    overall_score = max(
        round(overall_score, 2),
        0.0,
    )

    # ---------------------------------------------------------
    # Outlook
    # ---------------------------------------------------------

    if overall_score >= 1.5:
        outlook = "strongly_supportive"

    elif overall_score >= 0.8:
        outlook = "supportive"

    elif overall_score >= 0.4:
        outlook = "mixed"

    else:
        outlook = "weak"

    return {
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "score": overall_score,
        "outlook": outlook,
        "scores": {
            "positive": positive_score,
            "supportive_theme": supportive_score,
            "context": context_score,
        },
        "indicators": indicators,
    }


def _get_all_dasha_periods(
    chart: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return all Mahadasha / Antardasha combinations."""

    dashas = chart.get(
        "dashas",
        {},
    )

    if not isinstance(dashas, dict):
        return []

    mahadashas = dashas.get(
        "mahadashas",
        [],
    )

    if not isinstance(mahadashas, list):
        return []

    periods: list[dict[str, Any]] = []

    for md in mahadashas:

        if not isinstance(md, dict):
            continue

        mahadasha = md.get("planet")

        if not isinstance(mahadasha, str):
            continue

        antardashas = md.get(
            "antardashas",
            [],
        )

        if not isinstance(antardashas, list):
            continue

        for ad in antardashas:

            if not isinstance(ad, dict):
                continue

            antardasha = ad.get("planet")

            if not isinstance(antardasha, str):
                continue

            periods.append(
                {
                    "mahadasha": mahadasha,
                    "antardasha": antardasha,
                    "start": ad.get("start"),
                    "end": ad.get("end"),
                }
            )

    return periods


def analyze_marriage_timing(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyse all available Vimshottari Mahadasha /
    Antardasha periods and rank them for marriage relevance.
    """

    periods = _get_all_dasha_periods(
        chart
    )

    if not periods:

        return {
            "available": False,
            "reason": (
                "Dasha periods are not available."
            ),
            "periods": [],
        }

    seventh_lord = _extract_seventh_lord(
        chart
    )

    scored_periods: list[dict[str, Any]] = []

    for period in periods:

        result = _score_dasha_pair(
            chart,
            period["mahadasha"],
            period["antardasha"],
            seventh_lord,
        )

        result.update(
            {
                "start": period.get("start"),
                "end": period.get("end"),
            }
        )

        scored_periods.append(
            result
        )

    # ---------------------------------------------------------
    # Rank periods
    # ---------------------------------------------------------

    ranked_periods = sorted(
        scored_periods,
        key=lambda item: item.get(
            "score",
            0.0,
        ),
        reverse=True,
    )

    # Add rank after sorting.
    for index, period in enumerate(
        ranked_periods,
        start=1,
    ):
        period["rank"] = index

    return {
        "available": True,
        "seventh_lord": seventh_lord,
        "total_periods": len(ranked_periods),
        "periods": ranked_periods,
        "top_periods": ranked_periods[:5],
    }