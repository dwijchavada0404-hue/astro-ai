from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import app.services.chart_service as chart_service

from app.astrology.features.career_forecast_router_v3 import (
    route_career_question_v3,
)
from app.astrology.features.career_question_intelligence_v3 import (
    analyze_career_question_v3,
)
from app.models.chart import BirthInput
from app.services.chart_service import build_chart


# =========================================================
# CANONICAL REFERENCE DATA
# =========================================================

REFERENCE_PLACE = {
    "query": "Mumbai, Maharashtra, India",
    "resolved_name": (
        "Mumbai, Mumbai Suburban District, "
        "Maharashtra, 400051, India"
    ),
    "latitude": 19.054999,
    "longitude": 72.8692035,
    "timezone": "Asia/Kolkata",
}


REFERENCE_BIRTH = BirthInput(
    date="2000-04-04",
    time="14:04",
    place="Mumbai, Maharashtra, India",
)


REFERENCE_MOMENT = datetime(
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
# FIXTURES
# =========================================================

@pytest.fixture
def canonical_chart(
    monkeypatch,
):
    """
    Build the canonical 2:04 PM reference chart
    using fixed coordinates.

    The test intentionally avoids live geocoding so
    regression results remain deterministic.
    """

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        lambda place: {
            **REFERENCE_PLACE,
            "query": place,
        },
    )

    return build_chart(
        REFERENCE_BIRTH
    )


# =========================================================
# HELPER
# =========================================================

def _ask(
    chart,
    question: str,
    previous_context=None,
):
    analysis = (
        analyze_career_question_v3(
            question
        )
    )

    result = (
        route_career_question_v3(
            chart,
            analysis,
            REFERENCE_MOMENT,
            previous_context=(
                previous_context
            ),
        )
    )

    return (
        analysis,
        result,
    )


# =========================================================
# SINGLE EVENT — JOB CHANGE
# =========================================================

def test_v3_job_change_next_6_months(
    canonical_chart,
):
    analysis, result = _ask(
        canonical_chart,
        (
            "Will I change my job "
            "in the next 6 months?"
        ),
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
        == "job_change"
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
        == "job_change"
    )

    assert (
        result[
            "resolved_forecast_request"
        ][
            "range_type"
        ]
        == "next_6_months"
    )

    assert (
        result[
            "forecast_available"
        ]
        is False
    )

    assert (
        result[
            "outcome"
        ]
        == "no_strong_window"
    )

    assert (
        result[
            "probability_level"
        ]
        == "not_strongly_supported"
    )

    assert (
        result[
            "probability_score"
        ]
        == 0.3
    )

    assert (
        result[
            "window"
        ]
        == {}
    )


# =========================================================
# SINGLE EVENT — PROMOTION
# =========================================================

def test_v3_promotion_window(
    canonical_chart,
):
    analysis, result = _ask(
        canonical_chart,
        "When will I get promoted?",
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "promotion_recognition"
    )

    assert (
        result[
            "event"
        ]
        == "promotion_recognition"
    )

    assert (
        result[
            "forecast_available"
        ]
        is True
    )

    assert (
        result[
            "outcome"
        ]
        == "very_strong"
    )

    assert (
        result[
            "probability_level"
        ]
        == "strongly_likely"
    )

    assert (
        result[
            "confirmation"
        ]
        == "strong_confirmation"
    )

    window = result[
        "window"
    ]

    assert (
        window[
            "start"
        ]
        == "2027-04-17"
    )

    assert (
        window[
            "end"
        ]
        == "2027-07-03"
    )

    assert (
        window[
            "peak_date"
        ]
        == "2027-06-05"
    )

    assert (
        window[
            "period"
        ]
        == "Venus/Venus"
    )

    assert (
        window[
            "strength"
        ]
        == "very_strong"
    )


# =========================================================
# SINGLE EVENT — INCOME
# =========================================================

def test_v3_income_gain_window(
    canonical_chart,
):
    analysis, result = _ask(
        canonical_chart,
        (
            "Will my salary increase "
            "in the next year?"
        ),
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "income_gains"
    )

    assert (
        result[
            "event"
        ]
        == "income_gains"
    )

    assert (
        result[
            "forecast_available"
        ]
        is True
    )

    assert (
        result[
            "outcome"
        ]
        == "strong"
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
        == 0.8
    )

    assert (
        result[
            "confirmation"
        ]
        == "strong_confirmation"
    )

    window = result[
        "window"
    ]

    assert (
        window[
            "start"
        ]
        == "2027-06-26"
    )

    assert (
        window[
            "end"
        ]
        == "2027-08-21"
    )

    assert (
        window[
            "peak_date"
        ]
        == "2027-06-26"
    )

    assert (
        window[
            "period"
        ]
        == "Venus/Venus"
    )

    assert (
        window[
            "strength"
        ]
        == "strong"
    )


