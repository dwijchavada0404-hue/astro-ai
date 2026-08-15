from fastapi.testclient import TestClient

import app.services.chart_service as chart_service

from app.main import app


# =========================================================
# TEST CLIENT
# =========================================================

client = TestClient(
    app
)


# =========================================================
# FIXED PLACE RESOLUTION
# =========================================================

def _mock_place_resolution():
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


def _request_body(
    question: str,
) -> dict:

    return {
        "birth": {
            "date": "2000-04-04",
            "time": "14:04:00",
            "place": (
                "Mumbai, Maharashtra, India"
            ),
        },
        "question": (
            question
        ),
        "reference_moment": (
            "2026-08-15T12:00:00+05:30"
        ),
    }


# =========================================================
# BASIC ENDPOINT
# =========================================================

def test_marriage_question_v2_endpoint():

    _mock_place_resolution()

    response = client.post(
        "/api/v1/marriage-question-v2",
        json=_request_body(
            "When will I get married?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data[
            "question"
        ]
        == "When will I get married?"
    )

    assert (
        data[
            "result"
        ][
            "route"
        ]
        == "single_event"
    )

    assert (
        data[
            "result"
        ][
            "event"
        ]
        == "marriage_timing"
    )


# =========================================================
# OPEN-ENDED TIMING RANGE
# =========================================================

def test_marriage_question_v2_uses_36_month_range():

    _mock_place_resolution()

    response = client.post(
        "/api/v1/marriage-question-v2",
        json=_request_body(
            "When will I get married?"
        ),
    )

    data = response.json()

    request = (
        data[
            "result"
        ][
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
        request[
            "start"
        ]
        == "2026-08-15T12:00:00+05:30"
    )


# =========================================================
# PRIMARY WINDOW REGRESSION
# =========================================================

def test_marriage_question_v2_primary_window():

    _mock_place_resolution()

    response = client.post(
        "/api/v1/marriage-question-v2",
        json=_request_body(
            "When will I get married?"
        ),
    )

    data = response.json()

    result = (
        data[
            "result"
        ]
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

    assert (
        result[
            "probability_score"
        ]
        == 0.85
    )


# =========================================================
# EXPLICIT YEAR
# =========================================================

def test_marriage_question_v2_calendar_year():

    _mock_place_resolution()

    response = client.post(
        "/api/v1/marriage-question-v2",
        json=_request_body(
            "Will I marry in 2027?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    request = (
        data[
            "result"
        ][
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
# EMPTY QUESTION
# =========================================================

def test_marriage_question_v2_rejects_empty_question():

    _mock_place_resolution()

    response = client.post(
        "/api/v1/marriage-question-v2",
        json=_request_body(
            "   "
        ),
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        "question must not be empty"
        in response.json()[
            "detail"
        ]
    )


# =========================================================
# TIMEZONE VALIDATION
# =========================================================

def test_marriage_question_v2_requires_timezone():

    _mock_place_resolution()

    body = _request_body(
        "When will I get married?"
    )

    body[
        "reference_moment"
    ] = "2026-08-15T12:00:00"

    response = client.post(
        "/api/v1/marriage-question-v2",
        json=body,
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        "timezone offset"
        in response.json()[
            "detail"
        ]
    )