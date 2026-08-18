from __future__ import annotations

from typing import Any

from app.astrology.dignity import evaluate_planetary_dignities


# =========================================================
# HELPERS
# =========================================================

def _safe_dict(value: Any) -> dict[str, Any]:

    return value if isinstance(value, dict) else {}


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


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


def _get_house(
    chart: dict[str, Any],
    house_number: int,
) -> dict[str, Any]:

    return _safe_dict(
        _safe_dict(
            chart.get("houses")
        ).get(
            str(house_number)
        )
    )


def _get_planet(
    chart: dict[str, Any],
    planet: str | None,
) -> dict[str, Any]:

    if not planet:
        return {}

    return _safe_dict(
        _safe_dict(
            chart.get("planets")
        ).get(planet)
    )


def _planets_in_house(
    chart: dict[str, Any],
    house_number: int,
) -> list[str]:

    result = []

    for name, raw_data in _safe_dict(
        chart.get("planets")
    ).items():

        data = _safe_dict(raw_data)

        if data.get("house") == house_number:

            result.append(str(name))

    return result


# =========================================================
# SIGN APPEARANCE THEMES
# =========================================================

SIGN_THEMES = {
    "Aries": [
        "athletic or energetic appearance",
        "sharp facial features",
    ],
    "Taurus": [
        "pleasant and attractive appearance",
        "well-proportioned build",
    ],
    "Gemini": [
        "youthful appearance",
        "slim or agile build",
    ],
    "Cancer": [
        "soft facial features",
        "gentle appearance",
    ],
    "Leo": [
        "confident presence",
        "striking appearance",
    ],
    "Virgo": [
        "neat appearance",
        "slender build",
    ],
    "Libra": [
        "balanced facial features",
        "attractive appearance",
    ],
    "Scorpio": [
        "intense eyes",
        "defined facial features",
    ],
    "Sagittarius": [
        "tall or long-limbed appearance",
        "athletic build",
    ],
    "Capricorn": [
        "lean build",
        "mature appearance",
    ],
    "Aquarius": [
        "distinctive appearance",
        "tall or slender build",
    ],
    "Pisces": [
        "soft expressive eyes",
        "gentle appearance",
    ],
}


# =========================================================
# PLANET APPEARANCE THEMES
# =========================================================

PLANET_THEMES = {
    "Venus": [
        "attractive appearance",
        "pleasant facial features",
    ],
    "Jupiter": [
        "well-built frame",
        "pleasant presence",
    ],
    "Mars": [
        "athletic build",
        "defined features",
    ],
    "Mercury": [
        "youthful appearance",
        "slim build",
    ],
    "Moon": [
        "soft facial features",
        "gentle expression",
    ],
    "Sun": [
        "confident presence",
        "striking appearance",
    ],
    "Saturn": [
        "lean or slender build",
        "mature appearance",
    ],
    "Rahu": [
        "distinctive appearance",
        "unconventional features",
    ],
}


# =========================================================
# MAIN ENGINE
# =========================================================

def analyze_spouse_appearance_v1(
    chart: dict[str, Any],
) -> dict[str, Any]:

    seventh_house = _get_house(
        chart,
        7,
    )

    if not seventh_house:

        return {
            "available": False,
            "event": "spouse_appearance",
            "model_version": "v1",
            "reason": "7th house data is unavailable.",
        }

    seventh_sign = str(
        seventh_house.get(
            "sign",
            "",
        )
        or ""
    )

    seventh_lord = seventh_house.get("lord")

    seventh_lord_data = _get_planet(
        chart,
        seventh_lord,
    )

    occupants = _planets_in_house(
        chart,
        7,
    )

    dignity_map = {
        str(item.get("planet")): item
        for item in evaluate_planetary_dignities(chart)
        if isinstance(item, dict)
        and item.get("planet")
    }

    indicators = []

    # -----------------------------------------------------
    # 7TH SIGN
    # -----------------------------------------------------

    for theme in SIGN_THEMES.get(
        seventh_sign,
        [],
    ):

        indicators.append(
            {
                "factor": "seventh_house_sign",
                "strength": 0.55,
                "theme": theme,
            }
        )

    # -----------------------------------------------------
    # 7TH LORD
    # -----------------------------------------------------

    if seventh_lord:

        for theme in PLANET_THEMES.get(
            str(seventh_lord),
            [],
        ):

            indicators.append(
                {
                    "factor": "seventh_lord",
                    "strength": 0.65,
                    "theme": theme,
                }
            )

    # -----------------------------------------------------
    # PLANETS IN 7TH
    # -----------------------------------------------------

    for planet in occupants:

        for theme in PLANET_THEMES.get(
            planet,
            [],
        ):

            indicators.append(
                {
                    "factor": "planet_in_seventh",
                    "planet": planet,
                    "strength": 0.75,
                    "theme": theme,
                }
            )

    # -----------------------------------------------------
    # DIGNITY CONTEXT
    # -----------------------------------------------------

    dignity = _safe_dict(
        dignity_map.get(
            str(seventh_lord)
        )
    )

    dignity_name = dignity.get("dignity")

    if dignity_name in (
        "exalted",
        "own_sign",
    ):

        indicators.append(
            {
                "factor": "seventh_lord_dignity",
                "strength": 0.35,
                "theme": "well-presented and balanced appearance",
            }
        )

    # -----------------------------------------------------
    # AGGREGATE THEMES
    # -----------------------------------------------------

    theme_scores: dict[str, float] = {}

    for item in indicators:

        theme = str(item.get("theme"))

        theme_scores[theme] = (
            theme_scores.get(theme, 0.0)
            + _safe_float(
                item.get("strength")
            )
        )

    ranked = sorted(
        theme_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_themes = [
        theme
        for theme, _ in ranked[:5]
    ]

    confidence = _clamp(
        0.55
        + min(
            len(indicators),
            8,
        )
        * 0.04,
        0.55,
        0.88,
    )

    summary = (
        "The spouse appearance pattern is most consistent with "
        + ", ".join(top_themes[:3])
        + ". These are broad physical themes rather than exact "
        "predictions of height, complexion or facial details."
        if top_themes
        else
        "The currently modelled natal indicators do not provide "
        "strong appearance-specific themes."
    )

    return {
        "available": True,
        "event": "spouse_appearance",
        "model_version": "v1",
        "confidence": round(confidence, 3),
        "summary": summary,
        "appearance_themes": top_themes,
        "theme_scores": {
            theme: round(score, 3)
            for theme, score in ranked
        },
        "chart_context": {
            "seventh_house": {
                "sign": seventh_sign,
                "lord": seventh_lord,
                "occupants": occupants,
            },
            "seventh_lord": {
                "planet": seventh_lord,
                "house": seventh_lord_data.get("house"),
                "sign": seventh_lord_data.get("sign"),
                "dignity": dignity_name,
            },
        },
        "indicators": indicators,
    }