# =========================================================
# MULTI EVENT — PROMOTION + INCOME
# =========================================================

def test_v3_promotion_and_income_overlap(
    canonical_chart,
):
    analysis, result = _ask(
        canonical_chart,
        (
            "Will I get promoted and "
            "get a salary increase "
            "in the next year?"
        ),
    )

    assert (
        analysis[
            "query_mode"
        ]
        == "multi_event"
    )

    assert (
        analysis[
            "event_count"
        ]
        == 2
    )

    assert (
        result[
            "route"
        ]
        == "multi_event"
    )

    assert (
        result[
            "events"
        ]
        == [
            "promotion_recognition",
            "income_gains",
        ]
    )

    relationship = result[
        "relationship"
    ]

    assert (
        relationship[
            "relationship"
        ]
        == "both_supported_and_overlapping"
    )

    overlap = relationship[
        "overlap"
    ]

    assert (
        overlap[
            "available"
        ]
        is True
    )

    assert (
        overlap[
            "start"
        ]
        == "2027-06-26"
    )

    assert (
        overlap[
            "end"
        ]
        == "2027-07-03"
    )

    event_results = result[
        "event_results"
    ]

    assert (
        event_results[
            0
        ][
            "event"
        ]
        == "promotion_recognition"
    )

    assert (
        event_results[
            1
        ][
            "event"
        ]
        == "income_gains"
    )


# =========================================================
# YEAR COMPARISON — JOB CHANGE
# =========================================================

def test_v3_job_change_2026_vs_2027(
    canonical_chart,
):
    analysis, result = _ask(
        canonical_chart,
        (
            "Is 2026 or 2027 better "
            "for changing jobs?"
        ),
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
        == "job_change"
    )

    assert (
        result[
            "route"
        ]
        == "calendar_year_comparison"
    )

    assert (
        result[
            "future_aware"
        ]
        is True
    )

    assert (
        result[
            "current_year_trimmed"
        ]
        is True
    )

    assert (
        result[
            "years"
        ]
        == [
            2026,
            2027,
        ]
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
        == 0.0
    )

    ranked = result[
        "ranked_results"
    ]

    assert (
        ranked[
            0
        ][
            "comparison_score"
        ]
        == 0.0
    )

    assert (
        ranked[
            1
        ][
            "comparison_score"
        ]
        == 0.0
    )

    assert (
        ranked[
            0
        ][
            "available"
        ]
        is False
    )

    assert (
        ranked[
            1
        ][
            "available"
        ]
        is False
    )


# =========================================================
# FOLLOW-UP CONTEXT
# =========================================================

def test_v3_follow_up_inherits_event(
    canonical_chart,
):
    first_analysis, first_result = _ask(
        canonical_chart,
        "When will I get promoted?",
    )

    previous_context = {
        "question_analysis": (
            first_analysis
        ),
        "route_result": (
            first_result
        ),
    }

    follow_analysis, follow_result = _ask(
        canonical_chart,
        "What about June?",
        previous_context=(
            previous_context
        ),
    )

    assert (
        follow_analysis[
            "query_mode"
        ]
        == "follow_up"
    )

    assert (
        follow_result[
            "route"
        ]
        == "follow_up_month"
    )

    assert (
        follow_result[
            "context_used"
        ]
        is True
    )

    assert (
        follow_result[
            "inherited_event"
        ]
        == "promotion_recognition"
    )

    assert (
        follow_result[
            "resolved_month"
        ][
            "month"
        ]
        == 6
    )

    assert (
        follow_result[
            "resolved_month"
        ][
            "year"
        ]
        == 2027
    )

    assert (
        follow_result[
            "resolved_month"
        ][
            "label"
        ]
        == "June 2027"
    )


# =========================================================
# RISK ROUTE
# =========================================================

def test_v3_employment_risk_route(
    canonical_chart,
):
    analysis, result = _ask(
        canonical_chart,
        (
            "Will I lose my job "
            "in the next 6 months?"
        ),
    )

    assert (
        analysis[
            "query_mode"
        ]
        == "risk"
    )

    assert (
        analysis[
            "primary_event"
        ]
        == "job_loss_risk"
    )

    assert (
        result[
            "route"
        ]
        == "employment_risk"
    )

    assert (
        result[
            "event"
        ]
        == "job_loss_risk"
    )

    assert (
        result[
            "job_loss_specific_signal"
        ]
        == "unconfirmed"
    )

    assert (
        result[
            "risk_basis"
        ]
        == (
            "employment_instability_and_restructuring"
        )
    )

    assert (
        result[
            "risk_analysis"
        ][
            "direct_job_loss_evidence_available"
        ]
        is False
    )