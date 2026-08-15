import pytest

from app.astrology.features.marriage_question_intelligence_v2 import (
    analyze_marriage_question_v2,
)


# =========================================================
# MARRIAGE TIMING
# =========================================================

def test_marriage_timing_question():

    result = (
        analyze_marriage_question_v2(
            "When will I get married?"
        )
    )

    assert (
        result[
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        result[
            "primary_event"
        ]
        == "marriage_timing"
    )

    assert (
        result[
            "intent"
        ][
            "question_type"
        ]
        == "timing"
    )

    assert (
        result[
            "intent"
        ][
            "direction"
        ]
        == "occurrence"
    )


# =========================================================
# RELATIONSHIP COMMITMENT
# =========================================================

def test_relationship_commitment_question():

    result = (
        analyze_marriage_question_v2(
            (
                "Will I get into a serious relationship "
                "in the next 6 months?"
            )
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "relationship_commitment"
    )

    assert (
        result[
            "intent"
        ][
            "question_type"
        ]
        == "probability"
    )

    assert (
        result[
            "forecast_horizon"
        ]
        == {
            "type": "months",
            "value": 6,
        }
    )


# =========================================================
# SPOUSE TRAITS
# =========================================================

def test_spouse_traits_question():

    result = (
        analyze_marriage_question_v2(
            "What will my future spouse be like?"
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "spouse_traits"
    )

    assert (
        result[
            "intent"
        ][
            "question_type"
        ]
        == "general_outlook"
    )

    assert (
        result[
            "intent"
        ][
            "direction"
        ]
        == "neutral"
    )


# =========================================================
# MARRIAGE DELAY
# =========================================================

def test_marriage_delay_question():

    result = (
        analyze_marriage_question_v2(
            "Why is my marriage delayed?"
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "marriage_delay_challenge"
    )

    assert (
        result[
            "intent"
        ][
            "question_type"
        ]
        == "general_outlook"
    )


# =========================================================
# RELATIONSHIP STABILITY
# =========================================================

def test_relationship_stability_question():

    result = (
        analyze_marriage_question_v2(
            "Will my relationship last?"
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "relationship_stability"
    )

    assert (
        result[
            "intent"
        ][
            "question_type"
        ]
        == "probability"
    )

    assert (
        result[
            "intent"
        ][
            "direction"
        ]
        == "increase"
    )


# =========================================================
# FOREIGN / INTERCULTURAL
# =========================================================

def test_intercultural_marriage_question():

    result = (
        analyze_marriage_question_v2(
            (
                "Will I marry someone from "
                "a different culture?"
            )
        )
    )

    assert (
        result[
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        result[
            "primary_event"
        ]
        == "foreign_intercultural_connection"
    )

    assert (
        result[
            "event_count"
        ]
        == 1
    )


# =========================================================
# CALENDAR YEAR
# =========================================================

def test_marriage_calendar_year_question():

    result = (
        analyze_marriage_question_v2(
            "Will I marry in 2027?"
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "marriage_timing"
    )

    assert (
        result[
            "forecast_horizon"
        ]
        == {
            "type": "calendar_year",
            "year": 2027,
        }
    )


# =========================================================
# FOLLOW-UP
# =========================================================

def test_follow_up_question():

    result = (
        analyze_marriage_question_v2(
            "What about next year?"
        )
    )

    assert (
        result[
            "query_mode"
        ]
        == "follow_up"
    )

    assert (
        result[
            "follow_up"
        ][
            "is_follow_up"
        ]
        is True
    )

    assert (
        result[
            "follow_up"
        ][
            "requires_context"
        ]
        is True
    )

    assert (
        result[
            "forecast_horizon"
        ]
        == {
            "type": "years",
            "value": 1,
        }
    )


# =========================================================
# MULTI EVENT
# =========================================================

def test_multi_event_question():

    result = (
        analyze_marriage_question_v2(
            (
                "Will I get married and have "
                "a stable relationship?"
            )
        )
    )

    assert (
        result[
            "query_mode"
        ]
        == "multi_event"
    )

    events = [
        item[
            "event"
        ]
        for item
        in result[
            "detected_events"
        ]
    ]

    assert (
        "marriage_timing"
        in events
    )

    assert (
        "relationship_stability"
        in events
    )


# =========================================================
# EMPTY QUESTION
# =========================================================

def test_empty_question_rejected():

    with pytest.raises(
        ValueError
    ):
        analyze_marriage_question_v2(
            "   "
        )