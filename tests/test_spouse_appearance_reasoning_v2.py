from __future__ import annotations

from typing import Any

import pytest

from app.astrology.features.spouse_appearance_reasoning_v2 import (
    analyze_spouse_appearance_v2,
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
# BASIC CONTRACT
# =========================================================

def test_spouse_appearance_v2_basic_contract():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "What will my future spouse look like?",
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
        == "spouse_appearance"
    )

    assert (
        result[
            "model_version"
        ]
        == "v2"
    )

    assert (
        result[
            "target"
        ]
        == "general"
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
            "confidence"
        ],
        float,
    )


# =========================================================
# TARGET DETECTION
# =========================================================

@pytest.mark.parametrize(
    (
        "question",
        "expected_target",
    ),
    [
        (
            "Will my spouse be tall?",
            "height",
        ),
        (
            "Will my spouse have a slim build?",
            "build",
        ),
        (
            "Will my spouse be attractive?",
            "attractiveness",
        ),
        (
            "What kind of facial features will my spouse have?",
            "facial_features",
        ),
        (
            "What will my spouse's eyes look like?",
            "eyes",
        ),
        (
            "Will my spouse look youthful?",
            "youthfulness",
        ),
        (
            "Will my spouse look mature?",
            "maturity",
        ),
        (
            "Will my spouse have a striking presence?",
            "presence",
        ),
    ],
)
def test_spouse_appearance_v2_target_detection(
    question: str,
    expected_target: str,
):

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            question,
        )
    )

    assert (
        result[
            "target"
        ]
        == expected_target
    )


# =========================================================
# GENERAL QUESTION
# =========================================================

def test_spouse_appearance_v2_general_question():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "Describe my future spouse's appearance.",
        )
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

    assert isinstance(
        result[
            "strongest_themes"
        ],
        list,
    )

    assert (
        result[
            "evidence_count"
        ]
        > 0
    )


# =========================================================
# HEIGHT TARGET
# =========================================================

def test_spouse_appearance_v2_height_target():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "Will my spouse be tall?",
        )
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
        0.0
        <= result[
            "support_score"
        ]
        <= 0.92
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
# BUILD TARGET
# =========================================================

def test_spouse_appearance_v2_build_target():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "Will my spouse have a lean build?",
        )
    )

    assert (
        result[
            "target"
        ]
        == "build"
    )

    assert (
        result[
            "evidence_count"
        ]
        > 0
    )

    assert any(
        item.get(
            "theme"
        )
        in (
            "lean build",
            "lean or slender build",
        )
        for item in result[
            "evidence"
        ]
    )


# =========================================================
# ATTRACTIVENESS TARGET
# =========================================================

def test_spouse_appearance_v2_attractiveness_target():

    chart = (
        _reference_chart()
    )

    chart[
        "planets"
    ][
        "Venus"
    ][
        "house"
    ] = 7

    chart[
        "planets"
    ][
        "Venus"
    ][
        "sign"
    ] = "Capricorn"

    result = (
        analyze_spouse_appearance_v2(
            chart,
            "Will my spouse be attractive?",
        )
    )

    assert (
        result[
            "target"
        ]
        == "attractiveness"
    )

    assert (
        result[
            "evidence_count"
        ]
        > 0
    )

    assert any(
        item.get(
            "theme"
        )
        == "attractive appearance"
        for item in result[
            "evidence"
        ]
    )

    assert (
        "subjective"
        in result[
            "limitation"
        ].lower()
    )


# =========================================================
# FACIAL FEATURES
# =========================================================

def test_spouse_appearance_v2_facial_features():

    chart = (
        _reference_chart()
    )

    chart[
        "planets"
    ][
        "Mars"
    ][
        "house"
    ] = 7

    chart[
        "planets"
    ][
        "Mars"
    ][
        "sign"
    ] = "Capricorn"

    result = (
        analyze_spouse_appearance_v2(
            chart,
            "Will my spouse have defined facial features?",
        )
    )

    assert (
        result[
            "target"
        ]
        == "facial_features"
    )

    assert (
        result[
            "evidence_count"
        ]
        > 0
    )


