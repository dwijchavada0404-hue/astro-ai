from fastapi.testclient import TestClient

import app.services.chart_service as chart_service

from app.main import app


client = TestClient(
    app
)


# =========================================================
# HELPERS
# =========================================================

def _mock_resolve_place(
    place: str,
):

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


def _payload(
    question: str,
):

    return {
        "birth": {
            "date": "2000-04-04",
            "time": "14:04:00",
            "place": (
                "Mumbai, Maharashtra, India"
            ),
        },
        "question": question,
        "reference_moment": (
            "2026-08-15T12:00:00+05:30"
        ),
    }


# =========================================================
# END-TO-END SPOUSE TRAITS
# =========================================================

def test_marriage_question_v3_spouse_traits_api(
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
            "What will my future spouse be like?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body[
            "understanding"
        ][
            "primary_event"
        ]
        == "spouse_traits"
    )

    assert (
        body[
            "understanding"
        ][
            "query_mode"
        ]
        == "single_event"
    )

    result = (
        body[
            "result"
        ]
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

    assert (
        result[
            "evidence_engine"
        ]
        == "spouse_traits_reasoning_v2"
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
# PROFILE DATA
# =========================================================

def test_marriage_question_v3_spouse_traits_profile_api(
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
            "Describe my future spouse."
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    result = (
        body[
            "result"
        ]
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

    assert (
        profile[
            "social_background"
        ]
        == []
    )


# =========================================================
# BLENDED TRAITS
# =========================================================

def test_marriage_question_v3_spouse_traits_blends_api(
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
            "What kind of personality will my spouse have?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    result = (
        response.json()[
            "result"
        ]
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
# ALTERNATE PHRASING
# =========================================================

def test_marriage_question_v3_spouse_traits_alt_phrase_api(
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
            "What kind of person will I marry?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body[
            "understanding"
        ][
            "primary_event"
        ]
        == "spouse_traits"
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == "spouse_traits"
    )


# =========================================================
# DO NOT BREAK MARRIAGE TIMING
# =========================================================

def test_marriage_question_v3_spouse_traits_does_not_break_timing(
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

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body[
            "understanding"
        ][
            "primary_event"
        ]
        == "marriage_timing"
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == "marriage_timing"
    )


# =========================================================
# DO NOT BREAK SPOUSE MEETING
# =========================================================

def test_marriage_question_v3_spouse_traits_does_not_break_meeting(
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

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    assert (
        body[
            "understanding"
        ][
            "primary_event"
        ]
        == "spouse_meeting"
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == "spouse_meeting"
    )

    assert (
        body[
            "result"
        ][
            "forecast_engine"
        ]
        == "spouse_meeting_forecast_v2"
    )
