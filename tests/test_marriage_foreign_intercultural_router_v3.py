from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features import (
    marriage_forecast_router_v3 as router,
)


# =========================================================
# TEST CONSTANTS
# =========================================================

REFERENCE_MOMENT = datetime.fromisoformat(
    "2026-08-15T12:00:00+05:30"
)


# =========================================================
# MOCK CHART
# =========================================================

def _mock_chart() -> dict[str, Any]:

    return {
        "houses": {
            "1": {
                "sign": "Taurus",
                "lord": "Venus",
            },
            "2": {
                "sign": "Gemini",
                "lord": "Mercury",
            },
            "3": {
                "sign": "Cancer",
                "lord": "Moon",
            },
            "4": {
                "sign": "Leo",
                "lord": "Sun",
            },
            "5": {
                "sign": "Virgo",
                "lord": "Mercury",
            },
            "6": {
                "sign": "Libra",
                "lord": "Venus",
            },
            "7": {
                "sign": "Scorpio",
                "lord": "Mars",
            },
            "8": {
                "sign": "Sagittarius",
                "lord": "Jupiter",
            },
            "9": {
                "sign": "Capricorn",
                "lord": "Saturn",
            },
            "10": {
                "sign": "Aquarius",
                "lord": "Saturn",
            },
            "11": {
                "sign": "Pisces",
                "lord": "Jupiter",
            },
            "12": {
                "sign": "Aries",
                "lord": "Mars",
            },
        },

        "planets": {
            "Sun": {
                "house": 4,
                "sign": "Leo",
            },
            "Moon": {
                "house": 3,
                "sign": "Cancer",
            },
            "Mars": {
                "house": 12,
                "sign": "Aries",
            },
            "Mercury": {
                "house": 5,
                "sign": "Virgo",
            },
            "Jupiter": {
                "house": 8,
                "sign": "Sagittarius",
            },
            "Venus": {
                "house": 6,
                "sign": "Libra",
            },
            "Saturn": {
                "house": 9,
                "sign": "Capricorn",
            },
            "Rahu": {
                "house": 7,
                "sign": "Scorpio",
            },
            "Ketu": {
                "house": 1,
                "sign": "Taurus",
            },
        },
    }


# =========================================================
# MOCK QUESTION ANALYSIS
# =========================================================

def _question_analysis(
    question: str = (
        "Will I marry someone from another country?"
    ),
) -> dict[str, Any]:

    return {
        "available": True,

        "original_question": (
            question
        ),

        "normalised_question": (
            question.lower()
        ),

        "query_mode": (
            "single_event"
        ),

        "complexity": (
            "standard"
        ),

        "primary_event": (
            "foreign_intercultural_connection"
        ),

        "primary_event_label": (
            "Foreign / Intercultural Relationship"
        ),

        "detected_events": [
            {
                "event": (
                    "foreign_intercultural_connection"
                ),

                "event_label": (
                    "Foreign / Intercultural Relationship"
                ),

                "matched_keywords": [
                    "another country"
                ],
            }
        ],

        "event_count": 1,

        "is_multi_event": False,

        "comparison": {
            "is_comparison": False,
            "comparison_type": None,
            "values": [],
        },

        "follow_up": {
            "is_follow_up": False,
            "requires_context": False,
        },

        "intent": {
            "domain": (
                "marriage"
            ),

            "event": (
                "foreign_intercultural_connection"
            ),

            "event_label": (
                "Foreign / Intercultural Relationship"
            ),

            "question_type": (
                "probability"
            ),

            "direction": (
                "occurrence"
            ),

            "confidence": (
                0.82
            ),
        },
    }


# =========================================================
# DIRECT ROUTE TEST
# =========================================================

