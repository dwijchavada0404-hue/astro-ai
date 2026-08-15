import re
from typing import Any

from app.astrology.features.career_question_parser import (
    parse_career_question,
)


# =========================================================
# EVENT DEFINITIONS
# =========================================================

EVENT_LABELS = {
    "job_change": (
        "Job Change / Professional Transition"
    ),
    "promotion_recognition": (
        "Promotion / Recognition"
    ),
    "income_gains": (
        "Income / Professional Gains"
    ),
    "foreign_international_opportunity": (
        "Foreign / International Opportunity"
    ),
    "career_pressure_challenge": (
        "Career Pressure / Challenge"
    ),
    "job_loss_risk": (
        "Job Loss / Employment Risk"
    ),
    "general_career": (
        "General Career Forecast"
    ),
}


EVENT_KEYWORDS = {
    "job_change": [
        "change job",
        "change my job",
        "change jobs",
        "changing job",
        "changing jobs",
        "changing my job",
        "switch job",
        "switch jobs",
        "switch my job",
        "switching job",
        "switching jobs",
        "switching my job",
        "new job",
        "another job",
        "leave my job",
        "leave job",
        "leaving my job",
        "leaving job",
        "career change",
        "changing career",
        "job change",
        "job switch",
        "change company",
        "switch company",
        "changing company",
        "switching company",
    ],

    "promotion_recognition": [
        "promotion",
        "promoted",
        "get promoted",
        "getting promoted",
        "recognition",
        "designation",
        "higher position",
        "senior position",
        "career growth",
    ],

    "income_gains": [
        "salary",
        "salary increase",
        "salary hike",
        "pay hike",
        "increment",
        "income",
        "income increase",
        "earn more",
        "earning more",
        "higher salary",
        "better salary",
        "compensation",
        "bonus",
    ],

    "foreign_international_opportunity": [
        "foreign job",
        "overseas job",
        "international job",
        "abroad",
        "foreign opportunity",
        "international opportunity",
        "relocate abroad",
        "relocation abroad",
        "work abroad",
        "working abroad",
        "move abroad",
        "moving abroad",
        "onsite",
        "on-site",
    ],

    "career_pressure_challenge": [
        "work pressure",
        "job pressure",
        "career pressure",
        "workload",
        "stress at work",
        "work stress",
        "job stress",
        "professional pressure",
    ],

    "job_loss_risk": [
        "lose my job",
        "lose job",
        "losing my job",
        "losing job",
        "job loss",
        "get fired",
        "getting fired",
        "be fired",
        "fired from",
        "laid off",
        "layoff",
        "lay off",
        "termination",
        "terminated",
        "unemployed",
        "lose employment",
    ],
}


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _normalise_text(
    question: str,
) -> str:
    text = question.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


# =========================================================
# EVENT DETECTION
# =========================================================

def _detect_events(
    text: str,
) -> list[dict[str, Any]]:
    """
    Detect every career event mentioned in the question.

    Unlike the original parser, this intentionally returns
    multiple events when more than one is present.
    """

    detected = []

    for (
        event,
        keywords,
    ) in EVENT_KEYWORDS.items():

        matched = []

        for keyword in keywords:

            if keyword in text:
                matched.append(
                    keyword
                )

        if matched:

            detected.append(
                {
                    "event": (
                        event
                    ),
                    "event_label": (
                        EVENT_LABELS[
                            event
                        ]
                    ),
                    "matched_keywords": (
                        matched
                    ),
                }
            )

    return detected


# =========================================================
# COMPARISON DETECTION
# =========================================================

def _extract_years(
    text: str,
) -> list[int]:

    raw_years = re.findall(
        r"\b(20\d{2})\b",
        text,
    )

    years = []

    for raw in raw_years:

        year = int(
            raw
        )

        if year not in years:
            years.append(
                year
            )

    return years


