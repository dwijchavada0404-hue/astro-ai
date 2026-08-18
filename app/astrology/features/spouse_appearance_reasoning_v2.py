from __future__ import annotations

from typing import Any

from app.astrology.features.spouse_appearance_reasoning_v1 import (
    analyze_spouse_appearance_v1,
)


# =========================================================
# CONSTANTS
# =========================================================

APPEARANCE_TARGET_LABELS = {
    "general": (
        "General Appearance"
    ),
    "height": (
        "Height"
    ),
    "build": (
        "Body Build"
    ),
    "attractiveness": (
        "Attractiveness"
    ),
    "facial_features": (
        "Facial Features"
    ),
    "eyes": (
        "Eyes / Expression"
    ),
    "youthfulness": (
        "Youthful Appearance"
    ),
    "maturity": (
        "Mature Appearance"
    ),
    "presence": (
        "Overall Presence"
    ),
}


# =========================================================
# TARGET THEME MAPS
# =========================================================

TARGET_POSITIVE_THEMES = {
    "height": (
        "tall or long-limbed appearance",
        "tall or slender build",
    ),

    "build": (
        "athletic or energetic appearance",
        "well-proportioned build",
        "slim or agile build",
        "slender build",
        "athletic build",
        "lean build",
        "lean or slender build",
        "well-built frame",
    ),

    "attractiveness": (
        "pleasant and attractive appearance",
        "attractive appearance",
        "balanced facial features",
        "pleasant facial features",
        "well-presented and balanced appearance",
        "striking appearance",
        "pleasant presence",
    ),

    "facial_features": (
        "sharp facial features",
        "soft facial features",
        "balanced facial features",
        "defined facial features",
        "pleasant facial features",
        "defined features",
    ),

    "eyes": (
        "intense eyes",
        "soft expressive eyes",
        "gentle expression",
    ),

    "youthfulness": (
        "youthful appearance",
    ),

    "maturity": (
        "mature appearance",
    ),

    "presence": (
        "confident presence",
        "striking appearance",
        "pleasant presence",
        "distinctive appearance",
        "unconventional features",
        "gentle appearance",
    ),
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_dict(
    value: Any,
) -> dict[str, Any]:

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def _safe_list(
    value: Any,
) -> list[Any]:

    if isinstance(
        value,
        list,
    ):
        return value

    return []


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _normalise_text(
    value: str,
) -> str:

    return " ".join(
        value.strip().lower().split()
    )


# =========================================================
# QUESTION TARGET DETECTION
# =========================================================

def _detect_target(
    question: str,
) -> dict[str, Any]:

    normalised = (
        _normalise_text(
            question
        )
    )

    target_patterns = (
        (
            "height",
            (
                "tall",
                "short",
                "height",
                "how tall",
                "long-limbed",
                "long limbed",
            ),
        ),

        (
            "build",
            (
                "athletic",
                "slim",
                "slender",
                "lean",
                "body type",
                "body build",
                "build",
                "physique",
                "well built",
                "well-built",
            ),
        ),

        (
            "attractiveness",
            (
                "attractive",
                "beautiful",
                "handsome",
                "good looking",
                "good-looking",
                "pretty",
                "appearance attractive",
            ),
        ),

        (
            "eyes",
            (
                "eyes",
                "eye",
                "expression",
            ),
        ),

        (
            "facial_features",
            (
                "facial features",
                "face",
                "sharp features",
                "soft features",
                "defined features",
            ),
        ),

        (
            "youthfulness",
            (
                "young looking",
                "young-looking",
                "youthful",
                "look younger",
                "younger than",
            ),
        ),

        (
            "maturity",
            (
                "mature looking",
                "mature-looking",
                "look mature",
                "older looking",
                "older-looking",
            ),
        ),

        (
            "presence",
            (
                "presence",
                "personality look",
                "striking",
                "distinctive",
                "confident appearance",
            ),
        ),
    )

    for (
        target,
        patterns,
    ) in target_patterns:

        matched = [
            pattern
            for pattern in patterns
            if pattern in normalised
        ]

        if matched:

            return {
                "target": (
                    target
                ),
                "target_label": (
                    APPEARANCE_TARGET_LABELS[
                        target
                    ]
                ),
                "matched_keywords": (
                    matched
                ),
            }

    return {
        "target": (
            "general"
        ),
        "target_label": (
            APPEARANCE_TARGET_LABELS[
                "general"
            ]
        ),
        "matched_keywords": [],
    }


# =========================================================
# QUESTION POLARITY
# =========================================================

def _detect_requested_polarity(
    question: str,
    target: str,
) -> str:

    normalised = (
        _normalise_text(
            question
        )
    )

    negative_patterns = {
        "height": (
            "short",
        ),
        "build": (
            "heavy",
            "stocky",
            "broad",
        ),
        "attractiveness": (
            "unattractive",
            "not attractive",
        ),
        "youthfulness": (
            "older looking",
            "older-looking",
        ),
        "maturity": (
            "young looking",
            "young-looking",
        ),
    }

    if any(
        pattern in normalised
        for pattern in negative_patterns.get(
            target,
            (),
        )
    ):

        return (
            "inverse"
        )

    return (
        "direct"
    )


# =========================================================
# TARGET EVIDENCE EXTRACTION
# =========================================================

def _extract_target_evidence(
    v1_result: dict[str, Any],
    target: str,
) -> list[dict[str, Any]]:

    indicators = _safe_list(
        v1_result.get(
            "indicators"
        )
    )

    if target == "general":

        return [
            item
            for item in indicators
            if isinstance(
                item,
                dict,
            )
        ]

    allowed_themes = set(
        TARGET_POSITIVE_THEMES.get(
            target,
            (),
        )
    )

    evidence = []

    for raw_item in indicators:

        item = _safe_dict(
            raw_item
        )

        theme = str(
            item.get(
                "theme",
                "",
            )
        )

        if theme in allowed_themes:

            evidence.append(
                item
            )

    return evidence


# =========================================================
# SUPPORT SCORE
# =========================================================

def _calculate_support_score(
    evidence: list[dict[str, Any]],
    target: str,
) -> float:

    if not evidence:

        return 0.20

    strengths = [
        _safe_float(
            item.get(
                "strength"
            )
        )
        for item in evidence
    ]

    strongest = max(
        strengths,
        default=0.0,
    )

    total = sum(
        strengths
    )

    breadth_bonus = min(
        max(
            len(
                evidence
            )
            - 1,
            0,
        )
        * 0.06,
        0.18,
    )

    score = (
        strongest * 0.72
        + min(
            total,
            1.80,
        )
        / 1.80
        * 0.18
        + breadth_bonus
    )

    if (
        target
        == "general"
    ):

        score += (
            0.08
        )

    return round(
        _clamp(
            score,
            0.0,
            0.92,
        ),
        3,
    )


# =========================================================
# SUPPORT CLASSIFICATION
# =========================================================

def _classify_support(
    score: float,
) -> tuple[
    str,
    str,
]:

    if score >= 0.72:

        return (
            "strong_support",
            "Strong Support",
        )

    if score >= 0.54:

        return (
            "moderate_support",
            "Moderate Support",
        )

    if score >= 0.34:

        return (
            "mild_support",
            "Mild Support",
        )

    return (
        "limited_support",
        "Limited Support",
    )


# =========================================================
# CONFIDENCE
# =========================================================

def _calculate_confidence(
    v1_result: dict[str, Any],
    evidence: list[dict[str, Any]],
    target: str,
) -> float:

    natal_confidence = (
        _safe_float(
            v1_result.get(
                "confidence"
            ),
            0.55,
        )
    )

    evidence_bonus = min(
        len(
            evidence
        )
        * 0.025,
        0.10,
    )

    confidence = (
        natal_confidence
        + evidence_bonus
    )

    if (
        target
        != "general"
        and not evidence
    ):

        confidence = min(
            confidence,
            0.58,
        )

    return round(
        _clamp(
            confidence,
            0.50,
            0.90,
        ),
        3,
    )


# =========================================================
# STRONGEST THEMES
# =========================================================

def _strongest_themes(
    evidence: list[dict[str, Any]],
) -> list[str]:

    theme_scores: dict[
        str,
        float,
    ] = {}

    for item in evidence:

        theme = str(
            item.get(
                "theme",
                "",
            )
        )

        if not theme:

            continue

        theme_scores[
            theme
        ] = (
            theme_scores.get(
                theme,
                0.0,
            )
            + _safe_float(
                item.get(
                    "strength"
                )
            )
        )

    ranked = sorted(
        theme_scores.items(),
        key=lambda item: (
            item[
                1
            ]
        ),
        reverse=True,
    )

    return [
        theme
        for (
            theme,
            _
        ) in ranked[
            :5
        ]
    ]


# =========================================================
# TARGET-SPECIFIC ANSWER
# =========================================================

def _build_target_answer(
    target: str,
    support_level: str,
    themes: list[str],
    polarity: str,
) -> str:

    if (
        target
        == "general"
    ):

        if themes:

            return (
                "The strongest appearance themes suggest "
                + ", ".join(
                    themes[
                        :3
                    ]
                )
                + "."
            )

        return (
            "The currently modelled chart factors do not "
            "produce a sufficiently specific spouse appearance "
            "profile."
        )

    target_label = (
        APPEARANCE_TARGET_LABELS.get(
            target,
            target,
        )
    )

    if (
        support_level
        == "strong_support"
    ):

        opening = (
            f"The chart gives relatively strong support for "
            f"the {target_label.lower()} theme asked about."
        )

    elif (
        support_level
        == "moderate_support"
    ):

        opening = (
            f"The chart gives moderate support for the "
            f"{target_label.lower()} theme asked about."
        )

    elif (
        support_level
        == "mild_support"
    ):

        opening = (
            f"The chart gives some support for the "
            f"{target_label.lower()} theme, although it is "
            "not dominant."
        )

    else:

        opening = (
            f"The currently modelled indicators provide limited "
            f"support for a specific {target_label.lower()} "
            "prediction."
        )

    if (
        polarity
        == "inverse"
    ):

        opening += (
            " The question asks about the opposite side of the "
            "main modelled appearance themes, so the result should "
            "be interpreted cautiously."
        )

    if themes:

        opening += (
            " The relevant themes are "
            + ", ".join(
                themes[
                    :3
                ]
            )
            + "."
        )

    return (
        opening
    )


# =========================================================
# LIMITATION TEXT
# =========================================================

def _build_limitation(
    target: str,
) -> str:

    if (
        target
        == "height"
    ):

        return (
            "Astrological appearance indicators are better treated "
            "as broad tendencies than as a precise prediction of "
            "physical height."
        )

    if (
        target
        == "attractiveness"
    ):

        return (
            "Attractiveness is subjective, so the model interprets "
            "this through broader themes such as harmony, pleasant "
            "features, presentation and visual presence."
        )

    if target in (
        "facial_features",
        "eyes",
    ):

        return (
            "The model can describe broad facial or expressive "
            "themes, but it cannot reliably predict exact facial "
            "geometry or individual physical details."
        )

    return (
        "Spouse appearance analysis represents broad symbolic "
        "tendencies and should not be interpreted as an exact "
        "physical description."
    )


# =========================================================
# MAIN V2 ENGINE
# =========================================================

def analyze_spouse_appearance_v2(
    chart: dict[str, Any],
    question: str,
) -> dict[str, Any]:

    if not isinstance(
        chart,
        dict,
    ):

        raise ValueError(
            "chart must be a dictionary."
        )

    if not isinstance(
        question,
        str,
    ):

        raise ValueError(
            "question must be a string."
        )

    normalised_question = (
        _normalise_text(
            question
        )
    )

    if not normalised_question:

        raise ValueError(
            "question must not be empty."
        )

    v1_result = (
        analyze_spouse_appearance_v1(
            chart
        )
    )

    if not v1_result.get(
        "available"
    ):

        return {
            "available": False,
            "event": (
                "spouse_appearance"
            ),
            "model_version": (
                "v2"
            ),
            "reason": (
                v1_result.get(
                    "reason",
                    "Natal spouse appearance analysis is unavailable.",
                )
            ),
            "natal_analysis": (
                v1_result
            ),
        }

    target_analysis = (
        _detect_target(
            normalised_question
        )
    )

    target = str(
        target_analysis.get(
            "target",
            "general",
        )
    )

    polarity = (
        _detect_requested_polarity(
            normalised_question,
            target,
        )
    )

    evidence = (
        _extract_target_evidence(
            v1_result,
            target,
        )
    )

    support_score = (
        _calculate_support_score(
            evidence,
            target,
        )
    )

    (
        support_level,
        support_label,
    ) = (
        _classify_support(
            support_score
        )
    )

    confidence = (
        _calculate_confidence(
            v1_result,
            evidence,
            target,
        )
    )

    strongest_themes = (
        _strongest_themes(
            evidence
        )
    )

    answer = (
        _build_target_answer(
            target,
            support_level,
            strongest_themes,
            polarity,
        )
    )

    limitation = (
        _build_limitation(
            target
        )
    )

    return {
        "available": True,

        "event": (
            "spouse_appearance"
        ),

        "model_version": (
            "v2"
        ),

        "question": (
            question
        ),

        "normalised_question": (
            normalised_question
        ),

        "target": (
            target
        ),

        "target_label": (
            target_analysis.get(
                "target_label"
            )
        ),

        "matched_keywords": (
            target_analysis.get(
                "matched_keywords",
                [],
            )
        ),

        "requested_polarity": (
            polarity
        ),

        "support_score": (
            support_score
        ),

        "support_level": (
            support_level
        ),

        "support_label": (
            support_label
        ),

        "confidence": (
            confidence
        ),

        "answer": (
            answer
        ),

        "summary": (
            answer
        ),

        "limitation": (
            limitation
        ),

        "strongest_themes": (
            strongest_themes
        ),

        "evidence_count": len(
            evidence
        ),

        "evidence": (
            evidence
        ),

        "natal_profile": {
            "appearance_themes": (
                v1_result.get(
                    "appearance_themes",
                    [],
                )
            ),

            "theme_scores": (
                v1_result.get(
                    "theme_scores",
                    {},
                )
            ),

            "chart_context": (
                v1_result.get(
                    "chart_context",
                    {},
                )
            ),
        },

        "natal_analysis": (
            v1_result
        ),
    }