# =========================================================
# INVERSE POLARITY
# =========================================================

def test_spouse_appearance_v2_short_height_inverse_polarity():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "Will my spouse be short?",
        )
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
# NO TARGET EVIDENCE
# =========================================================

def test_spouse_appearance_v2_no_target_evidence_is_cautious():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "Will my spouse be tall?",
        )
    )

    if (
        result[
            "evidence_count"
        ]
        == 0
    ):

        assert (
            result[
                "support_level"
            ]
            == "limited_support"
        )

        assert (
            result[
                "confidence"
            ]
            <= 0.58
        )


# =========================================================
# NATAL PROFILE PROPAGATION
# =========================================================

def test_spouse_appearance_v2_natal_profile():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "What will my future spouse look like?",
        )
    )

    natal_profile = (
        result[
            "natal_profile"
        ]
    )

    assert isinstance(
        natal_profile[
            "appearance_themes"
        ],
        list,
    )

    assert isinstance(
        natal_profile[
            "theme_scores"
        ],
        dict,
    )

    assert (
        natal_profile[
            "chart_context"
        ][
            "seventh_house"
        ][
            "sign"
        ]
        == "Capricorn"
    )


# =========================================================
# NATAL ANALYSIS PROPAGATION
# =========================================================

def test_spouse_appearance_v2_natal_analysis():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "Will my spouse look mature?",
        )
    )

    assert (
        result[
            "natal_analysis"
        ][
            "event"
        ]
        == "spouse_appearance"
    )

    assert (
        result[
            "natal_analysis"
        ][
            "model_version"
        ]
        == "v1"
    )


# =========================================================
# MISSING 7TH HOUSE
# =========================================================

def test_spouse_appearance_v2_missing_seventh_house():

    result = (
        analyze_spouse_appearance_v2(
            {
                "houses": {},
                "planets": {},
            },
            "What will my spouse look like?",
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
        == "spouse_appearance"
    )

    assert (
        result[
            "model_version"
        ]
        == "v2"
    )

    assert (
        "reason"
        in result
    )


# =========================================================
# INPUT VALIDATION
# =========================================================

def test_spouse_appearance_v2_rejects_non_dict_chart():

    with pytest.raises(
        ValueError,
        match="chart must be a dictionary",
    ):

        analyze_spouse_appearance_v2(
            [],
            "What will my spouse look like?",
        )


def test_spouse_appearance_v2_rejects_non_string_question():

    with pytest.raises(
        ValueError,
        match="question must be a string",
    ):

        analyze_spouse_appearance_v2(
            _reference_chart(),
            None,
        )


def test_spouse_appearance_v2_rejects_empty_question():

    with pytest.raises(
        ValueError,
        match="question must not be empty",
    ):

        analyze_spouse_appearance_v2(
            _reference_chart(),
            "   ",
        )


# =========================================================
# CONFIDENCE BOUNDS
# =========================================================

def test_spouse_appearance_v2_confidence_is_bounded():

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            "What will my spouse look like?",
        )
    )

    assert (
        0.50
        <= result[
            "confidence"
        ]
        <= 0.90
    )


# =========================================================
# SUPPORT SCORE BOUNDS
# =========================================================

@pytest.mark.parametrize(
    "question",
    [
        "Will my spouse be tall?",
        "Will my spouse have an athletic build?",
        "Will my spouse be attractive?",
        "Will my spouse look youthful?",
        "Will my spouse look mature?",
        "Will my spouse have a striking presence?",
    ],
)
def test_spouse_appearance_v2_support_score_is_bounded(
    question: str,
):

    result = (
        analyze_spouse_appearance_v2(
            _reference_chart(),
            question,
        )
    )

    assert (
        0.0
        <= result[
            "support_score"
        ]
        <= 0.92
    )