def _detect_comparison(
    text: str,
) -> dict[str, Any]:

    years = _extract_years(
        text
    )

    comparison_words = (
        "better",
        "best",
        "which year",
        "which period",
        " or ",
        "compare",
        "compared",
        "versus",
        " vs ",
    )

    has_comparison_language = any(
        word in text
        for word in comparison_words
    )

    if (
        len(years) >= 2
        and has_comparison_language
    ):
        return {
            "is_comparison": True,
            "comparison_type": (
                "calendar_years"
            ),
            "values": (
                years
            ),
        }

    return {
        "is_comparison": False,
        "comparison_type": None,
        "values": [],
    }


# =========================================================
# MONTH / FOLLOW-UP DETECTION
# =========================================================

def _detect_month_reference(
    text: str,
) -> dict[str, Any]:

    matches = []

    for (
        month_name,
        month_number,
    ) in MONTHS.items():

        if re.search(
            rf"\b{month_name}\b",
            text,
        ):
            matches.append(
                {
                    "name": (
                        month_name.title()
                    ),
                    "month": (
                        month_number
                    ),
                }
            )

    return {
        "available": bool(
            matches
        ),
        "months": (
            matches
        ),
    }


def _detect_follow_up_style(
    text: str,
    month_reference: dict[str, Any],
) -> bool:
    """
    Detect questions which depend heavily on prior context.

    Examples:

        What about November?
        And February?
        What about next year?
        Is October better?
    """

    patterns = (
        r"^what about\b",
        r"^how about\b",
        r"^and what about\b",
        r"^and\s+[a-z]+",
        r"^what if\b",
        r"^then what about\b",
    )

    if any(
        re.search(
            pattern,
            text,
        )
        for pattern in patterns
    ):
        return True

    word_count = len(
        text.split()
    )

    if (
        word_count <= 4
        and month_reference.get(
            "available"
        )
    ):
        return True

    return False


# =========================================================
# NEGATIVE / RISK DETECTION
# =========================================================

def _detect_risk_question(
    text: str,
    detected_events: list[dict[str, Any]],
) -> dict[str, Any]:

    risk_keywords = (
        "lose",
        "loss",
        "losing",
        "fired",
        "fire me",
        "laid off",
        "layoff",
        "terminated",
        "termination",
        "unemployed",
        "risk",
        "danger",
        "bad for career",
    )

    risk_language = any(
        keyword in text
        for keyword in risk_keywords
    )

    has_job_loss_event = any(
        item.get(
            "event"
        ) == "job_loss_risk"
        for item in detected_events
    )

    return {
        "is_risk_question": (
            risk_language
            or has_job_loss_event
        ),
        "risk_event": (
            "job_loss_risk"
            if has_job_loss_event
            else None
        ),
    }


# =========================================================
# QUESTION STRUCTURE
# =========================================================

def _detect_multi_event(
    detected_events: list[dict[str, Any]],
) -> bool:

    meaningful_events = {
        item.get(
            "event"
        )
        for item in detected_events
        if item.get(
            "event"
        )
    }

    return (
        len(
            meaningful_events
        )
        > 1
    )


def _classify_complexity(
    *,
    is_comparison: bool,
    is_multi_event: bool,
    is_follow_up: bool,
    is_risk: bool,
) -> str:

    score = sum(
        [
            bool(
                is_comparison
            ),
            bool(
                is_multi_event
            ),
            bool(
                is_follow_up
            ),
            bool(
                is_risk
            ),
        ]
    )

    if score >= 2:
        return "complex"

    if score == 1:
        return "enhanced"

    return "standard"


# =========================================================
# PRIMARY EVENT RESOLUTION
# =========================================================

