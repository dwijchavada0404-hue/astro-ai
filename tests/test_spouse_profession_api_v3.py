from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

import app.services.chart_service as chart_service


client = TestClient(
    app
)


# =========================================================
# MOCK PLACE RESOLUTION
# =========================================================

def _mock_resolve_place(
    place: str,
) -> dict:

    return {
        "query": (
            place
        ),
        "resolved_name": (
            "Mumbai, Mumbai Suburban District, "
            "Maharashtra, 400051, India"
        ),
        "latitude": (
            19.054999
        ),
        "longitude": (
            72.8692035
        ),
        "timezone": (
            "Asia/Kolkata"
        ),
    }


# =========================================================
# REQUEST PAYLOAD
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
# GENERAL SPOUSE PROFESSION
# =========================================================

def test_spouse_profession_api_general(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "What will my spouse do for work?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    understanding = (
        body[
            "understanding"
        ]
    )

    result = (
        body[
            "result"
        ]
    )

    assert (
        understanding[
            "primary_event"
        ]
        == "spouse_profession"
    )

    assert (
        understanding[
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        understanding[
            "intent"
        ][
            "question_type"
        ]
        == "general_outlook"
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
        == "spouse_profession"
    )

    assert (
        result[
            "evidence_engine"
        ]
        == "spouse_profession_reasoning_v2"
    )

    assert (
        result[
            "model_version"
        ]
        == "v2.1"
    )

    assert (
        result[
            "target_profession"
        ]
        is None
    )

    assert (
        result[
            "target_analysis"
        ]
        is None
    )

    assert (
        isinstance(
            result[
                "answer"
            ],
            str,
        )
    )

    assert (
        result[
            "answer"
        ]
    )


# =========================================================
# TARGETED PROFESSION CASES
# =========================================================

@pytest.mark.parametrize(
    (
        "question",
        "expected_target",
        "expected_type",
    ),
    [
        (
            "Will my spouse work abroad?",
            "international_work",
            "broad",
        ),
        (
            "Could my spouse be a lawyer?",
            "law",
            "specific",
        ),
        (
            "Will my spouse have a corporate job?",
            "corporate_work",
            "broad",
        ),
        (
            "Could my spouse be a consultant?",
            "consulting",
            "specific",
        ),
        (
            "Could my spouse be a designer?",
            "creative_work",
            "specific",
        ),
        (
            "Could my spouse own a business?",
            "business",
            "broad",
        ),
        (
            "Will my spouse work in finance?",
            "finance",
            "specific",
        ),
        (
            "Will my spouse work in technology?",
            "technology",
            "specific",
        ),
        (
            "Could my spouse be a software engineer?",
            "technology",
            "specific",
        ),
        (
            "Could my spouse be a banker?",
            "finance",
            "specific",
        ),
        (
            "Could my spouse be an entrepreneur?",
            "business",
            "broad",
        ),
    ],
)
def test_spouse_profession_api_target_detection(
    monkeypatch: pytest.MonkeyPatch,
    question: str,
    expected_target: str,
    expected_type: str,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            question
        ),
    )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.json()
    )

    understanding = (
        body[
            "understanding"
        ]
    )

    result = (
        body[
            "result"
        ]
    )

    assert (
        understanding[
            "primary_event"
        ]
        == "spouse_profession"
    )

    assert (
        understanding[
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        understanding[
            "intent"
        ][
            "question_type"
        ]
        == "probability"
    )

    assert (
        result[
            "event"
        ]
        == "spouse_profession"
    )

    assert (
        result[
            "target_profession"
        ]
        == expected_target
    )

    assert (
        result[
            "target_analysis"
        ][
            "target"
        ]
        == expected_target
    )

    assert (
        result[
            "target_analysis"
        ][
            "target_type"
        ]
        == expected_type
    )

    assert (
        0.0
        <= result[
            "target_analysis"
        ][
            "support_score"
        ]
        <= 1.0
    )

    assert (
        result[
            "target_analysis"
        ][
            "support_level"
        ]
        in (
            "strongly_supported",
            "supported",
            "possible",
            "weakly_supported",
        )
    )

    assert (
        isinstance(
            result[
                "answer"
            ],
            str,
        )
    )

    assert (
        result[
            "answer"
        ]
    )


# =========================================================
# EXPECTED SUPPORT PATTERNS
# =========================================================

@pytest.mark.parametrize(
    (
        "question",
        "expected_support_level",
    ),
    [
        (
            "Will my spouse work abroad?",
            "strongly_supported",
        ),
        (
            "Could my spouse be a lawyer?",
            "strongly_supported",
        ),
        (
            "Will my spouse have a corporate job?",
            "supported",
        ),
        (
            "Could my spouse be a consultant?",
            "strongly_supported",
        ),
        (
            "Could my spouse be a designer?",
            "strongly_supported",
        ),
        (
            "Could my spouse own a business?",
            "strongly_supported",
        ),
        (
            "Will my spouse work in finance?",
            "weakly_supported",
        ),
        (
            "Will my spouse work in technology?",
            "weakly_supported",
        ),
    ],
)
def test_spouse_profession_api_support_levels(
    monkeypatch: pytest.MonkeyPatch,
    question: str,
    expected_support_level: str,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            question
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
            "target_analysis"
        ][
            "support_level"
        ]
        == expected_support_level
    )


