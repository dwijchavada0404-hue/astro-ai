from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services import chart_service


client = TestClient(
    app
)


# =========================================================
# MOCK PLACE RESOLUTION
# =========================================================

def _mock_resolve_place(
    place: str,
):

    return {
        "resolved_name": (
            "Mumbai, Maharashtra, India"
        ),
        "latitude": (
            19.0760
        ),
        "longitude": (
            72.8777
        ),
        "timezone": (
            "Asia/Kolkata"
        ),
    }

# =========================================================
# PAYLOAD
# =========================================================

def _payload(
    question: str,
) -> dict:

    return {
        "birth": {
            "date": (
                "2000-04-04"
            ),
            "time": (
                "14:04:00"
            ),
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
# BASIC FOREIGN / INTERCULTURAL API ROUTING
# =========================================================

def test_foreign_intercultural_api_basic(
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
            "Will I marry someone from another country?"
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
        == "foreign_intercultural_connection"
    )

    assert (
        body[
            "understanding"
        ][
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        body[
            "understanding"
        ][
            "intent"
        ][
            "question_type"
        ]
        == "probability"
    )

    assert (
        body[
            "understanding"
        ][
            "intent"
        ][
            "direction"
        ]
        == "occurrence"
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
            "event"
        ]
        == "foreign_intercultural_connection"
    )

    assert (
        result[
            "route"
        ]
        == "natal_evidence"
    )

    assert (
        result[
            "evidence_engine"
        ]
        == "marriage_foreign_intercultural_reasoning_v1"
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
        == "v1"
    )


# =========================================================
# API OUTPUT CONTRACT
# =========================================================

def test_foreign_intercultural_api_output_contract(
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
            "Could my spouse be from a different country?"
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

    assert (
        "outcome"
        in result
    )

    assert (
        "label"
        in result
    )

    assert (
        "confidence"
        in result
    )

    assert (
        "support_score"
        in result
    )

    assert (
        "probability_level"
        in result
    )

    assert (
        "probability_score"
        in result
    )

    assert (
        "answer"
        in result
    )

    assert (
        "summary"
        in result
    )

    assert (
        "scores"
        in result
    )

    assert (
        "chart_context"
        in result
    )

    assert (
        "primary_indicators"
        in result
    )

    assert (
        "secondary_indicators"
        in result
    )

    assert (
        "context_indicators"
        in result
    )

    assert (
        "indicators"
        in result
    )

    assert (
        "analysis"
        in result
    )


# =========================================================
# SCORE BOUNDS
# =========================================================

def test_foreign_intercultural_api_scores_are_bounded(
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
            "Will I have an intercultural marriage?"
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

    assert (
        0.0
        <= result[
            "support_score"
        ]
        <= 1.0
    )

    assert (
        0.0
        <= result[
            "probability_score"
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

    assert (
        result[
            "outcome"
        ]
        in (
            "strongly_supported",
            "supported",
            "mixed",
            "weakly_supported",
        )
    )


# =========================================================
# MATCHED KEYWORDS PROPAGATE THROUGH UNDERSTANDING
# =========================================================

def test_foreign_intercultural_api_preserves_detection_metadata(
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
            "Will my spouse be from another country?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    understanding = (
        response.json()[
            "understanding"
        ]
    )

    assert (
        understanding[
            "event_count"
        ]
        == 1
    )

    assert (
        understanding[
            "detected_events"
        ][
            0
        ][
            "event"
        ]
        == "foreign_intercultural_connection"
    )

    assert (
        "spouse from another country"
        in understanding[
            "detected_events"
        ][
            0
        ][
            "matched_keywords"
        ]
    )


# =========================================================
# PROFESSION CONFLICT PROTECTION
# =========================================================

def test_foreign_intercultural_api_does_not_hijack_spouse_profession(
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
            "Will my spouse work abroad?"
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
        == "spouse_profession"
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == "spouse_profession"
    )


# =========================================================
# SPOUSE TRAITS CONFLICT PROTECTION
# =========================================================

def test_foreign_intercultural_api_does_not_hijack_spouse_traits(
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
# SPOUSE MEETING CONFLICT PROTECTION
# =========================================================

def test_foreign_intercultural_api_does_not_hijack_spouse_meeting(
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


# =========================================================
# MARRIAGE TIMING CONFLICT PROTECTION
# =========================================================

def test_foreign_intercultural_api_does_not_hijack_marriage_timing(
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
# LOVE VS ARRANGED CONFLICT PROTECTION
# =========================================================

def test_foreign_intercultural_api_does_not_hijack_love_vs_arranged(
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
            "Will I have a love marriage or arranged marriage?"
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
        == "love_vs_arranged"
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == "love_vs_arranged"
    )


# =========================================================
# INTERFAITH VARIANT
# =========================================================

def test_foreign_intercultural_api_interfaith_variant(
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
            "Could I have an interfaith marriage?"
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
        == "foreign_intercultural_connection"
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == "foreign_intercultural_connection"
    )


# =========================================================
# REGIONAL VARIANT
# =========================================================

def test_foreign_intercultural_api_regional_variant(
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
            "Will my spouse be from another state?"
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
        == "foreign_intercultural_connection"
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == "foreign_intercultural_connection"
    )


# =========================================================
# ANALYSIS CONSISTENCY
# =========================================================

def test_foreign_intercultural_api_analysis_consistency(
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
            "Will I marry someone from a different culture?"
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

    analysis = (
        result[
            "analysis"
        ]
    )

    assert (
        result[
            "support_score"
        ]
        == analysis[
            "support_score"
        ]
    )

    assert (
        result[
            "probability_score"
        ]
        == analysis[
            "support_score"
        ]
    )

    assert (
        result[
            "answer"
        ]
        == analysis[
            "summary"
        ]
    )

    assert (
        result[
            "outcome"
        ]
        == analysis[
            "outcome"
        ]
    )


