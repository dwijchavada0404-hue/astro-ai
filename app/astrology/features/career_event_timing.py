from typing import Any


EVENT_NAMES = {
    "job_change",
    "promotion_recognition",
    "income_gains",
    "foreign_international_opportunity",
    "career_pressure_challenge",
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
    planet: str,
) -> dict[str, Any]:
    planets = _safe_dict(
        chart.get("planets")
    )

    return _safe_dict(
        planets.get(planet)
    )


def _planet_house(
    chart: dict[str, Any],
    planet: str,
) -> int | None:
    return _planet_data(
        chart,
        planet,
    ).get("house")


def _planet_sign(
    chart: dict[str, Any],
    planet: str,
) -> str | None:
    return _planet_data(
        chart,
        planet,
    ).get("sign")


def _add_indicator(
    indicators: list[dict[str, Any]],
    event: str,
    factor: str,
    planet: str,
    strength: float,
    indicator_type: str,
    interpretation: str,
) -> None:
    indicators.append(
        {
            "event": event,
            "factor": factor,
            "planet": planet,
            "strength": strength,
            "type": indicator_type,
            "interpretation": interpretation,
        }
    )


def _get_tenth_lord(
    chart: dict[str, Any],
) -> str | None:
    houses = _safe_dict(
        chart.get("houses")
    )

    tenth = _safe_dict(
        houses.get("10")
    )

    return tenth.get("lord")


def _analyze_job_change_planet(
    chart: dict[str, Any],
    planet: str,
    role: str,
    tenth_lord: str | None,
) -> list[dict[str, Any]]:
    indicators: list[dict[str, Any]] = []

    house = _planet_house(
        chart,
        planet,
    )

    if planet == tenth_lord:
        _add_indicator(
            indicators,
            "job_change",
            f"{role}_tenth_lord",
            planet,
            0.85,
            "activation",
            (
                f"{planet} is the 10th lord. Its {role.replace('_', ' ')} "
                "activation can bring important professional decisions, "
                "restructuring or changes in career direction."
            ),
        )

    if house == 10:
        _add_indicator(
            indicators,
            "job_change",
            f"{role}_tenth_house",
            planet,
            0.75,
            "activation",
            (
                f"{planet} occupies the 10th house, making its activation "
                "highly relevant to professional role, responsibilities "
                "and changes in career direction."
            ),
        )

    if house in {3, 6, 8, 12}:
        _add_indicator(
            indicators,
            "job_change",
            f"{role}_change_house",
            planet,
            0.45,
            "transition",
            (
                f"{planet} is placed in the {house}th house, which may "
                "introduce transition, adjustment or restructuring in "
                "professional matters when activated."
            ),
        )

    if planet == "Mercury":
        _add_indicator(
            indicators,
            "job_change",
            f"{role}_mercury",
            planet,
            0.55,
            "activation",
            (
                "Mercury activation supports changes involving analytical, "
                "commercial, communication, documentation, data or "
                "information-oriented responsibilities."
            ),
        )

    if planet == "Rahu":
        _add_indicator(
            indicators,
            "job_change",
            f"{role}_rahu",
            planet,
            0.55,
            "transition",
            (
                "Rahu activation can correspond with unconventional "
                "opportunities, rapid shifts, technology-linked roles "
                "or changes from the existing professional pattern."
            ),
        )

    if planet == "Ketu":
        _add_indicator(
            indicators,
            "job_change",
            f"{role}_ketu",
            planet,
            0.45,
            "transition",
            (
                "Ketu activation can increase detachment from an existing "
                "professional setup and favour specialisation, independence "
                "or a change in work pattern."
            ),
        )

    return indicators


