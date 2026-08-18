from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

import app.astrology.features.marriage_forecast_router_v3 as router


REFERENCE_MOMENT = datetime(
    2026,
    8,
    15,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


# =========================================================
# REFERENCE CHART
# =========================================================

def _reference_chart() -> dict[str, Any]:

    return {
        "houses": {
            "1": {
                "sign": "Cancer",
                "lord": "Moon",
            },
            "2": {
                "sign": "Leo",
                "lord": "Sun",
            },
            "3": {
                "sign": "Virgo",
                "lord": "Mercury",
            },
            "4": {
                "sign": "Libra",
                "lord": "Venus",
            },
            "5": {
                "sign": "Scorpio",
                "lord": "Mars",
            },
            "6": {
                "sign": "Sagittarius",
                "lord": "Jupiter",
            },
            "7": {
                "sign": "Capricorn",
                "lord": "Saturn",
            },
            "8": {
                "sign": "Aquarius",
                "lord": "Saturn",
            },
            "9": {
                "sign": "Pisces",
                "lord": "Jupiter",
            },
            "10": {
                "sign": "Aries",
                "lord": "Mars",
            },
            "11": {
                "sign": "Taurus",
                "lord": "Venus",
            },
            "12": {
                "sign": "Gemini",
                "lord": "Mercury",
            },
        },
        "planets": {
            "Sun": {
                "house": 9,
                "sign": "Pisces",
            },
            "Moon": {
                "house": 9,
                "sign": "Pisces",
            },
            "Mars": {
                "house": 10,
                "sign": "Aries",
            },
            "Mercury": {
                "house": 8,
                "sign": "Aquarius",
            },
            "Jupiter": {
                "house": 10,
                "sign": "Aries",
            },
            "Venus": {
                "house": 9,
                "sign": "Pisces",
            },
            "Saturn": {
                "house": 10,
                "sign": "Aries",
            },
            "Rahu": {
                "house": 1,
                "sign": "Cancer",
            },
            "Ketu": {
                "house": 7,
                "sign": "Capricorn",
            },
        },
    }


# =========================================================
# QUESTION ANALYSIS
# =========================================================

def _question_analysis(
    question: str = "What will my future spouse look like?",
    question_type: str = "general_outlook",
) -> dict[str, Any]:

    return {
        "available": True,
        "original_question": question,
        "normalised_question": question.lower(),
        "query_mode": "single_event",
        "complexity": "standard",
        "primary_event": "spouse_appearance",
        "primary_event_label": (
            "Spouse Appearance / Physical Profile"
        ),
        "detected_events": [
            {
                "event": "spouse_appearance",
                "event_label": (
                    "Spouse Appearance / Physical Profile"
                ),
                "matched_keywords": [
                    "spouse appearance"
                ],
            }
        ],
        "event_count": 1,
        "is_multi_event": False,
        "intent": {
            "domain": "marriage",
            "event": "spouse_appearance",
            "event_label": (
                "Spouse Appearance / Physical Profile"
            ),
            "question_type": question_type,
            "direction": "neutral",
            "confidence": 0.82,
        },
        "comparison": {
            "is_comparison": False,
            "comparison_type": None,
            "values": [],
        },
        "follow_up": {
            "is_follow_up": False,
            "requires_context": False,
        },
    }


# =========================================================
# DIRECT ROUTE CONTRACT
# =========================================================

def test_spouse_appearance_route_basic_contract():

    result = (
        router._route_spouse_appearance(
            _reference_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result["available"]
        is True
    )

    assert (
        result["route"]
        == "natal_evidence"
    )

    assert (
        result["event"]
        == "spouse_appearance"
    )

    assert (
        result["event_label"]
        == "Spouse Appearance / Physical Profile"
    )

    assert (
        result["evidence_engine"]
        == "spouse_appearance_reasoning_v2"
    )

    assert (
        result["forecast_type"]
        == "natal_pattern"
    )

    assert (
        result["model_version"]
        == "v2"
    )


# =========================================================
# GENERAL APPEARANCE
# =========================================================

def test_spouse_appearance_route_general_question():

    result = (
        router._route_spouse_appearance(
            _reference_chart(),
            _question_analysis(
                "What will my future spouse look like?"
            ),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result["target"]
        == "general"
    )

    assert (
        result["target_label"]
        == "General Appearance"
    )

    assert isinstance(
        result["answer"],
        str,
    )

    assert (
        result["answer"]
    )

    assert isinstance(
        result["strongest_themes"],
        list,
    )


# =========================================================
# TARGETED HEIGHT
# =========================================================

def test_spouse_appearance_route_height_target():

    result = (
        router._route_spouse_appearance(
            _reference_chart(),
            _question_analysis(
                "Will my spouse be tall?",
                question_type="probability",
            ),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result["target"]
        == "height"
    )

    assert (
        result["question_type"]
        == "probability"
    )

    assert (
        result["direction"]
        == "neutral"
    )

    assert (
        0.0
        <= result["support_score"]
        <= 0.92
    )


# =========================================================
# TARGETED BUILD
# =========================================================

def test_spouse_appearance_route_build_target():

    result = (
        router._route_spouse_appearance(
            _reference_chart(),
            _question_analysis(
                "Will my spouse have a lean build?",
                question_type="probability",
            ),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result["target"]
        == "build"
    )

    assert (
        result["evidence_count"]
        > 0
    )


# =========================================================
# TARGETED ATTRACTIVENESS
# =========================================================

def test_spouse_appearance_route_attractiveness_target():

    chart = (
        _reference_chart()
    )

    chart["planets"]["Venus"]["house"] = 7
    chart["planets"]["Venus"]["sign"] = "Capricorn"

    result = (
        router._route_spouse_appearance(
            chart,
            _question_analysis(
                "Will my spouse be attractive?",
                question_type="probability",
            ),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result["target"]
        == "attractiveness"
    )

    assert (
        result["evidence_count"]
        > 0
    )

    assert (
        "subjective"
        in result["limitation"].lower()
    )


# =========================================================
# MAIN ROUTER DISPATCH
# =========================================================

def test_main_router_dispatches_spouse_appearance(
    monkeypatch,
):

    expected = {
        "available": True,
        "event": "spouse_appearance",
        "route": "natal_evidence",
        "sentinel": "appearance-route-called",
    }

    def _mock_route(
        chart: dict[str, Any],
        question_analysis: dict[str, Any],
        reference_moment: datetime,
    ) -> dict[str, Any]:

        return expected

    monkeypatch.setattr(
        router,
        "_route_spouse_appearance",
        _mock_route,
    )

    result = (
        router.route_marriage_question_v3(
            _reference_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result
        == expected
    )


# =========================================================
# MAIN ROUTER ARGUMENTS
# =========================================================

def test_main_router_passes_arguments_to_spouse_appearance(
    monkeypatch,
):

    chart = (
        _reference_chart()
    )

    analysis = (
        _question_analysis(
            "Will my spouse be tall?",
            question_type="probability",
        )
    )

    captured = {}

    def _mock_route(
        received_chart: dict[str, Any],
        received_analysis: dict[str, Any],
        received_reference: datetime,
    ) -> dict[str, Any]:

        captured["chart"] = received_chart
        captured["analysis"] = received_analysis
        captured["reference"] = received_reference

        return {
            "available": True,
            "event": "spouse_appearance",
        }

    monkeypatch.setattr(
        router,
        "_route_spouse_appearance",
        _mock_route,
    )

    router.route_marriage_question_v3(
        chart,
        analysis,
        REFERENCE_MOMENT,
    )

    assert (
        captured["chart"]
        is chart
    )

    assert (
        captured["analysis"]
        is analysis
    )

    assert (
        captured["reference"]
        is REFERENCE_MOMENT
    )


# =========================================================
# FOLLOW-UP ROUTE
# =========================================================

def test_spouse_appearance_follow_up_inherits_event(
    monkeypatch,
):

    captured = {}

    def _mock_route(
        chart: dict[str, Any],
        question_analysis: dict[str, Any],
        reference_moment: datetime,
    ) -> dict[str, Any]:

        captured["analysis"] = question_analysis

        return {
            "available": True,
            "route": "natal_evidence",
            "event": "spouse_appearance",
            "answer": "appearance answer",
        }

    monkeypatch.setattr(
        router,
        "_route_spouse_appearance",
        _mock_route,
    )

    follow_up_analysis = {
        "original_question": "What about her appearance?",
        "normalised_question": "what about her appearance?",
        "query_mode": "follow_up",
        "primary_event": "general_marriage",
        "primary_event_label": (
            "General Marriage / Relationship Outlook"
        ),
        "intent": {
            "domain": "marriage",
            "event": "general_marriage",
            "event_label": (
                "General Marriage / Relationship Outlook"
            ),
            "question_type": "general_outlook",
            "direction": "neutral",
            "confidence": 0.60,
        },
    }

    previous_context = {
        "question_analysis": {
            "primary_event": "spouse_appearance",
        }
    }

    result = (
        router.route_marriage_question_v3(
            _reference_chart(),
            follow_up_analysis,
            REFERENCE_MOMENT,
            previous_context=previous_context,
        )
    )

    assert (
        result["route"]
        == "follow_up"
    )

    assert (
        result["context_used"]
        is True
    )

    assert (
        result["inherited_event"]
        == "spouse_appearance"
    )

    assert (
        captured["analysis"]["primary_event"]
        == "spouse_appearance"
    )


# =========================================================
# UNAVAILABLE ANALYSIS
# =========================================================

def test_spouse_appearance_route_unavailable(
    monkeypatch,
):

    def _mock_analysis(
        chart: dict[str, Any],
        question: str,
    ) -> dict[str, Any]:

        return {
            "available": False,
            "event": "spouse_appearance",
            "model_version": "v2",
            "reason": "appearance unavailable",
        }

    monkeypatch.setattr(
        router,
        "analyze_spouse_appearance_v2",
        _mock_analysis,
    )

    result = (
        router._route_spouse_appearance(
            _reference_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result["available"]
        is False
    )

    assert (
        result["event"]
        == "spouse_appearance"
    )

    assert (
        result["evidence_engine"]
        == "spouse_appearance_reasoning_v2"
    )

    assert (
        result["reason"]
        == "appearance unavailable"
    )


# =========================================================
# OUTPUT CONTRACT
# =========================================================

def test_spouse_appearance_route_output_contract():

    result = (
        router._route_spouse_appearance(
            _reference_chart(),
            _question_analysis(
                "Will my spouse look mature?",
                question_type="probability",
            ),
            REFERENCE_MOMENT,
        )
    )

    required = {
        "available",
        "route",
        "event",
        "event_label",
        "question_type",
        "direction",
        "parser_confidence",
        "reference_moment",
        "evidence_engine",
        "forecast_type",
        "model_version",
        "confidence",
        "answer",
        "summary",
        "target",
        "target_label",
        "matched_keywords",
        "requested_polarity",
        "support_score",
        "support_level",
        "support_label",
        "limitation",
        "strongest_themes",
        "evidence_count",
        "evidence",
        "natal_profile",
        "natal_analysis",
        "analysis",
    }

    assert (
        required
        <= set(result)
    )


# =========================================================
# ANALYSIS CONSISTENCY
# =========================================================

def test_spouse_appearance_route_analysis_consistency():

    result = (
        router._route_spouse_appearance(
            _reference_chart(),
            _question_analysis(
                "Will my spouse look mature?",
                question_type="probability",
            ),
            REFERENCE_MOMENT,
        )
    )

    analysis = (
        result["analysis"]
    )

    assert (
        result["target"]
        == analysis["target"]
    )

    assert (
        result["support_score"]
        == analysis["support_score"]
    )

    assert (
        result["confidence"]
        == analysis["confidence"]
    )

    assert (
        result["answer"]
        == analysis["answer"]
    )


# =========================================================
# INPUT VALIDATION REGRESSION
# =========================================================

def test_main_router_requires_timezone():

    naive_reference = datetime(
        2026,
        8,
        15,
        12,
        0,
        0,
    )

    with pytest.raises(
        ValueError,
        match="reference_moment must include a timezone offset",
    ):

        router.route_marriage_question_v3(
            _reference_chart(),
            _question_analysis(),
            naive_reference,
        )