def _resolve_primary_event(
    base_parse: dict[str, Any],
    detected_events: list[dict[str, Any]],
) -> str:
    """
    Resolve the event which best represents the question.

    Job-loss risk receives priority because treating
    "Will I lose my job?" as ordinary job change would
    reverse the meaning of the question.
    """

    for item in detected_events:

        if item.get(
            "event"
        ) == "job_loss_risk":
            return "job_loss_risk"

    base_intent = _safe_dict(
        base_parse.get(
            "intent"
        )
    )

    base_event = base_intent.get(
        "event"
    )

    detected_names = [
        item.get(
            "event"
        )
        for item in detected_events
        if item.get(
            "event"
        )
    ]

    if (
        base_event
        and base_event
        != "general_career"
        and base_event
        in detected_names
    ):
        return str(
            base_event
        )

    if detected_names:
        return str(
            detected_names[0]
        )

    if (
        base_event
        and base_event
        != "general_career"
    ):
        return str(
            base_event
        )

    return "general_career"


# =========================================================
# QUERY MODE
# =========================================================

def _resolve_query_mode(
    *,
    comparison: dict[str, Any],
    multi_event: bool,
    follow_up: bool,
    risk: dict[str, Any],
) -> str:

    if follow_up:
        return "follow_up"

    if comparison.get(
        "is_comparison"
    ):
        return "comparison"

    if multi_event:
        return "multi_event"

    if risk.get(
        "is_risk_question"
    ):
        return "risk"

    return "single_event"


# =========================================================
# MAIN V3 QUESTION INTELLIGENCE
# =========================================================

def analyze_career_question_v3(
    question: str,
) -> dict[str, Any]:
    """
    Analyse the structure of a career question before
    forecast calculation.

    V3 sits above the existing deterministic career parser.

    It adds support for:

        multiple events
        year comparisons
        negative / job-loss questions
        follow-up style questions
        explicit month references

    This module does not calculate astrology.
    """

    if not isinstance(
        question,
        str,
    ):
        raise ValueError(
            "question must be a string."
        )

    if not question.strip():
        raise ValueError(
            "question must not be empty."
        )

    text = _normalise_text(
        question
    )

    base_parse = (
        parse_career_question(
            question
        )
    )

    detected_events = (
        _detect_events(
            text
        )
    )

    comparison = (
        _detect_comparison(
            text
        )
    )

    month_reference = (
        _detect_month_reference(
            text
        )
    )

    follow_up = (
        _detect_follow_up_style(
            text,
            month_reference,
        )
    )

    risk = (
        _detect_risk_question(
            text,
            detected_events,
        )
    )

    multi_event = (
        _detect_multi_event(
            detected_events
        )
    )

    primary_event = (
        _resolve_primary_event(
            base_parse,
            detected_events,
        )
    )

    query_mode = (
        _resolve_query_mode(
            comparison=(
                comparison
            ),
            multi_event=(
                multi_event
            ),
            follow_up=(
                follow_up
            ),
            risk=(
                risk
            ),
        )
    )

    complexity = (
        _classify_complexity(
            is_comparison=(
                comparison.get(
                    "is_comparison",
                    False,
                )
            ),
            is_multi_event=(
                multi_event
            ),
            is_follow_up=(
                follow_up
            ),
            is_risk=(
                risk.get(
                    "is_risk_question",
                    False,
                )
            ),
        )
    )

    requires_context = bool(
        follow_up
    )

    return {
        "available": True,

        "original_question": (
            question
        ),

        "normalised_question": (
            text
        ),

        "query_mode": (
            query_mode
        ),

        "complexity": (
            complexity
        ),

        "primary_event": (
            primary_event
        ),

        "primary_event_label": (
            EVENT_LABELS.get(
                primary_event,
                primary_event,
            )
        ),

        "detected_events": (
            detected_events
        ),

        "event_count": (
            len(
                detected_events
            )
        ),

        "is_multi_event": (
            multi_event
        ),

        "comparison": (
            comparison
        ),

        "month_reference": (
            month_reference
        ),

        "risk": (
            risk
        ),

        "follow_up": {
            "is_follow_up": (
                follow_up
            ),
            "requires_context": (
                requires_context
            ),
        },

        "base_parser": (
            base_parse
        ),
    }