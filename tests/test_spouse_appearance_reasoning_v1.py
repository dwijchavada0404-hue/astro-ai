from __future__ import annotations

from typing import Any

from app.astrology.features.spouse_appearance_reasoning_v1 import (
    analyze_spouse_appearance_v1,
)


# =========================================================
# REFERENCE CHART
# =========================================================

def _reference_chart() -> dict[str, Any]:

    return {
        "houses": {
            "1": {
                "sign": "Cancer",
                "lord": "Moon",
            },
            "2": {
                "sign": "Leo",
                "lord": "Sun",
            },
            "3": {
                "sign": "Virgo",
                "lord": "Mercury",
            },
            "4": {
                "sign": "Libra",
                "lord": "Venus",
            },
            "5": {
                "sign": "Scorpio",
                "lord": "Mars",
            },
            "6": {
                "sign": "Sagittarius",
                "lord": "Jupiter",
            },
            "7": {
                "sign": "Capricorn",
                "lord": "Saturn",
            },
            "8": {
                "sign": "Aquarius",
                "lord": "Saturn",
            },
            "9": {
                "sign": "Pisces",
                "lord": "Jupiter",
            },
            "10": {
                "sign": "Aries",
                "lord": "Mars",
            },
            "11": {
                "sign": "Taurus",
                "lord": "Venus",
            },
            "12": {
                "sign": "Gemini",
                "lord": "Mercury",
            },
        },

        "planets": {
            "Sun": {
                "house": 9,
                "sign": "Pisces",
            },
            "Moon": {
                "house": 9,
                "sign": "Pisces",
            },
            "Mars": {
                "house": 10,
                "sign": "Aries",
            },
            "Mercury": {
                "house": 8,
                "sign": "Aquarius",
            },
            "Jupiter": {
                "house": 10,
                "sign": "Aries",
            },
            "Venus": {
                "house": 9,
                "sign": "Pisces",
            },
            "Saturn": {
                "house": 10,
                "sign": "Aries",
            },
            "Rahu": {
                "house": 1,
                "sign": "Cancer",
            },
            "Ketu": {
                "house": 7,
                "sign": "Capricorn",
            },
        },
    }


# =========================================================
# BASIC CONTRACT
# =========================================================

def test_spouse_appearance_v1_basic_contract():

    result = (
        analyze_spouse_appearance_v1(
            _reference_chart()
        )
    )

    assert (
        result[
            "available"
        ]
        is True
    )

    assert (
        result[
            "event"
        ]
        == "spouse_appearance"
    )

    assert (
        result[
            "model_version"
        ]
        == "v1"
    )

    assert isinstance(
        result[
            "confidence"
        ],
        float,
    )

    assert (
        0.55
        <= result[
            "confidence"
        ]
        <= 0.88
    )

    assert isinstance(
        result[
            "summary"
        ],
        str,
    )

    assert (
        result[
            "summary"
        ]
    )


# =========================================================
# CAPRICORN 7TH HOUSE THEMES
# =========================================================

def test_spouse_appearance_v1_capricorn_sign_themes():

    result = (
        analyze_spouse_appearance_v1(
            _reference_chart()
        )
    )

    themes = set(
        result[
            "appearance_themes"
        ]
    )

    assert (
        "lean build"
        in themes
        or "mature appearance"
        in themes
    )


# =========================================================
# SATURN LORD THEMES
# =========================================================

def test_spouse_appearance_v1_saturn_lord_themes():

    result = (
        analyze_spouse_appearance_v1(
            _reference_chart()
        )
    )

    indicators = (
        result[
            "indicators"
        ]
    )

    assert any(
        (
            item.get(
                "factor"
            )
            == "seventh_lord"
            and item.get(
                "theme"
            )
            in (
                "lean or slender build",
                "mature appearance",
            )
        )
        for item in indicators
    )


# =========================================================
# KETU IN SEVENTH DOES NOT CRASH
# =========================================================

def test_spouse_appearance_v1_ketu_in_seventh_supported_safely():

    result = (
        analyze_spouse_appearance_v1(
            _reference_chart()
        )
    )

    assert (
        result[
            "available"
        ]
        is True
    )

    assert isinstance(
        result[
            "indicators"
        ],
        list,
    )


