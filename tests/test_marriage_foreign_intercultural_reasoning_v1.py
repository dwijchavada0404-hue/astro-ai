from __future__ import annotations

import pytest

from app.astrology.features.marriage_foreign_intercultural_reasoning_v1 import (
    analyze_foreign_intercultural_relationship_v1,
)


# =========================================================
# REFERENCE CHART
# =========================================================

def _reference_chart() -> dict:

    return {
        "houses": {
            "5": {
                "sign": "Scorpio",
                "lord": "Mars",
            },
            "7": {
                "sign": "Capricorn",
                "lord": "Saturn",
            },
            "9": {
                "sign": "Pisces",
                "lord": "Jupiter",
            },
            "12": {
                "sign": "Gemini",
                "lord": "Mercury",
            },
        },
        "planets": {
            "Sun": {
                "sign": "Pisces",
                "house": 9,
            },
            "Moon": {
                "sign": "Pisces",
                "house": 9,
            },
            "Mars": {
                "sign": "Aries",
                "house": 10,
            },
            "Mercury": {
                "sign": "Aquarius",
                "house": 8,
            },
            "Jupiter": {
                "sign": "Aries",
                "house": 10,
            },
            "Venus": {
                "sign": "Pisces",
                "house": 9,
            },
            "Saturn": {
                "sign": "Aries",
                "house": 10,
            },
            "Rahu": {
                "sign": "Cancer",
                "house": 1,
            },
            "Ketu": {
                "sign": "Capricorn",
                "house": 7,
            },
        },
    }


# =========================================================
# BASIC VALIDATION
# =========================================================

def test_foreign_intercultural_requires_chart_dict():

    with pytest.raises(
        ValueError
    ):

        analyze_foreign_intercultural_relationship_v1(
            None
        )


def test_foreign_intercultural_requires_seventh_house():

    chart = (
        _reference_chart()
    )

    chart[
        "houses"
    ].pop(
        "7"
    )

    result = (
        analyze_foreign_intercultural_relationship_v1(
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
        == "foreign_intercultural_connection"
    )


# =========================================================
# REFERENCE CHART OUTPUT
# =========================================================

def test_foreign_intercultural_reference_chart_available():

    result = (
        analyze_foreign_intercultural_relationship_v1(
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
        == "foreign_intercultural_connection"
    )

    assert (
        result[
            "model_version"
        ]
        == "v1"
    )

    assert (
        0.0
        <= result[
            "support_score"
        ]
        <= 1.0
    )

    assert (
        0.50
        <= result[
            "confidence"
        ]
        <= 0.88
    )


def test_foreign_intercultural_reference_chart_has_context():

    result = (
        analyze_foreign_intercultural_relationship_v1(
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
            "venus"
        ][
            "house"
        ]
        == 9
    )

    assert (
        context[
            "ketu"
        ][
            "house"
        ]
        == 7
    )


# =========================================================
# REFERENCE INDICATORS
# =========================================================

def test_foreign_intercultural_reference_chart_indicators():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _reference_chart()
        )
    )

    factors = {
        item[
            "factor"
        ]
        for item in result[
            "indicators"
        ]
    }

    assert (
        "venus_in_foreign_house"
        in factors
    )

    assert (
        "seventh_house_movable_sign"
        in factors
    )

    assert (
        "ketu_in_seventh"
        in factors
    )


# =========================================================
# STRONG FOREIGN PATTERN
# =========================================================

def _strong_foreign_chart() -> dict:

    chart = (
        _reference_chart()
    )

    chart[
        "planets"
    ][
        "Saturn"
    ] = {
        "sign": "Gemini",
        "house": 12,
    }

    chart[
        "planets"
    ][
        "Mercury"
    ] = {
        "sign": "Gemini",
        "house": 12,
    }

    chart[
        "planets"
    ][
        "Rahu"
    ] = {
        "sign": "Capricorn",
        "house": 7,
    }

    chart[
        "planets"
    ][
        "Ketu"
    ] = {
        "sign": "Cancer",
        "house": 1,
    }

    return (
        chart
    )


def test_foreign_intercultural_strong_chart():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _strong_foreign_chart()
        )
    )

    assert (
        result[
            "support_score"
        ]
        >= 0.78
    )

    assert (
        result[
            "outcome"
        ]
        == "strongly_supported"
    )

    assert (
        result[
            "label"
        ]
        == "Strong Foreign / Intercultural Potential"
    )


