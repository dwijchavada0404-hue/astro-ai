from __future__ import annotations

import pytest

from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)


@pytest.mark.parametrize(
    "question",
    [
        "Will I marry a foreigner?",
        "Will I marry someone from another country?",
        "Will my spouse be from another country?",
        "Could my spouse be from a different country?",
        "Will my future spouse be from abroad?",
        "Will I have an intercultural marriage?",
        "Could I have a cross-cultural marriage?",
        "Will my spouse be from a different culture?",
        "Will I marry someone from another culture?",
        "Could my spouse have a different nationality?",
        "Will I marry someone from a different religion?",
        "Could I have an interfaith marriage?",
        "Will my spouse be from another state?",
        "Will I marry someone from a different region?",
        "Could my spouse be from a different community?",
    ],
)
def test_foreign_intercultural_detection(
    question: str,
):

    result = analyze_marriage_question_v3(
        question
    )

    assert (
        result["primary_event"]
        == "foreign_intercultural_connection"
    )

    assert (
        result["primary_event_label"]
        == "Foreign / Intercultural Relationship"
    )

    assert (
        result["query_mode"]
        == "single_event"
    )

    assert (
        result["event_count"]
        == 1
    )


@pytest.mark.parametrize(
    "question",
    [
        "Will I marry a foreigner?",
        "Could my spouse be from another country?",
        "Can I have an intercultural marriage?",
        "Would I marry someone from a different culture?",
    ],
)
def test_foreign_intercultural_probability_question_type(
    question: str,
):

    result = analyze_marriage_question_v3(
        question
    )

    assert (
        result["intent"]["question_type"]
        == "probability"
    )

    assert (
        result["intent"]["direction"]
        == "occurrence"
    )


def test_foreign_intercultural_general_outlook_question():

    result = analyze_marriage_question_v3(
        "Tell me about intercultural marriage in my chart."
    )

    assert (
        result["primary_event"]
        == "foreign_intercultural_connection"
    )

    assert (
        result["intent"]["question_type"]
        == "general_outlook"
    )


def test_foreign_intercultural_confidence():

    result = analyze_marriage_question_v3(
        "Will I marry someone from another country?"
    )

    assert (
        result["intent"]["confidence"]
        >= 0.82
    )


@pytest.mark.parametrize(
    "question",
    [
        "Will my spouse work abroad?",
        "Will my spouse have a job abroad?",
        "Could my spouse work overseas?",
        "Will my spouse have an international career?",
        "Will my spouse work internationally?",
    ],
)
def test_foreign_intercultural_does_not_hijack_profession(
    question: str,
):

    result = analyze_marriage_question_v3(
        question
    )

    assert (
        result["primary_event"]
        == "spouse_profession"
    )


@pytest.mark.parametrize(
    "question",
    [
        "What kind of person will I marry?",
        "What will my future spouse be like?",
        "Describe my future spouse.",
        "What personality will my spouse have?",
    ],
)
def test_foreign_intercultural_does_not_hijack_spouse_traits(
    question: str,
):

    result = analyze_marriage_question_v3(
        question
    )

    assert (
        result["primary_event"]
        == "spouse_traits"
    )


def test_foreign_intercultural_does_not_hijack_spouse_meeting():

    result = analyze_marriage_question_v3(
        "When will I meet my future spouse?"
    )

    assert (
        result["primary_event"]
        == "spouse_meeting"
    )

    assert (
        result["intent"]["question_type"]
        == "timing"
    )


def test_foreign_intercultural_does_not_hijack_marriage_timing():

    result = analyze_marriage_question_v3(
        "When will I get married?"
    )

    assert (
        result["primary_event"]
        == "marriage_timing"
    )


def test_foreign_intercultural_does_not_hijack_love_vs_arranged():

    result = analyze_marriage_question_v3(
        "Will I have a love marriage or arranged marriage?"
    )

    assert (
        result["primary_event"]
        == "love_vs_arranged"
    )


def test_foreign_intercultural_preserves_matched_keywords():

    result = analyze_marriage_question_v3(
        "Will my spouse be from another country?"
    )

    event = result["detected_events"][0]

    assert (
        event["event"]
        == "foreign_intercultural_connection"
    )

    assert (
        "spouse from another country"
        in event["matched_keywords"]
    )


def test_foreign_intercultural_follow_up_detection_remains_intact():

    result = analyze_marriage_question_v3(
        "What about another country?"
    )

    assert (
        result["query_mode"]
        == "follow_up"
    )

    assert (
        result["follow_up"]["requires_context"]
        is True
    )
