from typing import Any


CAREER_HOUSES = {
    2: "income and accumulated professional resources",
    6: "employment, service, competition and daily work",
    10: "career, profession, status and responsibilities",
    11: "gains, recognition, networks and professional fulfilment",
}


PLANET_CAREER_THEMES = {
    "Jupiter": (
        "growth, opportunity, guidance, expansion and professional development"
    ),
    "Saturn": (
        "responsibility, structure, persistence, delay and professional consolidation"
    ),
    "Rahu": (
        "ambition, unconventional opportunities, rapid change, technology and new professional directions"
    ),
    "Ketu": (
        "detachment, reassessment, specialisation and separation from established patterns"
    ),
    "Mercury": (
        "analysis, communication, commerce, documentation, data and intellectual work"
    ),
    "Sun": (
        "authority, leadership, visibility, recognition and professional status"
    ),
    "Mars": (
        "initiative, competition, execution, courage and decisive professional action"
    ),
    "Venus": (
        "relationships, negotiation, alliances, value creation and professional gains"
    ),
    "Moon": (
        "public interaction, adaptability, responsiveness and changing professional circumstances"
    ),
}


def _empty_scores() -> dict[str, float]:
    return {
        "career_activation": 0.0,
        "growth": 0.0,
        "transition": 0.0,
        "recognition": 0.0,
        "pressure": 0.0,
        "foreign": 0.0,
    }


def _round_scores(
    scores: dict[str, float],
) -> dict[str, float]:
    return {
        key: round(value, 2)
        for key, value in scores.items()
    }


def _add_signal(
    signals: list[dict[str, Any]],
    reasons: list[str],
    planet: str,
    house: int,
    sign: str | None,
    signal_type: str,
    weight: float,
    reason: str,
) -> None:
    signals.append(
        {
            "planet": planet,
            "house": house,
            "sign": sign,
            "type": signal_type,
            "weight": weight,
            "reason": reason,
        }
    )

    reasons.append(reason)


