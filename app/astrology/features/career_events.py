from __future__ import annotations

from typing import Any, Dict, List


def _add_indicator(
    indicators: List[Dict[str, Any]],
    event: str,
    factor: str,
    interpretation: str,
    strength: float,
    indicator_type: str,
) -> None:
    indicators.append(
        {
            "event": event,
            "factor": factor,
            "interpretation": interpretation,
            "strength": strength,
            "type": indicator_type,
        }
    )


def _planet_house(chart: Dict[str, Any], planet: str):
    planets = chart.get("planets", {})
    data = planets.get(planet, {})
    return data.get("house")


def _planet_sign(chart: Dict[str, Any], planet: str):
    planets = chart.get("planets", {})
    data = planets.get(planet, {})
    return data.get("sign")


def _score_event(indicators: List[Dict[str, Any]]) -> Dict[str, float]:
    positive = sum(
        item["strength"]
        for item in indicators
        if item["type"] == "positive"
    )

    challenge = sum(
        item["strength"]
        for item in indicators
        if item["type"] == "challenge"
    )

    theme = sum(
        item["strength"]
        for item in indicators
        if item["type"] == "theme"
    )

    return {
        "positive_score": round(positive, 2),
        "challenge_score": round(challenge, 2),
        "theme_score": round(theme, 2),
    }


def _event_outlook(scores: Dict[str, float]) -> str:
    positive = scores["positive_score"]
    challenge = scores["challenge_score"]
    theme = scores["theme_score"]

    net = positive + (theme * 0.35) - challenge

    if net >= 2.0:
        return "strongly_supportive"

    if net >= 1.0:
        return "supportive"

    if challenge > positive and challenge >= 1.0:
        return "challenging"

    return "mixed"