# =========================================================
# SPECIFIC TARGET SCORING — LAW
# =========================================================

def test_spouse_profession_api_law_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "Could my spouse be a lawyer?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    target = (
        response.json()[
            "result"
        ][
            "target_analysis"
        ]
    )

    assert (
        target[
            "target_type"
        ]
        == "specific"
    )

    assert (
        target[
            "strongest_cluster_score"
        ]
        == pytest.approx(
            1.0,
            abs=0.001,
        )
    )

    assert (
        target[
            "strongest_family_score"
        ]
        == pytest.approx(
            0.95,
            abs=0.001,
        )
    )

    assert (
        target[
            "support_score"
        ]
        == pytest.approx(
            0.96,
            abs=0.001,
        )
    )


# =========================================================
# TECHNOLOGY DISCOUNT
# =========================================================

def test_spouse_profession_api_technology_discount(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "Will my spouse work in technology?"
        ),
    )

    assert (
        response.status_code
        == 200
    )

    target = (
        response.json()[
            "result"
        ][
            "target_analysis"
        ]
    )

    assert (
        target[
            "target_type"
        ]
        == "specific"
    )

    assert (
        target[
            "strongest_family_score"
        ]
        == pytest.approx(
            0.0,
            abs=0.001,
        )
    )

    assert (
        target[
            "strongest_cluster_score"
        ]
        == pytest.approx(
            0.176,
            abs=0.001,
        )
    )

    assert (
        target[
            "support_score"
        ]
        == pytest.approx(
            0.123,
            abs=0.001,
        )
    )


# =========================================================
# EXISTING EVENTS — API REGRESSION
# =========================================================

@pytest.mark.parametrize(
    (
        "question",
        "expected_event",
    ),
    [
        (
            "What kind of person will I marry?",
            "spouse_traits",
        ),
        (
            "What will my future spouse be like?",
            "spouse_traits",
        ),
        (
            "When will I meet my future spouse?",
            "spouse_meeting",
        ),
        (
            "When will I get married?",
            "marriage_timing",
        ),
        (
            "Will I have a love marriage or arranged marriage?",
            "love_vs_arranged",
        ),
    ],
)
def test_spouse_profession_api_does_not_hijack_existing_routes(
    monkeypatch: pytest.MonkeyPatch,
    question: str,
    expected_event: str,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            question
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
        == expected_event
    )

    assert (
        body[
            "result"
        ][
            "event"
        ]
        == expected_event
    )


# =========================================================
# RESPONSE METADATA
# =========================================================

def test_spouse_profession_api_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "Could my spouse be a consultant?"
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

    assert (
        result[
            "event_label"
        ]
        == "Spouse Profession / Career Profile"
    )

    assert (
        result[
            "question_type"
        ]
        == "probability"
    )

    assert (
        result[
            "direction"
        ]
        == "neutral"
    )

    assert (
        result[
            "parser_confidence"
        ]
        >= 0.82
    )

    assert (
        result[
            "forecast_type"
        ]
        == "natal_pattern"
    )

    assert (
        result[
            "evidence_engine"
        ]
        == "spouse_profession_reasoning_v2"
    )


# =========================================================
# ANALYSIS PAYLOAD
# =========================================================

def test_spouse_profession_api_preserves_analysis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload(
            "What will my spouse do for work?"
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
            "analysis"
        ][
            "model_version"
        ]
        == "v2.1"
    )

    assert (
        result[
            "career_style"
        ]
    )

    assert (
        result[
            "strongest_clusters"
        ]
    )

    assert (
        result[
            "ranked_families"
        ]
    )

    assert (
        result[
            "chart_context"
        ]
    )

    assert (
        result[
            "evidence"
        ]
    )
