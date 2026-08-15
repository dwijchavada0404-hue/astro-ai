from __future__ import annotations

import pytest

from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)


# =========================================================
# SPOUSE PROFESSION — GENERAL OUTLOOK
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "What will my spouse do for work?",
        "What profession will my future spouse have?",
        "What kind of career will my future spouse have?",
    ],
)
def test_spouse_profession_general_outlook(
    question: str,
) -> None:

    result = analyze_marriage_question_v3(
        question
    )

    assert result[
        "primary_event"
    ] == "spouse_profession"

    assert result[
        "query_mode"
    ] == "single_event"

    assert result[
        "event_count"
    ] == 1

    assert result[
        "is_multi_event"
    ] is False

    assert result[
        "intent"
    ][
        "event"
    ] == "spouse_profession"

    assert result[
        "intent"
    ][
        "question_type"
    ] == "general_outlook"

    assert result[
        "intent"
    ][
        "direction"
    ] == "neutral"

    assert result[
        "intent"
    ][
        "confidence"
    ] >= 0.82


# =========================================================
# SPOUSE PROFESSION — TARGETED PROBABILITY
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "Will my spouse have a corporate job?",
        "Will my spouse work abroad?",
        "Could my spouse be a lawyer?",
        "Could my spouse be a consultant?",
        "Could my spouse be a designer?",
        "Could my spouse own a business?",
        "Will my spouse work in finance?",
        "Will my spouse work in technology?",
        "Could my spouse be a software engineer?",
        "Could my spouse be a banker?",
        "Could my spouse be an entrepreneur?",
    ],
)
def test_spouse_profession_probability_questions(
    question: str,
) -> None:

    result = analyze_marriage_question_v3(
        question
    )

    assert result[
        "primary_event"
    ] == "spouse_profession"

    assert result[
        "query_mode"
    ] == "single_event"

    assert result[
        "event_count"
    ] == 1

    assert result[
        "is_multi_event"
    ] is False

    assert result[
        "intent"
    ][
        "event"
    ] == "spouse_profession"

    assert result[
        "intent"
    ][
        "question_type"
    ] == "probability"

    assert result[
        "intent"
    ][
        "direction"
    ] == "neutral"

    assert result[
        "intent"
    ][
        "confidence"
    ] >= 0.82


# =========================================================
# SPOUSE TRAITS REGRESSION
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "What kind of person will I marry?",
        "What will my future spouse be like?",
    ],
)
def test_spouse_traits_not_confused_with_profession(
    question: str,
) -> None:

    result = analyze_marriage_question_v3(
        question
    )

    assert result[
        "primary_event"
    ] == "spouse_traits"

    assert result[
        "query_mode"
    ] == "single_event"

    assert result[
        "event_count"
    ] == 1

    assert result[
        "intent"
    ][
        "question_type"
    ] == "general_outlook"

    assert result[
        "intent"
    ][
        "direction"
    ] == "neutral"


# =========================================================
# SPOUSE MEETING REGRESSION
# =========================================================

def test_spouse_meeting_not_confused_with_profession() -> None:

    result = analyze_marriage_question_v3(
        "When will I meet my future spouse?"
    )

    assert result[
        "primary_event"
    ] == "spouse_meeting"

    assert result[
        "query_mode"
    ] == "single_event"

    assert result[
        "event_count"
    ] == 1

    assert result[
        "intent"
    ][
        "question_type"
    ] == "timing"

    assert result[
        "intent"
    ][
        "direction"
    ] == "occurrence"


# =========================================================
# MARRIAGE TIMING REGRESSION
# =========================================================

def test_marriage_timing_not_confused_with_profession() -> None:

    result = analyze_marriage_question_v3(
        "When will I get married?"
    )

    assert result[
        "primary_event"
    ] == "marriage_timing"

    assert result[
        "query_mode"
    ] == "single_event"

    assert result[
        "event_count"
    ] == 1

    assert result[
        "intent"
    ][
        "question_type"
    ] == "timing"

    assert result[
        "intent"
    ][
        "direction"
    ] == "occurrence"


# =========================================================
# LOVE VS ARRANGED REGRESSION
# =========================================================

def test_love_vs_arranged_not_confused_with_profession() -> None:

    result = analyze_marriage_question_v3(
        "Will I have a love marriage or arranged marriage?"
    )

    assert result[
        "primary_event"
    ] == "love_vs_arranged"

    assert result[
        "query_mode"
    ] == "single_event"

    assert result[
        "event_count"
    ] == 1

    assert result[
        "intent"
    ][
        "question_type"
    ] == "general_outlook"

    assert result[
        "intent"
    ][
        "direction"
    ] == "neutral"


# =========================================================
# EVENT LABEL REGRESSION
# =========================================================

def test_spouse_profession_event_label() -> None:

    result = analyze_marriage_question_v3(
        "What will my spouse do for work?"
    )

    assert result[
        "primary_event_label"
    ] == "Spouse Profession / Career Profile"

    assert result[
        "intent"
    ][
        "event_label"
    ] == "Spouse Profession / Career Profile"


# =========================================================
# NORMALISATION
# =========================================================

def test_spouse_profession_normalisation() -> None:

    result = analyze_marriage_question_v3(
        "   COULD   MY   SPOUSE   BE   A   CONSULTANT?   "
    )

    assert result[
        "normalised_question"
    ] == "could my spouse be a consultant?"

    assert result[
        "primary_event"
    ] == "spouse_profession"

    assert result[
        "intent"
    ][
        "question_type"
    ] == "probability"


# =========================================================
# INVALID INPUT
# =========================================================

def test_empty_question_rejected() -> None:

    with pytest.raises(
        ValueError
    ):

        analyze_marriage_question_v3(
            ""
        )


def test_non_string_question_rejected() -> None:

    with pytest.raises(
        ValueError
    ):

        analyze_marriage_question_v3(
            None  # type: ignore[arg-type]
        )
