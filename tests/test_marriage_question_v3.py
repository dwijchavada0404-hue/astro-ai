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


# =========================================================
# QUESTION INTELLIGENCE REGRESSION
# =========================================================

def test_v3_year_comparison_intelligence():

    analysis = (
        analyze_marriage_question_v3(
            "Is 2027 or 2028 better for marriage?"
        )
    )

    assert (
        analysis[
            "query_mode"
        ]
        == "comparison"
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "marriage_timing"
    )

    assert (
        analysis[
            "comparison"
        ][
            "values"
        ]
        == [
            2027,
            2028,
        ]
    )


def test_v3_spouse_meeting_intelligence():

    analysis = (
        analyze_marriage_question_v3(
            "When will I meet my future spouse?"
        )
    )

    assert (
        analysis[
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "spouse_meeting"
    )

    assert (
        analysis[
            "event_count"
        ]
        == 1
    )


# =========================================================
# OPEN-ENDED MARRIAGE ROUTE
# =========================================================

def test_v3_open_ended_marriage_route():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v3(
            "When will I get married?"
        )
    )

    result = (
        route_marriage_question_v3(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    assert (
        result[
            "route"
        ]
        == "single_event"
    )

    assert (
        result[
            "event"
        ]
        == "marriage_timing"
    )

    assert (
        result[
            "primary_window"
        ][
            "peak"
        ][
            "date"
        ]
        == "2028-07-08"
    )

    assert (
        result[
            "confirmation"
        ]
        == "strong_confirmation"
    )


# =========================================================
# CALENDAR-YEAR COMPARISON
# =========================================================

def test_v3_calendar_year_comparison():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v3(
            "Is 2027 or 2028 better for marriage?"
        )
    )

    result = (
        route_marriage_question_v3(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    assert (
        result[
            "route"
        ]
        == "calendar_year_comparison"
    )

    assert (
        result[
            "event"
        ]
        == "marriage_timing"
    )

    assert (
        result[
            "years"
        ]
        == [
            2027,
            2028,
        ]
    )

    assert (
        result[
            "best_year"
        ]
        == 2027
    )

    assert (
        result[
            "comparison_strength"
        ]
        == "roughly_equal"
    )

    assert (
        result[
            "margin"
        ]
        == 0.021
    )


# =========================================================
# SPOUSE MEETING PROXY
# =========================================================

def test_v3_spouse_meeting_proxy():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v3(
            "When will I meet my future spouse?"
        )
    )

    result = (
        route_marriage_question_v3(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    assert (
        result[
            "event"
        ]
        == "spouse_meeting"
    )

    assert (
        result[
            "proxy_event"
        ]
        == "marriage_timing"
    )

    assert (
        result[
            "primary_window"
        ][
            "peak"
        ][
            "date"
        ]
        == "2028-07-08"
    )

    assert (
        result[
            "forecast_available"
        ]
        is True
    )


# =========================================================
# FOLLOW-UP REQUIRES CONTEXT
# =========================================================

def test_v3_follow_up_without_context():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v3(
            "What about 2029?"
        )
    )

    result = (
        route_marriage_question_v3(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    assert (
        result[
            "route"
        ]
        == "follow_up"
    )

    assert (
        result[
            "available"
        ]
        is False
    )

    assert (
        result[
            "requires_context"
        ]
        is True
    )

    assert (
        result[
            "context_used"
        ]
        is False
    )


# =========================================================
# FOLLOW-UP WITH CONTEXT
# =========================================================

def test_v3_follow_up_inherits_marriage_event():

    chart = (
        _build_reference_chart()
    )

    first_analysis = (
        analyze_marriage_question_v3(
            "When will I get married?"
        )
    )

    first_result = (
        route_marriage_question_v3(
            chart,
            first_analysis,
            _reference_moment(),
        )
    )

    context = {
        "question_analysis": (
            first_analysis
        ),
        "route_result": (
            first_result
        ),
    }

    follow_up_analysis = (
        analyze_marriage_question_v3(
            "What about 2029?"
        )
    )

    follow_up_result = (
        route_marriage_question_v3(
            chart,
            follow_up_analysis,
            _reference_moment(),
            previous_context=context,
        )
    )

    assert (
        follow_up_result[
            "route"
        ]
        == "follow_up"
    )

    assert (
        follow_up_result[
            "context_used"
        ]
        is True
    )

    assert (
        follow_up_result[
            "inherited_event"
        ]
        == "marriage_timing"
    )


# =========================================================
# UNSUPPORTED SPECIAL EVENT
# =========================================================

def test_v3_love_vs_arranged_is_understood_but_not_invented():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v3(
            "Will I have a love marriage or arranged marriage?"
        )
    )

    result = (
        route_marriage_question_v3(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    assert (
        result[
            "event"
        ]
        == "love_vs_arranged"
    )

    assert (
        result[
            "available"
        ]
        is False
    )

    assert (
        "dedicated evidence engine"
        in result[
            "reason"
        ]
    )


# =========================================================
# VALIDATION
# =========================================================

def test_v3_router_requires_timezone():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v3(
            "When will I get married?"
        )
    )

    naive_reference = datetime(
        2026,
        8,
        15,
        12,
        0,
    )

    try:

        route_marriage_question_v3(
            chart,
            analysis,
            naive_reference,
        )

    except ValueError as exc:

        assert (
            "timezone offset"
            in str(
                exc
            )
        )

    else:

        raise AssertionError(
            "Expected timezone validation error."
        )