def test_foreign_intercultural_strong_primary_evidence():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _strong_foreign_chart()
        )
    )

    factors = {
        item[
            "factor"
        ]
        for item in result[
            "primary_indicators"
        ]
    }

    assert (
        "seventh_lord_in_foreign_house"
        in factors
    )

    assert (
        "rahu_in_seventh"
        in factors
    )

    assert (
        "seventh_lord_rahu_connection"
        in factors
        or
        "seventh_twelfth_connection"
        in factors
    )


# =========================================================
# MODERATE FOREIGN PATTERN
# =========================================================

def _moderate_foreign_chart() -> dict:

    chart = (
        _reference_chart()
    )

    chart[
        "planets"
    ][
        "Saturn"
    ] = {
        "sign": "Pisces",
        "house": 9,
    }

    chart[
        "planets"
    ][
        "Rahu"
    ] = {
        "sign": "Cancer",
        "house": 1,
    }

    return (
        chart
    )


def test_foreign_intercultural_moderate_chart():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _moderate_foreign_chart()
        )
    )

    assert (
        result[
            "support_score"
        ]
        >= 0.40
    )

    assert (
        result[
            "outcome"
        ]
        in (
            "supported",
            "mixed",
            "strongly_supported",
        )
    )


# =========================================================
# WEAK FOREIGN PATTERN
# =========================================================

def _weak_foreign_chart() -> dict:

    return {
        "houses": {
            "5": {
                "sign": "Taurus",
                "lord": "Venus",
            },
            "7": {
                "sign": "Leo",
                "lord": "Sun",
            },
            "9": {
                "sign": "Aries",
                "lord": "Mars",
            },
            "12": {
                "sign": "Cancer",
                "lord": "Moon",
            },
        },
        "planets": {
            "Sun": {
                "sign": "Leo",
                "house": 2,
            },
            "Moon": {
                "sign": "Cancer",
                "house": 3,
            },
            "Mars": {
                "sign": "Virgo",
                "house": 4,
            },
            "Mercury": {
                "sign": "Virgo",
                "house": 4,
            },
            "Jupiter": {
                "sign": "Taurus",
                "house": 5,
            },
            "Venus": {
                "sign": "Taurus",
                "house": 5,
            },
            "Saturn": {
                "sign": "Virgo",
                "house": 4,
            },
            "Rahu": {
                "sign": "Virgo",
                "house": 4,
            },
            "Ketu": {
                "sign": "Pisces",
                "house": 10,
            },
        },
    }


def test_foreign_intercultural_weak_chart():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _weak_foreign_chart()
        )
    )

    assert (
        result[
            "support_score"
        ]
        < 0.40
    )

    assert (
        result[
            "outcome"
        ]
        == "weakly_supported"
    )


# =========================================================
# RELATIONSHIP-SPECIFIC CAP
# =========================================================

def test_foreign_intercultural_general_foreign_factors_do_not_overstate():

    chart = (
        _weak_foreign_chart()
    )

    chart[
        "planets"
    ][
        "Venus"
    ] = {
        "sign": "Pisces",
        "house": 9,
    }

    chart[
        "planets"
    ][
        "Jupiter"
    ] = {
        "sign": "Pisces",
        "house": 9,
    }

    chart[
        "planets"
    ][
        "Rahu"
    ] = {
        "sign": "Gemini",
        "house": 12,
    }

    result = (
        analyze_foreign_intercultural_relationship_v1(
            chart
        )
    )

    assert (
        result[
            "support_score"
        ]
        <= 0.52
    )


# =========================================================
# STRUCTURE
# =========================================================

def test_foreign_intercultural_score_payload():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _reference_chart()
        )
    )

    scores = (
        result[
            "scores"
        ]
    )

    assert (
        "primary_raw"
        in scores
    )

    assert (
        "secondary_raw"
        in scores
    )

    assert (
        "context_raw"
        in scores
    )

    assert (
        "support_score"
        in scores
    )


def test_foreign_intercultural_indicator_categories():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _reference_chart()
        )
    )

    for item in result[
        "indicators"
    ]:

        assert (
            item[
                "category"
            ]
            in (
                "primary",
                "secondary",
                "context",
            )
        )

        assert (
            0.0
            <= item[
                "strength"
            ]
            <= 1.0
        )


def test_foreign_intercultural_summary_present():

    result = (
        analyze_foreign_intercultural_relationship_v1(
            _reference_chart()
        )
    )

    assert (
        isinstance(
            result[
                "summary"
            ],
            str,
        )
    )

    assert (
        result[
            "summary"
        ]
    )