def _analyze_promotion_planet(
    chart: dict[str, Any],
    planet: str,
    role: str,
    tenth_lord: str | None,
) -> list[dict[str, Any]]:
    indicators: list[dict[str, Any]] = []

    house = _planet_house(
        chart,
        planet,
    )

    sign = _planet_sign(
        chart,
        planet,
    )

    if planet == tenth_lord:
        _add_indicator(
            indicators,
            "promotion_recognition",
            f"{role}_tenth_lord",
            planet,
            0.8,
            "activation",
            (
                f"{planet} is the 10th lord, making this period directly "
                "relevant to professional position and responsibilities."
            ),
        )

    if house == 10:
        _add_indicator(
            indicators,
            "promotion_recognition",
            f"{role}_tenth_house",
            planet,
            0.9,
            "positive",
            (
                f"{planet} is placed in the 10th house, strengthening "
                "career visibility and professional significance during "
                "its activation."
            ),
        )

    if house == 11:
        _add_indicator(
            indicators,
            "promotion_recognition",
            f"{role}_eleventh_house",
            planet,
            0.75,
            "positive",
            (
                f"{planet} is placed in the 11th house, supporting gains, "
                "recognition, networks and fulfilment of career objectives."
            ),
        )

    if planet == "Sun":
        _add_indicator(
            indicators,
            "promotion_recognition",
            f"{role}_sun",
            planet,
            0.65,
            "positive",
            (
                "Sun activation supports authority, leadership, visibility "
                "and professional recognition."
            ),
        )

    if planet == "Venus":
        strength = (
            0.75
            if sign == "Pisces"
            else 0.45
        )

        _add_indicator(
            indicators,
            "promotion_recognition",
            f"{role}_venus",
            planet,
            strength,
            "positive",
            (
                "Venus activation supports professional relationships, "
                "alliances, negotiation, gains and favourable outcomes."
            ),
        )

    if planet == "Mercury":
        _add_indicator(
            indicators,
            "promotion_recognition",
            f"{role}_mercury",
            planet,
            0.6,
            "positive",
            (
                "Mercury activation can improve professional visibility "
                "through analysis, communication, documentation, commerce "
                "and information handling."
            ),
        )

    return indicators


def _analyze_income_planet(
    chart: dict[str, Any],
    planet: str,
    role: str,
) -> list[dict[str, Any]]:
    indicators: list[dict[str, Any]] = []

    house = _planet_house(
        chart,
        planet,
    )

    sign = _planet_sign(
        chart,
        planet,
    )

    if house == 11:
        _add_indicator(
            indicators,
            "income_gains",
            f"{role}_eleventh_house",
            planet,
            0.8,
            "positive",
            (
                f"{planet} is placed in the 11th house, strongly linking "
                "its activation with gains, networks and fulfilment of "
                "professional objectives."
            ),
        )

    if house == 2:
        _add_indicator(
            indicators,
            "income_gains",
            f"{role}_second_house",
            planet,
            0.7,
            "positive",
            (
                f"{planet} is placed in the 2nd house, connecting its "
                "activation with income, accumulated resources and "
                "financial development."
            ),
        )

    if planet == "Venus":
        strength = (
            0.8
            if sign == "Pisces"
            else 0.45
        )

        _add_indicator(
            indicators,
            "income_gains",
            f"{role}_venus",
            planet,
            strength,
            "positive",
            (
                "Venus activation supports value creation, relationships, "
                "negotiation and favourable material outcomes."
            ),
        )

    if planet == "Jupiter":
        _add_indicator(
            indicators,
            "income_gains",
            f"{role}_jupiter",
            planet,
            0.5,
            "supportive",
            (
                "Jupiter activation can support financial growth, judgment, "
                "advisory work and expansion."
            ),
        )

    return indicators


