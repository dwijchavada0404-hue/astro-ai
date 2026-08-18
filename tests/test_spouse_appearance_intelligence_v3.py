from __future__ import annotations

import pytest

from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)


# =========================================================
# GENERAL APPEARANCE DETECTION
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "What will my future spouse look like?",
        "What will my spouse look like?",
        "What will my partner look like?",
        "Describe my future spouse's appearance.",
        "What kind of appearance will my spouse have?",
    ],
)
def test_spouse_appearance_general_detection(
    question: str,
):

    result = (
        analyze_marriage_question_v3(
            question
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "spouse_appearance"
    )

    assert (
        result[
            "primary_event_label"
        ]
        == "Spouse Appearance / Physical Profile"
    )

    assert (
        result[
            "query_mode"
        ]
        == "single_event"
    )

    assert (
        result[
            "event_count"
        ]
        == 1
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
# TARGETED APPEARANCE DETECTION
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "Will my spouse be tall?",
        "Will my spouse be short?",
        "Will my spouse have a slim build?",
        "Will my spouse have an athletic build?",
        "Will my spouse be attractive?",
        "Could my spouse be handsome?",
        "Could my spouse be beautiful?",
        "Will my spouse have sharp features?",
        "What will my spouse's eyes look like?",
        "Will my spouse look youthful?",
        "Will my spouse look mature?",
        "Will my spouse have a striking presence?",
    ],
)
def test_spouse_appearance_targeted_detection(
    question: str,
):

    result = (
        analyze_marriage_question_v3(
            question
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "spouse_appearance"
    )

    assert (
        result[
            "query_mode"
        ]
        == "single_event"
    )


# =========================================================
# PROBABILITY TYPE
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "Will my spouse be tall?",
        "Could my spouse be attractive?",
        "Can my spouse have an athletic build?",
        "Would my spouse look youthful?",
    ],
)
def test_spouse_appearance_probability_question_type(
    question: str,
):

    result = (
        analyze_marriage_question_v3(
            question
        )
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
        == "neutral"
    )


# =========================================================
# CONFIDENCE
# =========================================================

def test_spouse_appearance_parser_confidence():

    result = (
        analyze_marriage_question_v3(
            "Will my spouse be attractive?"
        )
    )

    assert (
        result[
            "intent"
        ][
            "confidence"
        ]
        >= 0.82
    )


# =========================================================
# TRAITS REGRESSION
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "What kind of person will I marry?",
        "What kind of personality will my spouse have?",
        "What will my future spouse be like?",
        "Who will I marry?",
    ],
)
def test_spouse_appearance_does_not_hijack_traits(
    question: str,
):

    result = (
        analyze_marriage_question_v3(
            question
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "spouse_traits"
    )


# =========================================================
# PROFESSION REGRESSION
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "What will my spouse do for work?",
        "Will my spouse work abroad?",
        "Could my spouse be a lawyer?",
        "Could my spouse be a software engineer?",
    ],
)
def test_spouse_appearance_does_not_hijack_profession(
    question: str,
):

    result = (
        analyze_marriage_question_v3(
            question
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "spouse_profession"
    )


# =========================================================
# FOREIGN / INTERCULTURAL REGRESSION
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "Will my spouse be from another country?",
        "Will I marry a foreigner?",
        "Could my spouse be from a different culture?",
        "Could I have an interfaith marriage?",
    ],
)
def test_spouse_appearance_does_not_hijack_foreign(
    question: str,
):

    result = (
        analyze_marriage_question_v3(
            question
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "foreign_intercultural_connection"
    )


# =========================================================
# MEETING REGRESSION
# =========================================================

def test_spouse_appearance_does_not_hijack_meeting():

    result = (
        analyze_marriage_question_v3(
            "When will I meet my future spouse?"
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "spouse_meeting"
    )


# =========================================================
# MARRIAGE TIMING REGRESSION
# =========================================================

def test_spouse_appearance_does_not_hijack_marriage_timing():

    result = (
        analyze_marriage_question_v3(
            "When will I get married?"
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "marriage_timing"
    )


# =========================================================
# LOVE VS ARRANGED REGRESSION
# =========================================================

def test_spouse_appearance_does_not_hijack_love_vs_arranged():

    result = (
        analyze_marriage_question_v3(
            "Will I have a love marriage or arranged marriage?"
        )
    )

    assert (
        result[
            "primary_event"
        ]
        == "love_vs_arranged"
    )


# =========================================================
# MATCHED KEYWORD METADATA
# =========================================================

def test_spouse_appearance_preserves_detection_metadata():

    result = (
        analyze_marriage_question_v3(
            "Will my spouse be tall?"
        )
    )

    event = (
        result[
            "detected_events"
        ][
            0
        ]
    )

    assert (
        event[
            "event"
        ]
        == "spouse_appearance"
    )

    assert (
        "spouse height"
        in event[
            "matched_keywords"
        ]
    )


# =========================================================
# FOLLOW-UP BEHAVIOUR
# =========================================================

def test_spouse_appearance_follow_up_detection_stays_intact():

    result = (
        analyze_marriage_question_v3(
            "What about her appearance?"
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
            "requires_context"
        ]
        is True
    )