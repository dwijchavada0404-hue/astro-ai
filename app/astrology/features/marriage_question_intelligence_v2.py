import re
from typing import Any


# =========================================================
# EVENT LABELS
# =========================================================

EVENT_LABELS = {
    "marriage_timing": "Marriage Timing",
    "relationship_commitment": "Relationship / Commitment",
    "spouse_traits": "Spouse Traits / Partner Profile",
    "marriage_delay_challenge": "Marriage Delay / Challenge",
    "relationship_stability": "Relationship Stability",
    "foreign_intercultural_connection": (
        "Foreign / Intercultural Relationship"
    ),
    "general_marriage": (
        "General Marriage / Relationship Outlook"
    ),
}


# =========================================================
# EVENT KEYWORDS
# =========================================================

EVENT_KEYWORDS = {
    "marriage_timing": [
        "when will i marry",
        "when will i get married",
        "when will i be married",
        "when am i likely to marry",
        "marriage timing",
        "marriage date",
        "marriage year",
        "get married",
        "getting married",
    ],

    "relationship_commitment": [
        "serious relationship",
        "committed relationship",
        "commitment",
        "engagement",
        "engaged",
        "relationship turn serious",
        "relationship become serious",
        "settle down",
    ],

    "spouse_traits": [
        "future spouse",
        "future husband",
        "future wife",
        "spouse personality",
        "spouse traits",
        "partner personality",
        "partner traits",
        "what will my spouse be like",
        "what kind of spouse",
        "what kind of partner",
    ],

    "marriage_delay_challenge": [
        "delay in marriage",
        "marriage delay",
        "marriage delayed",
        "late marriage",
        "why am i not married",
        "why is my marriage delayed",
        "why is marriage delayed",
        "obstacles in marriage",
        "marriage obstacles",
        "difficulty getting married",
    ],

    "relationship_stability": [
        "stable relationship",
        "relationship stability",
        "relationship last",
        "will my relationship last",
        "will our relationship last",
        "marriage stable",
        "stable marriage",
        "relationship problems",
        "marital problems",
        "relationship survive",
    ],

    "foreign_intercultural_connection": [
        "foreign spouse",
        "foreign husband",
        "foreign wife",
        "foreign partner",
        "different culture",
        "different nationality",
        "different religion",
        "different country",
        "intercultural marriage",
        "inter-cultural marriage",
        "intercaste marriage",
        "inter-caste marriage",
        "international partner",
        "international spouse",
        "overseas spouse",
        "someone from abroad",
    ],
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _normalise_text(
    text: str,
) -> str:
    text = text.strip().lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def _unique(
    values: list[Any],
) -> list[Any]:
    result = []

    for value in values:

        if value not in result:
            result.append(
                value
            )

    return result


# =========================================================
# FORECAST HORIZON
# =========================================================

def _detect_forecast_horizon(
    text: str,
) -> dict[str, Any]:

    month_match = re.search(
        r"\bnext\s+(\d+)\s+months?\b",
        text,
    )

    if month_match:

        return {
            "type": "months",
            "value": int(
                month_match.group(
                    1
                )
            ),
        }

    year_count_match = re.search(
        r"\bnext\s+(\d+)\s+years?\b",
        text,
    )

    if year_count_match:

        return {
            "type": "years",
            "value": int(
                year_count_match.group(
                    1
                )
            ),
        }

    if re.search(
        r"\bnext year\b",
        text,
    ):

        return {
            "type": "years",
            "value": 1,
        }

    calendar_year_match = re.search(
        r"\b(20\d{2})\b",
        text,
    )

    if calendar_year_match:

        return {
            "type": "calendar_year",
            "year": int(
                calendar_year_match.group(
                    1
                )
            ),
        }

    return {
        "type": "months",
        "value": 12,
    }


# =========================================================
# QUESTION TYPE
# =========================================================

def _detect_question_type(
    text: str,
) -> str:
    """
    Determine whether the question asks for:

        timing
        probability
        general_outlook

    Ordering matters.

    Example:

        "What will my future spouse be like?"

    contains "will my", but it is clearly an explanatory
    / descriptive question rather than a yes-no
    probability question.
    """

    # -----------------------------------------------------
    # TIMING QUESTIONS
    # -----------------------------------------------------

    if re.search(
        r"\bwhen\b",
        text,
    ):
        return "timing"

    # -----------------------------------------------------
    # DESCRIPTIVE / EXPLANATORY QUESTIONS
    # -----------------------------------------------------

    if re.match(
        (
            r"^(what|how|why)\b"
        ),
        text,
    ):
        return "general_outlook"

    # -----------------------------------------------------
    # YES / NO / POSSIBILITY QUESTIONS
    # -----------------------------------------------------

    if re.search(
        (
            r"\bwill\s+(?:i|my|we|our)\b"
            r"|\bcan\s+(?:i|my|we|our)\b"
            r"|\bcould\s+(?:i|my|we|our)\b"
            r"|\bis there\b"
            r"|\bare there\b"
            r"|\bdo i\b"
            r"|\bdoes my\b"
        ),
        text,
    ):
        return "probability"

    return "general_outlook"


# =========================================================
# DIRECTION
# =========================================================

def _detect_direction(
    text: str,
    event: str,
) -> str:

    if event in (
        "marriage_timing",
        "relationship_commitment",
        "foreign_intercultural_connection",
    ):
        return "occurrence"

    if event == "marriage_delay_challenge":

        if re.search(
            (
                r"\breduce\b"
                r"|\bend\b"
                r"|\bresolve\b"
                r"|\bovercome\b"
                r"|\bimprove\b"
            ),
            text,
        ):
            return "decrease"

        return "increase"

    if event == "relationship_stability":

        if re.search(
            (
                r"\bimprove\b"
                r"|\bstable\b"
                r"|\bstronger\b"
                r"|\blast\b"
                r"|\bsurvive\b"
            ),
            text,
        ):
            return "increase"

        if re.search(
            (
                r"\bworse\b"
                r"|\bbreak\b"
                r"|\bend\b"
                r"|\bunstable\b"
                r"|\bseparate\b"
            ),
            text,
        ):
            return "decrease"

        return "neutral"

    if event == "spouse_traits":
        return "neutral"

    return "neutral"


# =========================================================
# KEYWORD EVENT DETECTION
# =========================================================

def _detect_keyword_events(
    text: str,
) -> list[dict[str, Any]]:

    detected = []

    for (
        event_name,
        keywords,
    ) in EVENT_KEYWORDS.items():

        matched = []

        for keyword in keywords:

            if keyword in text:

                matched.append(
                    keyword
                )

        matched = _unique(
            matched
        )

        if matched:

            detected.append(
                {
                    "event": (
                        event_name
                    ),

                    "event_label": (
                        EVENT_LABELS[
                            event_name
                        ]
                    ),

                    "matched_keywords": (
                        matched
                    ),
                }
            )

    return detected


# =========================================================
# GENERIC MARRIAGE TIMING
# =========================================================

def _detect_generic_marriage_timing(
    text: str,
    detected_events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Detect generic marriage occurrence questions such as:

        Will I marry in 2027?
        Will I marry next year?

    But avoid treating 'marry' as a separate event when
    the real subject is more specific:

        Will I marry someone from a different culture?
    """

    existing_events = {
        str(
            item.get(
                "event"
            )
        )
        for item in detected_events
    }

    if "marriage_timing" in existing_events:
        return detected_events

    generic_pattern = re.search(
        (
            r"\bwill i marry\b"
            r"|\bcan i marry\b"
            r"|\bwill i be married\b"
        ),
        text,
    )

    if not generic_pattern:
        return detected_events

    specific_events = {
        "foreign_intercultural_connection",
        "spouse_traits",
        "marriage_delay_challenge",
        "relationship_stability",
    }

    if existing_events.intersection(
        specific_events
    ):
        return detected_events

    result = list(
        detected_events
    )

    result.append(
        {
            "event": (
                "marriage_timing"
            ),

            "event_label": (
                EVENT_LABELS[
                    "marriage_timing"
                ]
            ),

            "matched_keywords": [
                generic_pattern.group(
                    0
                )
            ],
        }
    )

    return result


# =========================================================
# EVENT DETECTION
# =========================================================

def _detect_events(
    text: str,
) -> list[dict[str, Any]]:

    detected = (
        _detect_keyword_events(
            text
        )
    )

    detected = (
        _detect_generic_marriage_timing(
            text,
            detected,
        )
    )

    return detected


# =========================================================
# PRIMARY EVENT
# =========================================================

def _select_primary_event(
    detected_events: list[dict[str, Any]],
    text: str,
) -> str:

    if not detected_events:
        return "general_marriage"

    event_names = [
        str(
            item.get(
                "event"
            )
        )
        for item in detected_events
    ]

    priority = [
        "marriage_delay_challenge",
        "foreign_intercultural_connection",
        "spouse_traits",
        "relationship_stability",
        "relationship_commitment",
        "marriage_timing",
    ]

    for event_name in priority:

        if event_name in event_names:
            return event_name

    return str(
        detected_events[
            0
        ].get(
            "event",
            "general_marriage",
        )
    )


# =========================================================
# FOLLOW-UP DETECTION
# =========================================================

def _is_follow_up(
    text: str,
    detected_events: list[dict[str, Any]],
) -> bool:

    if detected_events:
        return False

    follow_up_patterns = [
        r"\bwhat about\b",
        r"\band then\b",
        r"\bafter that\b",
        r"\bwhat about next year\b",
        r"\bwhat about later\b",
    ]

    return any(
        re.search(
            pattern,
            text,
        )
        for pattern in follow_up_patterns
    )


# =========================================================
# QUERY MODE
# =========================================================

def _detect_query_mode(
    text: str,
    detected_events: list[dict[str, Any]],
) -> str:

    if _is_follow_up(
        text,
        detected_events,
    ):
        return "follow_up"

    if len(
        detected_events
    ) >= 2:
        return "multi_event"

    return "single_event"


# =========================================================
# COMPLEXITY
# =========================================================

def _detect_complexity(
    query_mode: str,
    detected_events: list[dict[str, Any]],
) -> str:

    if (
        query_mode
        != "single_event"
        or len(
            detected_events
        )
        > 1
    ):
        return "enhanced"

    return "standard"


# =========================================================
# CONFIDENCE
# =========================================================

def _confidence_score(
    primary_event: str,
    detected_events: list[dict[str, Any]],
) -> float:

    if primary_event == "general_marriage":
        return 0.60

    matched_count = 0

    for item in detected_events:

        if item.get(
            "event"
        ) == primary_event:

            matched_count = len(
                item.get(
                    "matched_keywords",
                    [],
                )
            )

            break

    if matched_count >= 2:
        return 0.91

    if matched_count == 1:
        return 0.82

    return 0.70


# =========================================================
# STEP-DAY RECOMMENDATION
# =========================================================

def _recommended_step_days(
    question_type: str,
    horizon: dict[str, Any],
) -> int:

    if (
        question_type == "timing"
        and horizon.get(
            "type"
        )
        == "months"
        and int(
            horizon.get(
                "value",
                12,
            )
            or 12
        )
        <= 6
    ):
        return 3

    return 7


# =========================================================
# FOLLOW-UP METADATA
# =========================================================

def _follow_up_metadata(
    query_mode: str,
) -> dict[str, Any]:

    is_follow_up = (
        query_mode
        == "follow_up"
    )

    return {
        "is_follow_up": (
            is_follow_up
        ),

        "requires_context": (
            is_follow_up
        ),
    }


# =========================================================
# MAIN INTELLIGENCE FUNCTION
# =========================================================

def analyze_marriage_question_v2(
    question: str,
) -> dict[str, Any]:
    """
    Deterministic natural-language intelligence layer
    for marriage and relationship questions.

    No astrology is calculated here.

    The parser determines:

        query mode
        primary event
        detected events
        question type
        direction
        confidence
        forecast horizon
        recommended scan resolution
        follow-up requirements
    """

    if not isinstance(
        question,
        str,
    ):
        raise ValueError(
            "question must be a string."
        )

    normalised = (
        _normalise_text(
            question
        )
    )

    if not normalised:

        raise ValueError(
            "question must not be empty."
        )

    detected_events = (
        _detect_events(
            normalised
        )
    )

    primary_event = (
        _select_primary_event(
            detected_events,
            normalised,
        )
    )

    query_mode = (
        _detect_query_mode(
            normalised,
            detected_events,
        )
    )

    question_type = (
        _detect_question_type(
            normalised
        )
    )

    direction = (
        _detect_direction(
            normalised,
            primary_event,
        )
    )

    horizon = (
        _detect_forecast_horizon(
            normalised
        )
    )

    confidence = (
        _confidence_score(
            primary_event,
            detected_events,
        )
    )

    step_days = (
        _recommended_step_days(
            question_type,
            horizon,
        )
    )

    return {
        "available": True,

        "original_question": (
            question
        ),

        "normalised_question": (
            normalised
        ),

        "query_mode": (
            query_mode
        ),

        "complexity": (
            _detect_complexity(
                query_mode,
                detected_events,
            )
        ),

        "primary_event": (
            primary_event
        ),

        "primary_event_label": (
            EVENT_LABELS[
                primary_event
            ]
        ),

        "detected_events": (
            detected_events
        ),

        "event_count": len(
            detected_events
        ),

        "is_multi_event": (
            len(
                detected_events
            )
            >= 2
        ),

        "intent": {
            "domain": (
                "marriage"
            ),

            "event": (
                primary_event
            ),

            "event_label": (
                EVENT_LABELS[
                    primary_event
                ]
            ),

            "question_type": (
                question_type
            ),

            "direction": (
                direction
            ),

            "confidence": (
                confidence
            ),
        },

        "forecast_horizon": (
            horizon
        ),

        "recommended_step_days": (
            step_days
        ),

        "follow_up": (
            _follow_up_metadata(
                query_mode
            )
        ),
    }