def analyze_career_events(chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyse natal indicators relevant to major career-event categories.

    This module does not predict exact event dates. It identifies the natal
    capacity and themes that can later be combined with dasha/timing logic.
    """

    if not chart:
        return {
            "available": False,
            "reason": "Chart data is unavailable.",
        }

    houses = chart.get("houses", {})
    planets = chart.get("planets", {})

    tenth_house = houses.get(10, houses.get("10", {}))

    if isinstance(tenth_house, dict):
        tenth_sign = tenth_house.get("sign")
        tenth_lord = tenth_house.get("lord")
        tenth_occupants = tenth_house.get("occupants", [])
    else:
        tenth_sign = None
        tenth_lord = None
        tenth_occupants = []

    # Fallback for chart structures where occupants are not embedded
    # directly in the house object.
    if not tenth_occupants:
        tenth_occupants = [
            planet
            for planet, data in planets.items()
            if isinstance(data, dict) and data.get("house") == 10
        ]

    events: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # JOB CHANGE / PROFESSIONAL TRANSITION
    # ------------------------------------------------------------------

    job_change_indicators: List[Dict[str, Any]] = []

    if tenth_lord:
        lord_house = _planet_house(chart, tenth_lord)

        if lord_house in {3, 6, 8, 12}:
            _add_indicator(
                job_change_indicators,
                "job_change",
                "tenth_lord_change_house",
                (
                    f"The 10th lord {tenth_lord} is placed in the "
                    f"{lord_house}th house, which can introduce periods of "
                    "professional transition, restructuring or changes in "
                    "work environment when activated."
                ),
                0.75,
                "theme",
            )

        if lord_house == 12:
            _add_indicator(
                job_change_indicators,
                "job_change",
                "tenth_lord_twelfth_house",
                (
                    f"The 10th lord {tenth_lord} is placed in the 12th house. "
                    "Career changes may involve leaving an existing setup, "
                    "moving toward large institutions, international exposure, "
                    "remote environments or behind-the-scenes roles."
                ),
                0.7,
                "theme",
            )

    if "Mercury" in tenth_occupants:
        _add_indicator(
            job_change_indicators,
            "job_change",
            "mercury_tenth_house",
            (
                "Mercury in the 10th house supports adaptability, learning "
                "and changes in professional responsibilities, especially "
                "toward analytical, commercial, communication or "
                "information-oriented work."
            ),
            0.6,
            "positive",
        )

    job_change_scores = _score_event(job_change_indicators)

    events["job_change"] = {
        "available": bool(job_change_indicators),
        "outlook": _event_outlook(job_change_scores),
        "scores": job_change_scores,
        "indicators": job_change_indicators,
    }

    # ------------------------------------------------------------------
    # PROMOTION / RECOGNITION
    # ------------------------------------------------------------------

    promotion_indicators: List[Dict[str, Any]] = []

    sun_house = _planet_house(chart, "Sun")

    if sun_house == 11:
        _add_indicator(
            promotion_indicators,
            "promotion",
            "sun_eleventh_house",
            (
                "The Sun in the 11th house supports professional visibility, "
                "recognition, gains through networks and fulfilment of career "
                "objectives."
            ),
            0.8,
            "positive",
        )

    if "Mercury" in tenth_occupants:
        _add_indicator(
            promotion_indicators,
            "promotion",
            "mercury_tenth_house",
            (
                "Mercury in the 10th house strengthens professional visibility "
                "through analytical ability, communication, documentation, "
                "commerce and information handling."
            ),
            0.75,
            "positive",
        )

    venus_house = _planet_house(chart, "Venus")
    venus_sign = _planet_sign(chart, "Venus")

    if venus_house == 11:
        _add_indicator(
            promotion_indicators,
            "promotion",
            "venus_eleventh_house",
            (
                "Venus in the 11th house supports professional gains, helpful "
                "networks, alliances and fulfilment of career objectives."
            ),
            0.7,
            "positive",
        )

    if venus_sign == "Pisces":
        _add_indicator(
            promotion_indicators,
            "promotion",
            "venus_exalted",
            (
                "Venus is exalted in Pisces, strengthening its capacity to "
                "support gains, relationships, negotiation and favourable "
                "professional outcomes when activated."
            ),
            0.75,
            "positive",
        )

    promotion_scores = _score_event(promotion_indicators)

    events["promotion_recognition"] = {
        "available": bool(promotion_indicators),
        "outlook": _event_outlook(promotion_scores),
        "scores": promotion_scores,
        "indicators": promotion_indicators,
    }

    # ------------------------------------------------------------------
    # INCOME / PROFESSIONAL GAINS
    # ------------------------------------------------------------------

    income_indicators: List[Dict[str, Any]] = []

    for planet in ["Sun", "Venus", "Jupiter", "Mercury"]:
        if _planet_house(chart, planet) == 11:
            _add_indicator(
                income_indicators,
                "income_gains",
                f"{planet.lower()}_eleventh_house",
                (
                    f"{planet} is placed in the 11th house, connecting its "
                    "professional significations with gains, networks and "
                    "fulfilment of objectives."
                ),
                0.65,
                "positive",
            )

    if venus_sign == "Pisces":
        _add_indicator(
            income_indicators,
            "income_gains",
            "venus_exalted",
            (
                "Exalted Venus provides additional support for gains, value "
                "creation, professional relationships and favourable material "
                "outcomes."
            ),
            0.8,
            "positive",
        )

    income_scores = _score_event(income_indicators)

    events["income_gains"] = {
        "available": bool(income_indicators),
        "outlook": _event_outlook(income_scores),
        "scores": income_scores,
        "indicators": income_indicators,
    }

    # ------------------------------------------------------------------
    # FOREIGN / INTERNATIONAL CAREER OPPORTUNITY
    # ------------------------------------------------------------------

    foreign_indicators: List[Dict[str, Any]] = []

    if tenth_lord:
        lord_house = _planet_house(chart, tenth_lord)

        if lord_house == 12:
            _add_indicator(
                foreign_indicators,
                "foreign_opportunity",
                "tenth_lord_twelfth_house",
                (
                    f"The 10th lord {tenth_lord} is placed in the 12th house, "
                    "creating a meaningful connection between career and "
                    "foreign environments, international organisations, "
                    "remote settings or work away from the usual environment."
                ),
                1.0,
                "positive",
            )

    for planet in ["Jupiter", "Mars", "Saturn"]:
        if _planet_house(chart, planet) == 12:
            _add_indicator(
                foreign_indicators,
                "foreign_opportunity",
                f"{planet.lower()}_twelfth_house",
                (
                    f"{planet} in the 12th house reinforces themes of large "
                    "institutions, international environments, remote work, "
                    "relocation or behind-the-scenes professional activity."
                ),
                0.55,
                "theme",
            )

    foreign_scores = _score_event(foreign_indicators)

    events["foreign_international_opportunity"] = {
        "available": bool(foreign_indicators),
        "outlook": _event_outlook(foreign_scores),
        "scores": foreign_scores,
        "indicators": foreign_indicators,
    }

    # ------------------------------------------------------------------
    # CAREER PRESSURE / CHALLENGE
    # ------------------------------------------------------------------

    challenge_indicators: List[Dict[str, Any]] = []

    saturn_house = _planet_house(chart, "Saturn")
    saturn_sign = _planet_sign(chart, "Saturn")

    if saturn_sign == "Aries":
        _add_indicator(
            challenge_indicators,
            "career_pressure",
            "saturn_debilitated",
            (
                "Saturn is debilitated in Aries, indicating that periods "
                "strongly activating Saturn may bring heavier responsibility, "
                "delays, pressure, restructuring or the need for patience and "
                "professional maturity."
            ),
            0.9,
            "challenge",
        )

    if saturn_house == 12:
        _add_indicator(
            challenge_indicators,
            "career_pressure",
            "saturn_twelfth_house",
            (
                "Saturn in the 12th house may create phases of demanding "
                "behind-the-scenes work, institutional pressure, isolation, "
                "international responsibilities or increased professional "
                "expenditure of time and energy."
            ),
            0.6,
            "challenge",
        )

    mars_house = _planet_house(chart, "Mars")
    mars_sign = _planet_sign(chart, "Mars")

    if mars_house == 12:
        _add_indicator(
            challenge_indicators,
            "career_pressure",
            "mars_twelfth_house",
            (
                "Mars in the 12th house can increase intensity, hidden "
                "competition, workload or expenditure of energy in "
                "professional matters."
            ),
            0.45,
            "challenge",
        )

    if mars_sign == "Aries":
        _add_indicator(
            challenge_indicators,
            "career_pressure",
            "mars_own_sign",
            (
                "Mars in its own sign Aries provides strong initiative and "
                "execution capacity, helping the chart handle demanding "
                "professional periods constructively."
            ),
            0.7,
            "positive",
        )

    challenge_scores = _score_event(challenge_indicators)

    events["career_pressure_challenge"] = {
        "available": bool(challenge_indicators),
        "outlook": _event_outlook(challenge_scores),
        "scores": challenge_scores,
        "indicators": challenge_indicators,
    }

    return {
        "available": True,
        "career_foundation": {
            "tenth_house_sign": tenth_sign,
            "tenth_lord": tenth_lord,
            "tenth_house_occupants": tenth_occupants,
        },
        "events": events,
    }