def analyze_career_transits(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:
    """
    Interpret current transits from a career perspective.

    This layer generates transit signals only.

    Final event timing should later combine:
        natal promise
        + Dasha activation
        + transit activation
    """

    if not isinstance(mapped_transits, dict):
        return {
            "available": False,
            "reason": "Mapped transit data is unavailable.",
        }

    if not mapped_transits.get("available"):
        return {
            "available": False,
            "reason": "Mapped transit data is unavailable.",
        }

    planets = mapped_transits.get("planets")

    if not isinstance(planets, dict):
        return {
            "available": False,
            "reason": "Transit planet data is unavailable.",
        }

    scores = _empty_scores()
    reasons: list[str] = []
    signals: list[dict[str, Any]] = []

    for planet_name, data in planets.items():

        if not isinstance(data, dict):
            continue

        natal_house = data.get("natal_house")
        sign = data.get("sign")
        retrograde = bool(
            data.get("retrograde", False)
        )

        if not isinstance(natal_house, int):
            continue

        planet_theme = PLANET_CAREER_THEMES.get(
            planet_name,
            "professional activation",
        )

        handled_specific = False

        # -------------------------------------------------
        # Jupiter
        # -------------------------------------------------

        if planet_name == "Jupiter":

            if natal_house in {2, 10, 11}:
                handled_specific = True

                scores["career_activation"] += 0.45
                scores["growth"] += 1.0

                reason = (
                    f"Jupiter transiting the natal {natal_house}th "
                    "house supports expansion, opportunity and "
                    "professional development."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Jupiter",
                    natal_house,
                    sign,
                    "growth",
                    1.0,
                    reason,
                )

            elif natal_house in {3, 6}:
                handled_specific = True

                scores["growth"] += 0.45

                reason = (
                    f"Jupiter transiting the natal {natal_house}th "
                    "house can support professional development "
                    "through effort, skills, communication or work activity."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Jupiter",
                    natal_house,
                    sign,
                    "growth",
                    0.45,
                    reason,
                )

        # -------------------------------------------------
        # Saturn
        # -------------------------------------------------

        elif planet_name == "Saturn":

            if natal_house in {6, 10, 11}:
                handled_specific = True

                scores["career_activation"] += 0.7
                scores["pressure"] += 0.5

                reason = (
                    f"Saturn transiting the natal {natal_house}th "
                    "house increases professional responsibility, "
                    "structure and the need for sustained effort."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Saturn",
                    natal_house,
                    sign,
                    "responsibility",
                    0.7,
                    reason,
                )

            elif natal_house in {8, 12}:
                handled_specific = True

                scores["transition"] += 0.6
                scores["pressure"] += 0.6

                reason = (
                    f"Saturn transiting the natal {natal_house}th "
                    "house can correspond with restructuring, "
                    "delays or a demanding transition period."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Saturn",
                    natal_house,
                    sign,
                    "transition_pressure",
                    0.6,
                    reason,
                )

        # -------------------------------------------------
        # Rahu
        # -------------------------------------------------

        elif planet_name == "Rahu":

            if natal_house == 10:
                handled_specific = True

                scores["career_activation"] += 1.1
                scores["transition"] += 0.9

                reason = (
                    "Rahu is transiting the natal 10th house, "
                    "strongly activating career direction, ambition "
                    "and the possibility of unconventional or rapid "
                    "professional developments."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Rahu",
                    10,
                    sign,
                    "career_transition",
                    1.1,
                    reason,
                )

            elif natal_house in {3, 6, 11}:
                handled_specific = True

                scores["career_activation"] += 0.5

                reason = (
                    f"Rahu transiting the natal {natal_house}th "
                    "house can intensify ambition, experimentation "
                    "and pursuit of new professional opportunities."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Rahu",
                    natal_house,
                    sign,
                    "career_activation",
                    0.5,
                    reason,
                )

            elif natal_house == 12:
                handled_specific = True

                scores["foreign"] += 0.8
                scores["transition"] += 0.5

                reason = (
                    "Rahu transiting the natal 12th house can increase "
                    "activation around foreign environments, remote work, "
                    "relocation or professional activity outside the usual setting."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Rahu",
                    12,
                    sign,
                    "foreign_transition",
                    0.8,
                    reason,
                )

        # -------------------------------------------------
        # Ketu
        # -------------------------------------------------

        elif planet_name == "Ketu":

            if natal_house == 10:
                handled_specific = True

                scores["transition"] += 1.0

                reason = (
                    "Ketu transiting the natal 10th house can increase "
                    "detachment from the existing professional direction "
                    "and encourage reassessment or specialisation."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Ketu",
                    10,
                    sign,
                    "career_reassessment",
                    1.0,
                    reason,
                )

            elif natal_house in {8, 12}:
                handled_specific = True

                scores["transition"] += 0.5

                reason = (
                    f"Ketu transiting the natal {natal_house}th "
                    "house can strengthen themes of withdrawal, "
                    "reassessment or transition."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Ketu",
                    natal_house,
                    sign,
                    "transition",
                    0.5,
                    reason,
                )

        # -------------------------------------------------
        # Sun
        # -------------------------------------------------

        elif planet_name == "Sun":

            if natal_house in {10, 11}:
                handled_specific = True

                scores["career_activation"] += 0.25
                scores["recognition"] += 0.45

                reason = (
                    f"Sun transiting the natal {natal_house}th "
                    "house can temporarily increase professional "
                    "visibility, authority or recognition."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Sun",
                    natal_house,
                    sign,
                    "recognition",
                    0.45,
                    reason,
                )

        # -------------------------------------------------
        # Mercury
        # -------------------------------------------------

        elif planet_name == "Mercury":

            if natal_house in {3, 6, 10, 11}:
                handled_specific = True

                scores["career_activation"] += 0.25

                reason = (
                    f"Mercury transiting the natal {natal_house}th "
                    "house supports professional activity involving "
                    "analysis, communication, documentation, commerce or data."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Mercury",
                    natal_house,
                    sign,
                    "career_activity",
                    0.25,
                    reason,
                )

        # -------------------------------------------------
        # Mars
        # -------------------------------------------------

        elif planet_name == "Mars":

            if natal_house in {3, 6, 10}:
                handled_specific = True

                scores["career_activation"] += 0.3

                reason = (
                    f"Mars transiting the natal {natal_house}th "
                    "house can increase initiative, competition, "
                    "execution and decisive professional action."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Mars",
                    natal_house,
                    sign,
                    "professional_action",
                    0.3,
                    reason,
                )

        # -------------------------------------------------
        # Venus
        # -------------------------------------------------

        elif planet_name == "Venus":

            if natal_house == 11:
                handled_specific = True

                scores["recognition"] += 0.35
                scores["growth"] += 0.25

                reason = (
                    "Venus transiting the natal 11th house can support "
                    "professional relationships, networks, gains and "
                    "favourable outcomes."
                )

                _add_signal(
                    signals,
                    reasons,
                    "Venus",
                    11,
                    sign,
                    "professional_gains",
                    0.35,
                    reason,
                )

        # -------------------------------------------------
        # Generic fallback
        # -------------------------------------------------

        if (
            not handled_specific
            and natal_house in CAREER_HOUSES
        ):
            scores["career_activation"] += 0.4

            reason = (
                f"{planet_name} is transiting the natal "
                f"{natal_house}th house, activating "
                f"{CAREER_HOUSES[natal_house]}. "
                f"{planet_name} carries themes of {planet_theme}."
            )

            _add_signal(
                signals,
                reasons,
                planet_name,
                natal_house,
                sign,
                "career_activation",
                0.4,
                reason,
            )

        # -------------------------------------------------
        # Retrograde modifier
        # -------------------------------------------------

        if retrograde and planet_name in {
            "Jupiter",
            "Saturn",
            "Mercury",
            "Mars",
            "Venus",
        }:

            reason = (
                f"{planet_name} is retrograde, so its current "
                "professional themes may involve review, repetition, "
                "delay or reconsideration rather than purely linear progress."
            )

            _add_signal(
                signals,
                reasons,
                planet_name,
                natal_house,
                sign,
                "retrograde_modifier",
                0.0,
                reason,
            )

    scores = _round_scores(
        scores
    )

    total_activation = round(
        scores["career_activation"]
        + scores["growth"]
        + scores["transition"]
        + scores["recognition"],
        2,
    )

    if total_activation >= 3.0:
        outlook = "strong_activation"

    elif total_activation >= 1.5:
        outlook = "supportive_activation"

    elif total_activation >= 0.5:
        outlook = "active"

    else:
        outlook = "quiet"

    return {
        "available": True,
        "moment": mapped_transits.get(
            "moment"
        ),
        "outlook": outlook,
        "total_activation": (
            total_activation
        ),
        "scores": scores,
        "signals": signals,
        "reasons": reasons,
    }