import json

import app.services.chart_service as chart_service

from app.models.chart import BirthInput
from app.services.chart_service import build_chart

from app.astrology.features.spouse_traits_reasoning_v2 import (
    analyze_spouse_traits_v2,
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
# BASIC RESULT
# =========================================================

def test_spouse_traits_v21_reference_result():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
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
        == "spouse_traits"
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
# CORE PERSONALITY
# =========================================================

def test_spouse_traits_v21_core_personality():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
    )

    core = (
        result[
            "profile"
        ][
            "core_personality"
        ]
    )

    assert (
        core[:5]
        == [
            "responsible",
            "disciplined",
            "mature",
            "practical",
            "reserved",
        ]
    )

    assert (
        "independent"
        in core
    )

    assert (
        "direct"
        in core
    )


# =========================================================
# CAREER ORIENTATION
# =========================================================

def test_spouse_traits_v21_career_orientation():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
    )

    career = (
        result[
            "profile"
        ][
            "career_orientation"
        ]
    )

    assert (
        career[:4]
        == [
            "career-focused",
            "ambitious",
            "responsibility-oriented",
            "professionally visible",
        ]
    )

    assert (
        result[
            "confidence_by_dimension"
        ][
            "career_orientation"
        ]
        == 0.92
    )


# =========================================================
# EMOTIONAL / COMMUNICATION PROFILE
# =========================================================

def test_spouse_traits_v21_emotional_and_communication():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
    )

    emotional = (
        result[
            "profile"
        ][
            "emotional_style"
        ]
    )

    communication = (
        result[
            "profile"
        ][
            "communication_style"
        ]
    )

    assert (
        emotional
        == [
            "sensitive",
            "empathetic",
            "imaginative",
        ]
    )

    assert (
        communication
        == [
            "independent",
            "intellectual",
            "communicative",
            "analytical",
        ]
    )

    assert (
        result[
            "confidence_by_dimension"
        ][
            "emotional_style"
        ]
        == 0.6
    )

    assert (
        result[
            "confidence_by_dimension"
        ][
            "communication_style"
        ]
        == 0.6
    )


# =========================================================
# RELATIONSHIP BEHAVIOUR
# =========================================================

def test_spouse_traits_v21_relationship_behaviour():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
    )

    relationship = (
        result[
            "profile"
        ][
            "relationship_behaviour"
        ]
    )

    assert (
        relationship[:4]
        == [
            "patience and adjustment",
            "balancing stability with independence",
            "private",
            "independent",
        ]
    )

    assert (
        "affectionate"
        in relationship
    )

    assert (
        "romantic"
        in relationship
    )

    assert (
        result[
            "confidence_by_dimension"
        ][
            "relationship_behaviour"
        ]
        == 0.92
    )


# =========================================================
# UNCONVENTIONAL TRAITS
# =========================================================

def test_spouse_traits_v21_unconventional_traits():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
    )

    traits = (
        result[
            "profile"
        ][
            "unconventional_traits"
        ]
    )

    assert (
        traits
        == [
            "private",
            "independent",
            "may need personal space",
            "less conventionally expressive",
        ]
    )

    assert (
        result[
            "confidence_by_dimension"
        ][
            "unconventional_traits"
        ]
        == 0.85
    )


# =========================================================
# SOCIAL BACKGROUND SHOULD NOT BE INVENTED
# =========================================================

def test_spouse_traits_v21_social_background_not_invented():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
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
# BLENDED TRAITS
# =========================================================

def test_spouse_traits_v21_blended_traits():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
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
        themes
        == [
            "reserved_but_direct",
            "responsible_but_independent",
            "private_but_affectionate",
        ]
    )


# =========================================================
# CHART CONTEXT
# =========================================================

def test_spouse_traits_v21_chart_context():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
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
            "sign"
        ]
        == "Aries"
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
            "dignity"
        ]
        == "debilitated"
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
# SUMMARY
# =========================================================

def test_spouse_traits_v21_summary():

    chart = (
        _build_reference_chart()
    )

    result = (
        analyze_spouse_traits_v2(
            chart
        )
    )

    summary = (
        result[
            "summary"
        ]
    )

    assert (
        "responsible"
        in summary
    )

    assert (
        "career-focused"
        in summary
    )

    assert (
        "sensitive"
        in summary
    )

    assert (
        "reserved or serious exterior"
        in summary
    )


# =========================================================
# VALIDATION
# =========================================================

def test_spouse_traits_v21_requires_chart_dict():

    try:

        analyze_spouse_traits_v2(
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