def test_foreign_intercultural_direct_route():

    result = (
        router._route_foreign_intercultural_connection(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
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
            "forecast_type"
        ]
        == "natal_pattern"
    )

    assert (
        result[
            "evidence_engine"
        ]
        == "marriage_foreign_intercultural_reasoning_v1"
    )

    assert (
        result[
            "model_version"
        ]
        == "v1"
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
        == "occurrence"
    )

    assert isinstance(
        result[
            "support_score"
        ],
        float,
    )

    assert (
        0.0
        <= result[
            "support_score"
        ]
        <= 1.0
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

    assert isinstance(
        result[
            "answer"
        ],
        str,
    )

    assert (
        result[
            "answer"
        ]
    )

    assert isinstance(
        result[
            "analysis"
        ],
        dict,
    )


# =========================================================
# STRONG FOREIGN PATTERN
# =========================================================

def test_foreign_intercultural_route_detects_strong_pattern():

    result = (
        router._route_foreign_intercultural_connection(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    analysis = (
        result[
            "analysis"
        ]
    )

    factors = {
        item[
            "factor"
        ]
        for item in analysis[
            "indicators"
        ]
    }

    assert (
        "seventh_lord_in_foreign_house"
        in factors
    )

    assert (
        "rahu_in_seventh"
        in factors
    )

    assert (
        "seventh_twelfth_connection"
        in factors
    )

    assert (
        result[
            "support_score"
        ]
        > 0.0
    )


# =========================================================
# SCORE PROPAGATION
# =========================================================

def test_foreign_intercultural_route_propagates_scores():

    result = (
        router._route_foreign_intercultural_connection(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
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
            "probability_level"
        ]
        == analysis[
            "probability_level"
        ]
    )

    assert (
        result[
            "confidence"
        ]
        == analysis[
            "confidence"
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


# =========================================================
# INDICATOR PROPAGATION
# =========================================================

def test_foreign_intercultural_route_propagates_indicators():

    result = (
        router._route_foreign_intercultural_connection(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    analysis = (
        result[
            "analysis"
        ]
    )

    assert (
        result[
            "primary_indicators"
        ]
        == analysis[
            "primary_indicators"
        ]
    )

    assert (
        result[
            "secondary_indicators"
        ]
        == analysis[
            "secondary_indicators"
        ]
    )

    assert (
        result[
            "context_indicators"
        ]
        == analysis[
            "context_indicators"
        ]
    )

    assert (
        result[
            "indicators"
        ]
        == analysis[
            "indicators"
        ]
    )


# =========================================================
# CHART CONTEXT PROPAGATION
# =========================================================

def test_foreign_intercultural_route_propagates_chart_context():

    result = (
        router._route_foreign_intercultural_connection(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
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
            "lord"
        ]
        == "Mars"
    )

    assert (
        context[
            "seventh_lord"
        ][
            "house"
        ]
        == 12
    )

    assert (
        context[
            "rahu"
        ][
            "house"
        ]
        == 7
    )


# =========================================================
# UNAVAILABLE ENGINE RESULT
# =========================================================

def test_foreign_intercultural_route_handles_unavailable_result(
    monkeypatch,
):

    def _mock_analysis(
        chart: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "available": False,
            "event": (
                "foreign_intercultural_connection"
            ),
            "model_version": (
                "v1"
            ),
            "reason": (
                "7th house data is unavailable."
            ),
        }

    monkeypatch.setattr(
        router,
        "analyze_foreign_intercultural_relationship_v1",
        _mock_analysis,
    )

    result = (
        router._route_foreign_intercultural_connection(
            {},
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result[
            "available"
        ]
        is False
    )

    assert (
        result[
            "event"
        ]
        == "foreign_intercultural_connection"
    )

    assert (
        result[
            "reason"
        ]
        == "7th house data is unavailable."
    )

    assert (
        result[
            "evidence_engine"
        ]
        == "marriage_foreign_intercultural_reasoning_v1"
    )


# =========================================================
# MAIN ROUTER SINGLE-EVENT DISPATCH
# =========================================================

def test_main_router_dispatches_foreign_intercultural_event(
    monkeypatch,
):

    expected = {
        "available": True,
        "event": (
            "foreign_intercultural_connection"
        ),
        "route": (
            "natal_evidence"
        ),
        "sentinel": (
            "foreign-route-called"
        ),
    }

    def _mock_route(
        chart: dict[str, Any],
        question_analysis: dict[str, Any],
        reference_moment: datetime,
    ) -> dict[str, Any]:

        return (
            expected
        )

    monkeypatch.setattr(
        router,
        "_route_foreign_intercultural_connection",
        _mock_route,
    )

    result = (
        router.route_marriage_question_v3(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result
        == expected
    )


# =========================================================
# MAIN ROUTER PASSES CORRECT ARGUMENTS
# =========================================================

def test_main_router_passes_arguments_to_foreign_route(
    monkeypatch,
):

    chart = (
        _mock_chart()
    )

    question_analysis = (
        _question_analysis(
            "Will my spouse be from another country?"
        )
    )

    captured = {}

    def _mock_route(
        received_chart: dict[str, Any],
        received_analysis: dict[str, Any],
        received_reference: datetime,
    ) -> dict[str, Any]:

        captured[
            "chart"
        ] = (
            received_chart
        )

        captured[
            "analysis"
        ] = (
            received_analysis
        )

        captured[
            "reference"
        ] = (
            received_reference
        )

        return {
            "available": True,
            "event": (
                "foreign_intercultural_connection"
            ),
        }

    monkeypatch.setattr(
        router,
        "_route_foreign_intercultural_connection",
        _mock_route,
    )

    router.route_marriage_question_v3(
        chart,
        question_analysis,
        REFERENCE_MOMENT,
    )

    assert (
        captured[
            "chart"
        ]
        is chart
    )

    assert (
        captured[
            "analysis"
        ]
        is question_analysis
    )

    assert (
        captured[
            "reference"
        ]
        == REFERENCE_MOMENT
    )


# =========================================================
# FOLLOW-UP ROUTING
# =========================================================

def test_follow_up_routes_foreign_intercultural_event(
    monkeypatch,
):

    expected = {
        "available": True,
        "event": (
            "foreign_intercultural_connection"
        ),
        "route": (
            "natal_evidence"
        ),
    }

    def _mock_route(
        chart: dict[str, Any],
        question_analysis: dict[str, Any],
        reference_moment: datetime,
    ) -> dict[str, Any]:

        return dict(
            expected
        )

    monkeypatch.setattr(
        router,
        "_route_foreign_intercultural_connection",
        _mock_route,
    )

    follow_up_analysis = {
        "query_mode": (
            "follow_up"
        ),

        "primary_event": (
            "general_marriage"
        ),

        "intent": {
            "domain": (
                "marriage"
            ),

            "event": (
                "general_marriage"
            ),

            "question_type": (
                "probability"
            ),

            "direction": (
                "neutral"
            ),

            "confidence": (
                0.60
            ),
        },
    }

    previous_context = {
        "question_analysis": {
            "primary_event": (
                "foreign_intercultural_connection"
            ),
        },

        "route_result": {
            "event": (
                "foreign_intercultural_connection"
            ),
        },
    }

    result = (
        router.route_marriage_question_v3(
            _mock_chart(),
            follow_up_analysis,
            REFERENCE_MOMENT,
            previous_context=previous_context,
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
        == "foreign_intercultural_connection"
    )

    assert (
        result[
            "route"
        ]
        == "follow_up"
    )

    assert (
        result[
            "context_used"
        ]
        is True
    )

    assert (
        result[
            "inherited_event"
        ]
        == "foreign_intercultural_connection"
    )


# =========================================================
# EVENT LABEL
# =========================================================

def test_foreign_intercultural_event_label():

    result = (
        router._route_foreign_intercultural_connection(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result[
            "event_label"
        ]
        == "Foreign / Intercultural Relationship"
    )


# =========================================================
# REFERENCE MOMENT
# =========================================================

def test_foreign_intercultural_reference_moment():

    result = (
        router._route_foreign_intercultural_connection(
            _mock_chart(),
            _question_analysis(),
            REFERENCE_MOMENT,
        )
    )

    assert (
        result[
            "reference_moment"
        ]
        == REFERENCE_MOMENT.isoformat()
    )