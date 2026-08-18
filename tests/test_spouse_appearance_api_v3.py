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
# BASIC GENERAL APPEARANCE ROUTE
# =========================================================

def test_spouse_appearance_api_basic(
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
            "What will my future spouse look like?"
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
        == "spouse_appearance"
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
        == "general_outlook"
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
        == "spouse_appearance"
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
        == "spouse_appearance_reasoning_v2"
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
        == "v2"
    )


# =========================================================
# GENERAL OUTPUT CONTRACT
# =========================================================

def test_spouse_appearance_api_output_contract(
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
            "Describe my future spouse's appearance."
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

    required_keys = (
        "event",
        "model_version",
        "question",
        "normalised_question",
        "target",
        "target_label",
        "matched_keywords",
        "requested_polarity",
        "support_score",
        "support_level",
        "support_label",
        "confidence",
        "answer",
        "summary",
        "limitation",
        "strongest_themes",
        "evidence_count",
        "evidence",
        "natal_profile",
        "analysis",
    )

    for key in required_keys:

        assert (
            key
            in result
        )


# =========================================================
# GENERAL TARGET
# =========================================================

def test_spouse_appearance_api_general_target(
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
            "What will my spouse look like?"
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
        result[
            "target"
        ]
        == "general"
    )

    assert (
        result[
            "target_label"
        ]
        == "General Appearance"
    )

    assert (
        result[
            "requested_polarity"
        ]
        == "direct"
    )


# =========================================================
# HEIGHT TARGET
# =========================================================

def test_spouse_appearance_api_height_target(
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
            "Will my spouse be tall?"
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
        == "spouse_appearance"
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

    result = (
        body[
            "result"
        ]
    )

    assert (
        result[
            "target"
        ]
        == "height"
    )

    assert (
        result[
            "target_label"
        ]
        == "Height"
    )

    assert (
        result[
            "requested_polarity"
        ]
        == "direct"
    )

    assert (
        0.0
        <= result[
            "support_score"
        ]
        <= 0.92
    )


# =========================================================
# SHORT HEIGHT INVERSE POLARITY
# =========================================================

def test_spouse_appearance_api_short_height_inverse(
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
            "Will my spouse be short?"
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
        result[
            "target"
        ]
        == "height"
    )

    assert (
        result[
            "requested_polarity"
        ]
        == "inverse"
    )


# =========================================================
# BUILD TARGET
# =========================================================

def test_spouse_appearance_api_build_target(
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
            "Will my spouse have a lean build?"
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
        result[
            "target"
        ]
        == "build"
    )

    assert (
        result[
            "target_label"
        ]
        == "Body Build"
    )

    assert (
        result[
            "evidence_count"
        ]
        > 0
    )


# =========================================================
# ATTRACTIVENESS TARGET
# =========================================================

def test_spouse_appearance_api_attractiveness_target(
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
            "Will my spouse be attractive?"
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
        result[
            "target"
        ]
        == "attractiveness"
    )

    assert (
        result[
            "target_label"
        ]
        == "Attractiveness"
    )

    assert (
        "subjective"
        in result[
            "limitation"
        ].lower()
    )


# =========================================================
# FACIAL FEATURES TARGET
# =========================================================

def test_spouse_appearance_api_facial_features_target(
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
            "Will my spouse have sharp facial features?"
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
        result[
            "target"
        ]
        == "facial_features"
    )

    assert (
        result[
            "target_label"
        ]
        == "Facial Features"
    )


# =========================================================
# EYES TARGET
# =========================================================

def test_spouse_appearance_api_eyes_target(
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
            "What will my spouse's eyes look like?"
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
        result[
            "target"
        ]
        == "eyes"
    )

    assert (
        result[
            "target_label"
        ]
        == "Eyes / Expression"
    )


# =========================================================
# YOUTHFULNESS TARGET
# =========================================================

def test_spouse_appearance_api_youthfulness_target(
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
            "Will my spouse look youthful?"
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
        result[
            "target"
        ]
        == "youthfulness"
    )

    assert (
        result[
            "target_label"
        ]
        == "Youthful Appearance"
    )


# =========================================================
# MATURITY TARGET
# =========================================================

def test_spouse_appearance_api_maturity_target(
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
            "Will my spouse look mature?"
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
        result[
            "target"
        ]
        == "maturity"
    )

    assert (
        result[
            "target_label"
        ]
        == "Mature Appearance"
    )


# =========================================================
# PRESENCE TARGET
# =========================================================

def test_spouse_appearance_api_presence_target(
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
            "Will my spouse have a striking presence?"
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
        result[
            "target"
        ]
        == "presence"
    )

    assert (
        result[
            "target_label"
        ]
        == "Overall Presence"
    )


# =========================================================
# SCORE / CONFIDENCE BOUNDS
# =========================================================

def test_spouse_appearance_api_scores_are_bounded(
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
            "Will my spouse be attractive?"
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
        <= 0.92
    )

    assert (
        0.50
        <= result[
            "confidence"
        ]
        <= 0.90
    )

    assert (
        result[
            "support_level"
        ]
        in (
            "strong_support",
            "moderate_support",
            "mild_support",
            "limited_support",
        )
    )


# =========================================================
# ANALYSIS CONSISTENCY
# =========================================================

def test_spouse_appearance_api_analysis_consistency(
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
            "Will my spouse have a lean build?"
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
            "target"
        ]
        == analysis[
            "target"
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
            "support_level"
        ]
        == analysis[
            "support_level"
        ]
    )

    assert (
        result[
            "answer"
        ]
        == analysis[
            "answer"
        ]
    )


# =========================================================
# DETECTION METADATA
# =========================================================

def test_spouse_appearance_api_detection_metadata(
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
            "Will my spouse be tall?"
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
        == "spouse_appearance"
    )

    assert (
        "spouse height"
        in understanding[
            "detected_events"
        ][
            0
        ][
            "matched_keywords"
        ]
    )


# =========================================================
# TRAITS REGRESSION
# =========================================================

def test_spouse_appearance_api_does_not_hijack_traits(
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
# PROFESSION REGRESSION
# =========================================================

def test_spouse_appearance_api_does_not_hijack_profession(
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
# FOREIGN / INTERCULTURAL REGRESSION
# =========================================================

def test_spouse_appearance_api_does_not_hijack_foreign(
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
# MEETING REGRESSION
# =========================================================

def test_spouse_appearance_api_does_not_hijack_meeting(
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
# MARRIAGE TIMING REGRESSION
# =========================================================

def test_spouse_appearance_api_does_not_hijack_timing(
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
# LOVE VS ARRANGED REGRESSION
# =========================================================

def test_spouse_appearance_api_does_not_hijack_love_vs_arranged(
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