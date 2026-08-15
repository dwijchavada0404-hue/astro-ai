from fastapi.testclient import TestClient

import app.services.chart_service as chart_service
from app.main import app


client = TestClient(app)


def _mock_resolve_place(place: str) -> dict:
    return {
        "query": place,
        "resolved_name": (
            "Mumbai, Mumbai Suburban District, "
            "Maharashtra, 400051, India"
        ),
        "latitude": 19.054999,
        "longitude": 72.8692035,
        "timezone": "Asia/Kolkata",
    }


def _payload(question: str) -> dict:
    return {
        "birth": {
            "date": "2000-04-04",
            "time": "14:04:00",
            "place": "Mumbai, Maharashtra, India",
        },
        "question": question,
        "reference_moment": "2026-08-15T12:00:00+05:30",
    }


def test_marriage_question_v3_open_ended_timing(
    monkeypatch,
):
    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "When will I get married?"
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["understanding"]["primary_event"]
        == "marriage_timing"
    )

    assert (
        body["understanding"]["query_mode"]
        == "single_event"
    )

    result = body["result"]

    assert result["available"] is True
    assert result["route"] == "single_event"
    assert result["event"] == "marriage_timing"

    assert (
        result["resolved_forecast_request"]["range_type"]
        == "open_ended_marriage_timing_36_months"
    )

    assert result["forecast_available"] is True

    assert (
        result["primary_window"]["peak"]["date"]
        == "2028-07-08"
    )


def test_marriage_question_v3_year_comparison(
    monkeypatch,
):
    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "Is 2027 or 2028 better for marriage?"
        ),
    )

    assert response.status_code == 200

    body = response.json()

    understanding = body["understanding"]

    assert (
        understanding["query_mode"]
        == "comparison"
    )

    assert (
        understanding["primary_event"]
        == "marriage_timing"
    )

    assert (
        understanding["comparison"]["values"]
        == [2027, 2028]
    )

    result = body["result"]

    assert (
        result["route"]
        == "calendar_year_comparison"
    )

    assert result["years"] == [2027, 2028]

    assert result["best_year"] == 2027

    assert (
        result["comparison_strength"]
        == "roughly_equal"
    )

    assert len(
        result["ranked_results"]
    ) == 2


def test_marriage_question_v3_spouse_meeting_dedicated_engine(
    monkeypatch,
):
    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "When will I meet my future spouse?"
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["understanding"]["primary_event"]
        == "spouse_meeting"
    )

    assert (
        body["understanding"]["query_mode"]
        == "single_event"
    )

    result = body["result"]

    assert result["available"] is True

    assert (
        result["event"]
        == "spouse_meeting"
    )

    assert (
        result["forecast_engine"]
        == "spouse_meeting_forecast_v2"
    )

    assert (
        result["resolved_forecast_request"]["range_type"]
        == "open_ended_spouse_meeting_36_months"
    )

    assert (
        result["primary_window"]["start"]
        == "2027-01-30"
    )

    assert (
        result["primary_window"]["end"]
        == "2027-04-03"
    )

    assert (
        result["primary_window"]["peak"]["date"]
        == "2027-03-06"
    )

    assert (
        result["primary_window"]["peak"]["score"]
        == 0.889
    )

    assert (
        result["confirmation"]
        == "strong_meeting_signal"
    )

    assert (
        "proxy_event"
        not in result
    )

    assert (
        "proxy_reason"
        not in result
    )


def test_marriage_question_v3_rejects_empty_question(
    monkeypatch,
):
    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload("   "),
    )

    assert response.status_code == 400

    body = response.json()

    assert (
        body["detail"]
        == "question must not be empty."
    )
