import json
from datetime import datetime
from zoneinfo import ZoneInfo

import app.services.chart_service as chart_service

from app.models.chart import BirthInput
from app.services.chart_service import build_chart

from app.astrology.features.marriage_question_intelligence_v2 import (
    analyze_marriage_question_v2,
)

from app.astrology.features.marriage_forecast_router_v2 import (
    route_marriage_question_v2,
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
# OPEN-ENDED MARRIAGE TIMING
# =========================================================

def test_open_ended_marriage_timing_uses_36_month_scan():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v2(
            "When will I get married?"
        )
    )

    result = (
        route_marriage_question_v2(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    request = (
        result[
            "resolved_forecast_request"
        ]
    )

    assert (
        request[
            "range_type"
        ]
        == "open_ended_marriage_timing_36_months"
    )

    assert (
        result[
            "forecast_available"
        ]
        is True
    )


# =========================================================
# PRIMARY WINDOW
# =========================================================

def test_open_ended_marriage_primary_window():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v2(
            "When will I get married?"
        )
    )

    result = (
        route_marriage_question_v2(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    window = (
        result[
            "primary_window"
        ]
    )

    assert (
        window[
            "start"
        ]
        == "2028-06-10"
    )

    assert (
        window[
            "end"
        ]
        == "2028-07-29"
    )

    assert (
        window[
            "peak"
        ][
            "date"
        ]
        == "2028-07-08"
    )

    assert (
        window[
            "peak"
        ][
            "confirmation"
        ]
        == "strong_confirmation"
    )


# =========================================================
# SECONDARY 2027 WINDOW
# =========================================================

def test_open_ended_marriage_secondary_2027_window():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v2(
            "When will I get married?"
        )
    )

    result = (
        route_marriage_question_v2(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    secondary = (
        result[
            "secondary_windows"
        ]
    )

    assert any(
        (
            item[
                "start"
            ]
            == "2027-02-27"
            and item[
                "end"
            ]
            == "2027-03-27"
            and item[
                "peak"
            ][
                "date"
            ]
            == "2027-03-06"
        )
        for item in secondary
    )


# =========================================================
# EXPLICIT CALENDAR YEAR
# =========================================================

def test_explicit_calendar_year_is_respected():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v2(
            "Will I marry in 2027?"
        )
    )

    result = (
        route_marriage_question_v2(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    request = (
        result[
            "resolved_forecast_request"
        ]
    )

    assert (
        request[
            "range_type"
        ]
        == "calendar_year_2027"
    )

    assert (
        request[
            "start"
        ]
        == "2027-01-01T00:00:00+05:30"
    )


# =========================================================
# EXPLICIT SIX MONTH HORIZON
# =========================================================

def test_explicit_six_month_horizon_is_respected():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v2(
            "Will I get married in the next 6 months?"
        )
    )

    result = (
        route_marriage_question_v2(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    assert (
        result[
            "resolved_forecast_request"
        ][
            "range_type"
        ]
        == "next_6_months"
    )


# =========================================================
# PROBABILITY LANGUAGE
# =========================================================

def test_open_ended_marriage_probability_language():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v2(
            "When will I get married?"
        )
    )

    result = (
        route_marriage_question_v2(
            chart,
            analysis,
            _reference_moment(),
        )
    )

    assert (
        result[
            "probability_level"
        ]
        == "likely"
    )

    assert (
        result[
            "probability_score"
        ]
        == 0.85
    )

    assert (
        result[
            "confirmation"
        ]
        == "strong_confirmation"
    )


# =========================================================
# VALIDATION
# =========================================================

def test_router_requires_timezone():

    chart = (
        _build_reference_chart()
    )

    analysis = (
        analyze_marriage_question_v2(
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

        route_marriage_question_v2(
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