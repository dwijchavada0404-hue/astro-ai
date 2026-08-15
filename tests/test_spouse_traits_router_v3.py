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

    result = (
        route_marriage_question_v3(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    return (
        analysis,
        result,
    )


# =========================================================
# PARSER → ROUTER
# =========================================================

def test_spouse_traits_parser_and_router():

    (
        analysis,
        result,
    ) = _route(
        "What will my future spouse be like?"
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "spouse_traits"
    )

    assert (
        analysis[
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        result[
            "available"
        ]
        is True
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
        == "spouse_traits"
    )


# =========================================================
# ENGINE METADATA
# =========================================================

def test_spouse_traits_router_engine_metadata():

    _, result = _route(
        "What kind of person will I marry?"
    )

    assert (
        result[
            "evidence_engine"
        ]
        == "spouse_traits_reasoning_v2"
    )

    assert (
        result[
            "forecast_type"
        ]
        == "natal_pattern"
    )

    assert (
        result[
            "model_version"
        ]
        == "v2.1"
    )

    assert (
        result[
            "confidence"
        ]
        == 0.841
    )


# =========================================================
# PROFILE SURVIVES ROUTING
# =========================================================

def test_spouse_traits_profile_survives_router():

    _, result = _route(
        "What will my future spouse be like?"
    )

    profile = (
        result[
            "profile"
        ]
    )

    assert (
        profile[
            "core_personality"
        ][:5]
        == [
            "responsible",
            "disciplined",
            "mature",
            "practical",
            "reserved",
        ]
    )

    assert (
        profile[
            "career_orientation"
        ][:2]
        == [
            "career-focused",
            "ambitious",
        ]
    )

    assert (
        profile[
            "emotional_style"
        ][:2]
        == [
            "sensitive",
            "empathetic",
        ]
    )


# =========================================================
# NO INVENTED SOCIAL BACKGROUND
# =========================================================

def test_spouse_traits_router_does_not_invent_background():

    _, result = _route(
        "Describe my future spouse."
    )

    assert (
        result[
            "profile"
        ][
            "social_background"
        ]
        == []
    )

    assert (
        result[
            "confidence_by_dimension"
        ][
            "social_background"
        ]
        == 0.0
    )


# =========================================================
# RELATIONSHIP BEHAVIOUR
# =========================================================

def test_spouse_traits_router_relationship_profile():

    _, result = _route(
        "What will my future spouse be like?"
    )

    behaviour = (
        result[
            "profile"
        ][
            "relationship_behaviour"
        ]
    )

    assert (
        "patience and adjustment"
        in behaviour
    )

    assert (
        "balancing stability with independence"
        in behaviour
    )

    assert (
        "affectionate"
        in behaviour
    )

    assert (
        "romantic"
        in behaviour
    )


# =========================================================
# BLENDED TRAITS
# =========================================================

def test_spouse_traits_router_blended_traits():

    _, result = _route(
        "What kind of personality will my spouse have?"
    )

    themes = [
        item[
            "theme"
        ]
        for item in result[
            "blended_traits"
        ]
    ]

    assert (
        "reserved_but_direct"
        in themes
    )

    assert (
        "responsible_but_independent"
        in themes
    )

    assert (
        "private_but_affectionate"
        in themes
    )


# =========================================================
# CHART CONTEXT
# =========================================================

def test_spouse_traits_router_chart_context():

    _, result = _route(
        "What will my future spouse be like?"
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
            "seventh_house"
        ][
            "occupants"
        ]
        == [
            "Ketu"
        ]
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


# =========================================================
# EVIDENCE PROVENANCE
# =========================================================

def test_spouse_traits_router_evidence_provenance():

    _, result = _route(
        "Describe my future spouse."
    )

    factors = [
        item[
            "factor"
        ]
        for item in result[
            "evidence"
        ]
    ]

    assert (
        "seventh_house_sign"
        in factors
    )

    assert (
        "seventh_lord_profile"
        in factors
    )

    assert (
        "seventh_lord_in_tenth"
        in factors
    )

    assert (
        "ketu_in_seventh"
        in factors
    )

    assert (
        "venus_exalted"
        in factors
    )


# =========================================================
# ANSWER
# =========================================================

def test_spouse_traits_router_answer():

    _, result = _route(
        "What will my future spouse be like?"
    )

    answer = (
        result[
            "answer"
        ]
    )

    assert (
        answer
        == result[
            "summary"
        ]
    )

    assert (
        "responsible"
        in answer
    )

    assert (
        "career-focused"
        in answer
    )

    assert (
        "sensitive"
        in answer
    )


# =========================================================
# FOLLOW-UP CONTEXT
# =========================================================

def test_spouse_traits_follow_up_context():

    chart = (
        _build_reference_chart()
    )

    first_analysis = (
        analyze_marriage_question_v3(
            "What will my future spouse be like?"
        )
    )

    first_result = (
        route_marriage_question_v3(
            chart,
            first_analysis,
            _reference_moment(),
        )
    )

    previous_context = {
        "question_analysis": (
            first_analysis
        ),
        "route_result": (
            first_result
        ),
    }

    follow_up_analysis = (
        analyze_marriage_question_v3(
            "What about their personality?"
        )
    )

    # Force the parser result into the conversational
    # follow-up mode expected by the router. This isolates
    # the router's context-inheritance behaviour.
    follow_up_analysis = dict(
        follow_up_analysis
    )

    follow_up_analysis[
        "query_mode"
    ] = "follow_up"

    follow_up_analysis[
        "follow_up"
    ] = {
        "is_follow_up": True,
        "requires_context": True,
    }

    result = (
        route_marriage_question_v3(
            chart,
            follow_up_analysis,
            _reference_moment(),
            previous_context=(
                previous_context
            ),
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
            "route"
        ]
        == "follow_up"
    )

    assert (
        result[
            "context_used"
        ]
        is True
    )

    assert (
        result[
            "inherited_event"
        ]
        == "spouse_traits"
    )

    assert (
        result[
            "event"
        ]
        == "spouse_traits"
    )
