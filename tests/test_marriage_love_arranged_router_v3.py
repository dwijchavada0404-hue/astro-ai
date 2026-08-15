import json
from datetime import datetime
from zoneinfo import ZoneInfo

import app.services.chart_service as chart_service

from app.models.chart import BirthInput
from app.services.chart_service import build_chart

from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)

from app.astrology.features.marriage_forecast_router_v3 import (
    route_marriage_question_v3,
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


def _reference_moment():

    return datetime(
        2026,
        8,
        15,
        12,
        0,
        tzinfo=ZoneInfo(
            "Asia/Kolkata"
        ),
    )


def _route(
    question: str,
):

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v3(
            question
        )
    )

    return (
        analysis,
        route_marriage_question_v3(
            chart,
            analysis,
            _reference_moment(),
        ),
    )


# =========================================================
# LOVE VS ARRANGED
# =========================================================

def test_v3_love_vs_arranged_route():

    analysis, result = (
        _route(
            "Will I have a love marriage or arranged marriage?"
        )
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "love_vs_arranged"
    )

    assert (
        result[
            "route"
        ]
        == "natal_evidence"
    )

    assert (
        result[
            "event"
        ]
        == "love_vs_arranged"
    )

    assert (
        result[
            "evidence_engine"
        ]
        == "marriage_love_arranged_reasoning_v2"
    )

    assert (
        result[
            "forecast_type"
        ]
        == "natal_pattern"
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

    assert (
        result[
            "probability_level"
        ]
        == "mixed"
    )


# =========================================================
# BALANCED SCORES
# =========================================================

def test_v3_love_vs_arranged_balanced_scores():

    _, result = (
        _route(
            "Will I have a love marriage or arranged marriage?"
        )
    )

    assert (
        result[
            "love_probability"
        ]
        == 0.582
    )

    assert (
        result[
            "arranged_probability"
        ]
        == 0.418
    )

    assert (
        result[
            "scores"
        ][
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
# LOVE MARRIAGE QUESTION
# =========================================================

def test_v3_love_marriage_single_side_route():

    analysis, result = (
        _route(
            "Will I have a love marriage?"
        )
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "love_marriage"
    )

    assert (
        result[
            "event"
        ]
        == "love_marriage"
    )

    assert (
        result[
            "route"
        ]
        == "natal_evidence"
    )

    assert (
        result[
            "probability_score"
        ]
        == 0.582
    )

    assert (
        result[
            "probability_level"
        ]
        == "possible"
    )

    assert (
        result[
            "outcome"
        ]
        == "mixed_or_hybrid"
    )

    assert len(
        result[
            "relevant_indicators"
        ]
    ) >= 1

    assert (
        result[
            "relevant_indicators"
        ][
            0
        ][
            "category"
        ]
        == "love"
    )


# =========================================================
# ARRANGED MARRIAGE QUESTION
# =========================================================

def test_v3_arranged_marriage_single_side_route():

    analysis, result = (
        _route(
            "Will I have an arranged marriage?"
        )
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "arranged_marriage"
    )

    assert (
        result[
            "event"
        ]
        == "arranged_marriage"
    )

    assert (
        result[
            "route"
        ]
        == "natal_evidence"
    )

    assert (
        result[
            "probability_score"
        ]
        == 0.418
    )

    assert (
        result[
            "probability_level"
        ]
        == "less_likely"
    )

    assert (
        result[
            "outcome"
        ]
        == "mixed_or_hybrid"
    )

    assert len(
        result[
            "relevant_indicators"
        ]
    ) >= 1

    assert (
        result[
            "relevant_indicators"
        ][
            0
        ][
            "category"
        ]
        == "arranged"
    )


# =========================================================
# EVIDENCE CONTEXT
# =========================================================

def test_v3_love_arranged_preserves_evidence():

    _, result = (
        _route(
            "Will I have a love marriage or arranged marriage?"
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
# CHART CONTEXT
# =========================================================

def test_v3_love_arranged_chart_context():

    _, result = (
        _route(
            "Will I have a love marriage or arranged marriage?"
        )
    )

    context = (
        result[
            "chart_context"
        ]
    )

    assert (
        context[
            "fifth_lord"
        ][
            "planet"
        ]
        == "Mars"
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
            "planet"
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
            "fifth_seventh_connection"
        ][
            "strength"
        ]
        == 0.45
    )