def _analyze_foreign_planet(
    chart: dict[str, Any],
    planet: str,
    role: str,
    tenth_lord: str | None,
) -> list[dict[str, Any]]:
    indicators: list[dict[str, Any]] = []

    house = _planet_house(
        chart,
        planet,
    )

    if (
        planet == tenth_lord
        and house == 12
    ):
        _add_indicator(
            indicators,
            "foreign_international_opportunity",
            f"{role}_tenth_lord_twelfth",
            planet,
            1.0,
            "positive",
            (
                f"{planet} is the 10th lord and is placed in the "
                "12th house, directly linking career activation with "
                "international environments, large institutions, remote "
                "settings or work away from the usual environment."
            ),
        )

    elif house == 12:
        _add_indicator(
            indicators,
            "foreign_international_opportunity",
            f"{role}_twelfth_house",
            planet,
            0.65,
            "activation",
            (
                f"{planet} is placed in the 12th house, activating themes "
                "of foreign environments, large institutions, remote work, "
                "relocation or behind-the-scenes activity."
            ),
        )

    if planet == "Rahu":
        _add_indicator(
            indicators,
            "foreign_international_opportunity",
            f"{role}_rahu",
            planet,
            0.6,
            "activation",
            (
                "Rahu activation can strengthen unconventional, technology, "
                "foreign or internationally connected opportunities."
            ),
        )

    return indicators


def _analyze_pressure_planet(
    chart: dict[str, Any],
    planet: str,
    role: str,
) -> list[dict[str, Any]]:
    indicators: list[dict[str, Any]] = []

    house = _planet_house(
        chart,
        planet,
    )

    sign = _planet_sign(
        chart,
        planet,
    )

    if (
        planet == "Saturn"
        and sign == "Aries"
    ):
        _add_indicator(
            indicators,
            "career_pressure_challenge",
            f"{role}_saturn_debilitated",
            planet,
            0.9,
            "challenge",
            (
                "Saturn is debilitated in Aries. Its activation may bring "
                "heavier responsibility, delays, restructuring, pressure "
                "or the need for greater patience and maturity."
            ),
        )

    if (
        planet == "Saturn"
        and house == 12
    ):
        _add_indicator(
            indicators,
            "career_pressure_challenge",
            f"{role}_saturn_twelfth",
            planet,
            0.65,
            "challenge",
            (
                "Saturn in the 12th house can increase demanding "
                "behind-the-scenes work, institutional responsibilities "
                "or professional expenditure of time and energy."
            ),
        )

    if (
        planet == "Mars"
        and house == 12
    ):
        _add_indicator(
            indicators,
            "career_pressure_challenge",
            f"{role}_mars_twelfth",
            planet,
            0.5,
            "challenge",
            (
                "Mars in the 12th house can increase workload, hidden "
                "competition, intensity or expenditure of professional energy."
            ),
        )

    if (
        planet == "Mars"
        and sign == "Aries"
    ):
        _add_indicator(
            indicators,
            "career_pressure_challenge",
            f"{role}_mars_own_sign",
            planet,
            0.7,
            "resilience",
            (
                "Mars in its own sign Aries provides initiative and execution "
                "capacity, helping handle demanding professional periods."
            ),
        )

    return indicators


def _score_event_period(
    indicators: list[dict[str, Any]],
    event_name: str,
) -> dict[str, float]:
    positive = 0.0
    activation = 0.0
    transition = 0.0
    supportive = 0.0
    challenge = 0.0
    resilience = 0.0

    for item in indicators:
        strength = _safe_float(
            item.get("strength")
        )

        item_type = item.get("type")

        if item_type == "positive":
            positive += strength

        elif item_type == "activation":
            activation += strength

        elif item_type == "transition":
            transition += strength

        elif item_type == "supportive":
            supportive += strength

        elif item_type == "challenge":
            challenge += strength

        elif item_type == "resilience":
            resilience += strength

    if event_name == "career_pressure_challenge":
        event_score = (
            challenge
            - resilience * 0.5
        )

    elif event_name == "job_change":
        event_score = (
            positive
            + activation
            + transition * 0.8
            - challenge * 0.3
        )

    else:
        event_score = (
            positive
            + activation * 0.75
            + supportive * 0.6
            - challenge * 0.5
        )

    return {
        "positive": round(
            positive,
            2,
        ),
        "activation": round(
            activation,
            2,
        ),
        "transition": round(
            transition,
            2,
        ),
        "supportive": round(
            supportive,
            2,
        ),
        "challenge": round(
            challenge,
            2,
        ),
        "resilience": round(
            resilience,
            2,
        ),
        "event_score": round(
            max(
                0.0,
                event_score,
            ),
            2,
        ),
    }