# =========================================================
# THEME SCORES
# =========================================================

def test_spouse_appearance_v1_theme_scores_are_ranked():

    result = (
        analyze_spouse_appearance_v1(
            _reference_chart()
        )
    )

    scores = (
        result[
            "theme_scores"
        ]
    )

    assert isinstance(
        scores,
        dict,
    )

    values = list(
        scores.values()
    )

    assert (
        values
        == sorted(
            values,
            reverse=True,
        )
    )


# =========================================================
# CHART CONTEXT
# =========================================================

def test_spouse_appearance_v1_chart_context():

    result = (
        analyze_spouse_appearance_v1(
            _reference_chart()
        )
    )

    context = (
        result[
            "chart_context"
        ]
    )

    assert (
        context[
            "seventh_house"
        ][
            "sign"
        ]
        == "Capricorn"
    )

    assert (
        context[
            "seventh_house"
        ][
            "lord"
        ]
        == "Saturn"
    )

    assert (
        context[
            "seventh_lord"
        ][
            "house"
        ]
        == 10
    )

    assert (
        context[
            "seventh_lord"
        ][
            "sign"
        ]
        == "Aries"
    )


# =========================================================
# MISSING 7TH HOUSE
# =========================================================

def test_spouse_appearance_v1_missing_seventh_house():

    chart = {
        "houses": {},
        "planets": {},
    }

    result = (
        analyze_spouse_appearance_v1(
            chart
        )
    )

    assert (
        result[
            "available"
        ]
        is False
    )

    assert (
        result[
            "event"
        ]
        == "spouse_appearance"
    )

    assert (
        result[
            "model_version"
        ]
        == "v1"
    )

    assert (
        result[
            "reason"
        ]
        == "7th house data is unavailable."
    )


# =========================================================
# EMPTY PLANETS STILL WORK
# =========================================================

def test_spouse_appearance_v1_empty_planets_still_returns_sign_profile():

    chart = (
        _reference_chart()
    )

    chart[
        "planets"
    ] = {}

    result = (
        analyze_spouse_appearance_v1(
            chart
        )
    )

    assert (
        result[
            "available"
        ]
        is True
    )

    assert (
        "lean build"
        in result[
            "appearance_themes"
        ]
    )

    assert (
        "mature appearance"
        in result[
            "appearance_themes"
        ]
    )


# =========================================================
# VENUS OCCUPANT
# =========================================================

def test_spouse_appearance_v1_venus_in_seventh_adds_attractive_theme():

    chart = (
        _reference_chart()
    )

    chart[
        "planets"
    ][
        "Venus"
    ][
        "house"
    ] = 7

    chart[
        "planets"
    ][
        "Venus"
    ][
        "sign"
    ] = "Capricorn"

    result = (
        analyze_spouse_appearance_v1(
            chart
        )
    )

    indicators = (
        result[
            "indicators"
        ]
    )

    assert any(
        (
            item.get(
                "factor"
            )
            == "planet_in_seventh"
            and item.get(
                "planet"
            )
            == "Venus"
            and item.get(
                "theme"
            )
            == "attractive appearance"
        )
        for item in indicators
    )


# =========================================================
# MARS OCCUPANT
# =========================================================

def test_spouse_appearance_v1_mars_in_seventh_adds_athletic_theme():

    chart = (
        _reference_chart()
    )

    chart[
        "planets"
    ][
        "Mars"
    ][
        "house"
    ] = 7

    chart[
        "planets"
    ][
        "Mars"
    ][
        "sign"
    ] = "Capricorn"

    result = (
        analyze_spouse_appearance_v1(
            chart
        )
    )

    indicators = (
        result[
            "indicators"
        ]
    )

    assert any(
        (
            item.get(
                "factor"
            )
            == "planet_in_seventh"
            and item.get(
                "planet"
            )
            == "Mars"
            and item.get(
                "theme"
            )
            == "athletic build"
        )
        for item in indicators
    )