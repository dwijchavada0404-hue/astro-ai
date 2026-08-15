import json

import app.services.chart_service as chart_service

from app.models.chart import BirthInput
from app.services.chart_service import build_chart

from app.astrology.features.marriage_love_arranged_reasoning_v2 import (
    analyze_love_vs_arranged_marriage_v2,
)


# =========================================================
# HELPERS
# =========================================================

def _build_reference_chart():

    chart_service.resolve_place = lambda place: {
        "query": place,
        "resolved_name": (
            "Mumbai, Mumbai Suburban District, "
            "Maharashtra, 400051, India"
        ),
        "latitude": 19.054999,
        "longitude": 72.8692035,
        "timezone": "Asia/Kolkata",
    }

    with open(
        "test_request.json",
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(
            file
        )

    return build_chart(
        BirthInput(
            **payload
        )
    )


# =========================================================
# REFERENCE CHART RESULT
# =========================================================

def test_love_arranged_v2_reference_outcome():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_love_vs_arranged_marriage_v2(
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
        result[
            "event"
        ]
        == "love_vs_arranged"
    )

    assert (
        result[
            "model_version"
        ]
        == "v2"
    )

    assert (
        result[
            "outcome"
        ]
        == "mixed_or_hybrid"
    )

    assert (
        result[
            "label"
        ]
        == "Mixed / Hybrid Pathway"
    )


def test_love_arranged_v2_reference_scores():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_love_vs_arranged_marriage_v2(
            chart
        )
    )

    scores = (
        result[
            "scores"
        ]
    )

    assert (
        scores[
            "love_raw"
        ]
        == 0.505
    )

    assert (
        scores[
            "arranged_raw"
        ]
        == 0.2
    )

    assert (
        scores[
            "neutral_raw"
        ]
        == 1.15
    )

    assert (
        scores[
            "love_probability"
        ]
        == 0.582
    )

    assert (
        scores[
            "arranged_probability"
        ]
        == 0.418
    )

    assert (
        scores[
            "margin"
        ]
        == 0.164
    )

    assert (
        result[
            "confidence"
        ]
        == 0.642
    )


# =========================================================
# STRUCTURAL 5TH / 7TH CONNECTION
# =========================================================

def test_love_arranged_v2_fifth_seventh_connection():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_love_vs_arranged_marriage_v2(
            chart
        )
    )

    connection = (
        result[
            "chart_context"
        ][
            "fifth_seventh_connection"
        ]
    )

    assert (
        connection[
            "connected"
        ]
        is True
    )

    assert (
        connection[
            "strength"
        ]
        == 0.45
    )

    assert (
        connection[
            "types"
        ]
        == [
            "fifth_and_seventh_lords_same_house"
        ]
    )


# =========================================================
# CHART CONTEXT
# =========================================================

def test_love_arranged_v2_reference_chart_context():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_love_vs_arranged_marriage_v2(
            chart
        )
    )

    context = (
        result[
            "chart_context"
        ]
    )

    assert (
        context[
            "fifth_house"
        ][
            "lord"
        ]
        == "Mars"
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
            "fifth_lord"
        ][
            "house"
        ]
        == 10
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
            "dignity"
        ]
        == "exalted"
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
# INDICATORS
# =========================================================

def test_love_arranged_v2_reference_indicators():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_love_vs_arranged_marriage_v2(
            chart
        )
    )

    love_factors = [
        item[
            "factor"
        ]
        for item in result[
            "love_indicators"
        ]
    ]

    arranged_factors = [
        item[
            "factor"
        ]
        for item in result[
            "arranged_indicators"
        ]
    ]

    general_factors = [
        item[
            "factor"
        ]
        for item in result[
            "general_indicators"
        ]
    ]

    assert (
        "fifth_seventh_connection"
        in love_factors
    )

    assert (
        "ninth_house_tradition_emphasis"
        in arranged_factors
    )

    assert (
        "strong_venus_dignity"
        in general_factors
    )

    assert (
        "ketu_in_seventh"
        in general_factors
    )


# =========================================================
# VALIDATION
# =========================================================

def test_love_arranged_v2_requires_chart_dict():

    try:

        analyze_love_vs_arranged_marriage_v2(
            None
        )

    except ValueError as exc:

        assert (
            str(
                exc
            )
            == "chart must be a dictionary."
        )

    else:

        raise AssertionError(
            "Expected ValueError."
        )