def _classify_event_period(
    event_name: str,
    scores: dict[str, float],
) -> str:
    score = scores.get(
        "event_score",
        0.0,
    )

    if event_name == "career_pressure_challenge":
        if score >= 2.0:
            return "high_pressure"

        if score >= 1.0:
            return "elevated_pressure"

        if score >= 0.4:
            return "moderate_pressure"

        return "low_pressure"

    if score >= 2.2:
        return "strongly_supportive"

    if score >= 1.3:
        return "supportive"

    if score >= 0.6:
        return "active"

    return "weak"


def _event_indicators_for_planet(
    chart: dict[str, Any],
    event_name: str,
    planet: str,
    role: str,
    tenth_lord: str | None,
) -> list[dict[str, Any]]:
    if event_name == "job_change":
        return _analyze_job_change_planet(
            chart,
            planet,
            role,
            tenth_lord,
        )

    if event_name == "promotion_recognition":
        return _analyze_promotion_planet(
            chart,
            planet,
            role,
            tenth_lord,
        )

    if event_name == "income_gains":
        return _analyze_income_planet(
            chart,
            planet,
            role,
        )

    if event_name == "foreign_international_opportunity":
        return _analyze_foreign_planet(
            chart,
            planet,
            role,
            tenth_lord,
        )

    if event_name == "career_pressure_challenge":
        return _analyze_pressure_planet(
            chart,
            planet,
            role,
        )

    return []


def _analyze_period_for_event(
    chart: dict[str, Any],
    event_name: str,
    mahadasha: str,
    antardasha: str,
    start: Any,
    end: Any,
    tenth_lord: str | None,
) -> dict[str, Any]:
    md_indicators = _event_indicators_for_planet(
        chart,
        event_name,
        mahadasha,
        "mahadasha",
        tenth_lord,
    )

    ad_indicators = _event_indicators_for_planet(
        chart,
        event_name,
        antardasha,
        "antardasha",
        tenth_lord,
    )

    indicators = (
        md_indicators
        + ad_indicators
    )

    scores = _score_event_period(
        indicators,
        event_name,
    )

    outlook = _classify_event_period(
        event_name,
        scores,
    )

    return {
        "event": event_name,
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "period": (
            f"{mahadasha}/{antardasha}"
        ),
        "start": start,
        "end": end,
        "score": scores[
            "event_score"
        ],
        "outlook": outlook,
        "scores": scores,
        "indicators": indicators,
    }


def analyze_career_event_timing(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Rank all Vimshottari Mahadasha/Antardasha periods
    separately for each career-event category.

    Dasha dates are never recalculated here.
    They are read directly from chart["dashas"].
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
        }

    tenth_lord = _get_tenth_lord(
        chart
    )

    results: dict[
        str,
        dict[str, Any],
    ] = {}

    for event_name in EVENT_NAMES:
        periods: list[
            dict[str, Any]
        ] = []

        for md in mahadashas:
            mahadasha = md.get(
                "planet"
            )

            if not isinstance(
                mahadasha,
                str,
            ):
                continue

            antardashas = _safe_list(
                md.get(
                    "antardashas"
                )
            )

            for ad in antardashas:
                antardasha = ad.get(
                    "planet"
                )

                if not isinstance(
                    antardasha,
                    str,
                ):
                    continue

                periods.append(
                    _analyze_period_for_event(
                        chart=chart,
                        event_name=event_name,
                        mahadasha=mahadasha,
                        antardasha=antardasha,
                        start=ad.get("start"),
                        end=ad.get("end"),
                        tenth_lord=tenth_lord,
                    )
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

        results[event_name] = {
            "total_periods": len(
                periods
            ),
            "periods": periods,
            "top_periods": periods[:10],
        }

    return {
        "available": True,
        "tenth_lord": tenth_lord,
        "events": results,
    }