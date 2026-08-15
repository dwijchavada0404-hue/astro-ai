import re
from typing import Any


# =========================================================
# SUPPORTED CAREER EVENTS
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
    "general_career": (
        "General Career Forecast"
    ),
}


# =========================================================
# KEYWORD GROUPS
# =========================================================

JOB_CHANGE_KEYWORDS = (
    "job change",
    "switch job",
    "switch jobs",
    "switch company",
    "change company",
    "new job",
    "new company",
    "leave my job",
    "leave the job",
    "leave job",
    "resign",
    "resignation",
    "career change",
    "career transition",
    "change career",
    "another job",
    "another company",
)


PROMOTION_KEYWORDS = (
    "promotion",
    "promoted",
    "get promoted",
    "recognition",
    "career growth",
    "designation",
    "higher position",
    "senior role",
    "leadership role",
    "professional recognition",
)


INCOME_KEYWORDS = (
    "salary",
    "salary increase",
    "salary hike",
    "hike",
    "increment",
    "income",
    "income increase",
    "pay rise",
    "pay raise",
    "compensation",
    "earn more",
    "earning",
    "financial growth",
)


FOREIGN_KEYWORDS = (
    "foreign job",
    "foreign opportunity",
    "abroad",
    "overseas",
    "international job",
    "international opportunity",
    "international company",
    "foreign company",
    "relocation",
    "relocate",
    "move abroad",
    "work abroad",
    "onsite",
)


PRESSURE_KEYWORDS = (
    "career pressure",
    "job pressure",
    "work pressure",
    "workload",
    "stress at work",
    "work stress",
    "career stress",
    "difficult career",
    "job difficulty",
    "career challenge",
    "work challenge",
)


# =========================================================
# REGEX EVENT PATTERNS
# =========================================================

JOB_CHANGE_PATTERNS = (
    r"\bchange\s+(?:my\s+|the\s+|a\s+)?job\b",
    r"\bswitch\s+(?:my\s+|the\s+|a\s+)?job\b",
    r"\bswitch\s+(?:my\s+|the\s+)?company\b",
    r"\bchange\s+(?:my\s+|the\s+)?company\b",
    r"\bmove\s+to\s+(?:a\s+)?new\s+job\b",
    r"\bmove\s+to\s+another\s+job\b",
    r"\bmove\s+to\s+(?:a\s+)?new\s+company\b",
    r"\bmove\s+to\s+another\s+company\b",
    r"\bget\s+(?:a\s+)?new\s+job\b",
    r"\bfind\s+(?:a\s+)?new\s+job\b",
)


PROMOTION_PATTERNS = (
    r"\bget\s+promoted\b",
    r"\bbe\s+promoted\b",
    r"\breceive\s+(?:a\s+)?promotion\b",
)


INCOME_PATTERNS = (
    r"\bsalary\s+(?:will\s+)?increase\b",
    r"\bincrease\s+(?:in\s+)?(?:my\s+)?salary\b",
    r"\bget\s+(?:a\s+)?(?:salary\s+)?hike\b",
    r"\bget\s+(?:an\s+)?increment\b",
    r"\bearn\s+more\b",
)


FOREIGN_PATTERNS = (
    r"\bget\s+(?:a\s+)?foreign\s+job\b",
    r"\bwork\s+in\s+another\s+country\b",
    r"\bmove\s+abroad\b",
    r"\bwork\s+abroad\b",
    r"\bjob\s+abroad\b",
)


PRESSURE_PATTERNS = (
    r"\bwork\s+pressure\b",
    r"\bjob\s+pressure\b",
    r"\bcareer\s+pressure\b",
    r"\bpressure\s+at\s+work\b",
    r"\bstress\s+at\s+work\b",
)


# =========================================================
# QUESTION TYPE KEYWORDS
# =========================================================

WHEN_KEYWORDS = (
    "when",
    "what time",
    "which month",
    "which year",
    "how soon",
)


WILL_KEYWORDS = (
    "will",
    "can i",
    "chance",
    "chances",
    "possibility",
    "likely",
    "possible",
)


HOW_KEYWORDS = (
    "how is",
    "how will",
    "how does",
    "how would",
    "what will",
    "what is my career",
)


# =========================================================
# DIRECTION KEYWORDS
# =========================================================

INCREASE_KEYWORDS = (
    "increase",
    "increase in",
    "rise",
    "grow",
    "growth",
    "improve",
    "improvement",
    "more",
    "higher",
    "hike",
    "increment",
    "gain",
    "gains",
)


DECREASE_KEYWORDS = (
    "reduce",
    "reduced",
    "decrease",
    "decline",
    "less",
    "lower",
    "ease",
    "easier",
    "relief",
    "drop",
    "come down",
)


CHANGE_KEYWORDS = (
    "change",
    "switch",
    "move",
    "transition",
    "resign",
    "leave",
)


# =========================================================
# TEXT HELPERS
# =========================================================

def _normalise_text(
    question: str,
) -> str:
    text = question.strip().lower()

    text = re.sub(
        r"[^\w\s?'-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _contains_keyword(
    text: str,
    keywords: tuple[str, ...],
) -> bool:
    """
    Match complete words or phrases rather than
    arbitrary substrings.

    This prevents cases such as:

        "ease" matching inside "increase"

    while still supporting phrases such as:

        "work pressure"
        "can i"
        "come down"
    """

    for keyword in keywords:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text,
        ):
            return True

    return False


def _find_keyword_matches(
    text: str,
    keywords: tuple[str, ...],
) -> list[str]:
    """
    Return only complete-word / complete-phrase
    keyword matches.
    """

    matches: list[str] = []

    for keyword in keywords:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text,
        ):
            matches.append(
                keyword
            )

    return matches


def _pattern_matches(
    text: str,
    patterns: tuple[str, ...],
) -> list[str]:
    matches: list[str] = []

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )

        if match:
            matches.append(
                match.group(0)
            )

    return matches


# =========================================================
# EVENT IDENTIFICATION
# =========================================================

def _identify_event(
    text: str,
) -> tuple[str, float, list[str]]:
    """
    Identify the most likely career event.

    Both fixed keywords and flexible regex patterns
    are used so natural wording such as:

        change my job
        switch the job
        get promoted
        get a foreign job

    can be recognised reliably.
    """

    event_keywords = {
        "job_change": (
            JOB_CHANGE_KEYWORDS
        ),
        "promotion_recognition": (
            PROMOTION_KEYWORDS
        ),
        "income_gains": (
            INCOME_KEYWORDS
        ),
        "foreign_international_opportunity": (
            FOREIGN_KEYWORDS
        ),
        "career_pressure_challenge": (
            PRESSURE_KEYWORDS
        ),
    }

    event_patterns = {
        "job_change": (
            JOB_CHANGE_PATTERNS
        ),
        "promotion_recognition": (
            PROMOTION_PATTERNS
        ),
        "income_gains": (
            INCOME_PATTERNS
        ),
        "foreign_international_opportunity": (
            FOREIGN_PATTERNS
        ),
        "career_pressure_challenge": (
            PRESSURE_PATTERNS
        ),
    }

    scores: dict[
        str,
        dict[str, Any],
    ] = {}

    for event_name, keywords in (
        event_keywords.items()
    ):

        keyword_matches = (
            _find_keyword_matches(
                text,
                keywords,
            )
        )

        regex_matches = (
            _pattern_matches(
                text,
                event_patterns.get(
                    event_name,
                    (),
                ),
            )
        )

        all_matches = list(
            dict.fromkeys(
                keyword_matches
                + regex_matches
            )
        )

        if all_matches:

            scores[
                event_name
            ] = {
                "matches": all_matches,
                "score": (
                    len(keyword_matches)
                    + (
                        len(regex_matches)
                        * 1.25
                    )
                ),
            }

    if not scores:
        return (
            "general_career",
            0.60,
            [],
        )

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            -float(
                item[1]["score"]
            ),
            item[0],
        ),
    )

    event_name = ranked[0][0]

    matches = ranked[0][1][
        "matches"
    ]

    raw_score = float(
        ranked[0][1][
            "score"
        ]
    )

    confidence = min(
        0.75
        + (
            raw_score
            * 0.05
        ),
        0.95,
    )

    return (
        event_name,
        round(
            confidence,
            2,
        ),
        matches,
    )


# =========================================================
# QUESTION TYPE
# =========================================================

def _identify_question_type(
    text: str,
) -> str:
    if _contains_keyword(
        text,
        WHEN_KEYWORDS,
    ):
        return "timing"

    if _contains_keyword(
        text,
        WILL_KEYWORDS,
    ):
        return "probability"

    if _contains_keyword(
        text,
        HOW_KEYWORDS,
    ):
        return "general_outlook"

    return "general_outlook"


# =========================================================
# DIRECTION
# =========================================================

def _identify_direction(
    text: str,
    event: str,
) -> str:
    """
    Determine whether the user is asking about
    increase, decrease, change or occurrence.

    Examples:

        salary increase
            -> increase

        work pressure reduce
            -> decrease

        change my job
            -> change

        when will I get promoted
            -> increase

        foreign job
            -> occurrence
    """

    if event == "job_change":
        return "change"

    if event == (
        "promotion_recognition"
    ):
        return "increase"

    if event == (
        "foreign_international_opportunity"
    ):
        return "occurrence"

    if _contains_keyword(
        text,
        DECREASE_KEYWORDS,
    ):
        return "decrease"

    if _contains_keyword(
        text,
        INCREASE_KEYWORDS,
    ):
        return "increase"

    if _contains_keyword(
        text,
        CHANGE_KEYWORDS,
    ):
        return "change"

    return "neutral"


# =========================================================
# EXPLICIT YEAR
# =========================================================

def _extract_year(
    text: str,
) -> int | None:
    matches = re.findall(
        r"\b(20\d{2}|21\d{2})\b",
        text,
    )

    if not matches:
        return None

    try:
        return int(
            matches[0]
        )

    except ValueError:
        return None


# =========================================================
# MONTH HORIZON
# =========================================================

def _extract_month_horizon(
    text: str,
) -> int | None:
    patterns = (
        r"(?:next|within|in)\s+(\d+)\s+months?",
        r"(\d+)\s+months?\s+(?:from now|ahead)",
    )

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )

        if match:

            try:
                months = int(
                    match.group(1)
                )

            except ValueError:
                continue

            if months > 0:
                return months

    return None


# =========================================================
# YEAR HORIZON
# =========================================================

def _extract_year_horizon(
    text: str,
) -> int | None:
    patterns = (
        r"(?:next|within|in)\s+(\d+)\s+years?",
        r"(\d+)\s+years?\s+(?:from now|ahead)",
    )

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )

        if match:

            try:
                years = int(
                    match.group(1)
                )

            except ValueError:
                continue

            if years > 0:
                return years

    return None


# =========================================================
# NATURAL HORIZONS
# =========================================================

def _natural_horizon(
    text: str,
) -> dict[str, Any]:
    if (
        "next month" in text
        or "coming month" in text
    ):
        return {
            "type": "months",
            "value": 1,
        }

    if (
        "next 3 months" in text
        or "next three months" in text
    ):
        return {
            "type": "months",
            "value": 3,
        }

    if (
        "next 6 months" in text
        or "next six months" in text
        or "coming 6 months" in text
        or "coming six months" in text
    ):
        return {
            "type": "months",
            "value": 6,
        }

    if (
        "next year" in text
        or "coming year" in text
    ):
        return {
            "type": "years",
            "value": 1,
        }

    return {
        "type": "months",
        "value": 12,
    }


# =========================================================
# FORECAST HORIZON
# =========================================================

def _identify_horizon(
    text: str,
) -> dict[str, Any]:
    explicit_year = (
        _extract_year(
            text
        )
    )

    if explicit_year is not None:
        return {
            "type": "calendar_year",
            "year": explicit_year,
        }

    months = (
        _extract_month_horizon(
            text
        )
    )

    if months is not None:
        return {
            "type": "months",
            "value": months,
        }

    years = (
        _extract_year_horizon(
            text
        )
    )

    if years is not None:
        return {
            "type": "years",
            "value": years,
        }

    return _natural_horizon(
        text
    )


# =========================================================
# SCAN RESOLUTION
# =========================================================

def _recommended_step_days(
    horizon: dict[str, Any],
) -> int:
    horizon_type = horizon.get(
        "type"
    )

    if horizon_type == (
        "calendar_year"
    ):
        return 7

    if horizon_type == "months":

        months = int(
            horizon.get(
                "value",
                12,
            )
        )

        if months <= 3:
            return 3

        if months <= 12:
            return 7

        return 14

    if horizon_type == "years":

        years = int(
            horizon.get(
                "value",
                1,
            )
        )

        if years <= 1:
            return 7

        if years <= 3:
            return 14

        return 30

    return 7


# =========================================================
# MAIN PARSER
# =========================================================

def parse_career_question(
    question: str,
) -> dict[str, Any]:
    """
    Parse a natural-language career question into
    deterministic forecast instructions.

    This module performs no astrology calculations.
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

    (
        event,
        event_confidence,
        matched_keywords,
    ) = _identify_event(
        text
    )

    question_type = (
        _identify_question_type(
            text
        )
    )

    direction = (
        _identify_direction(
            text,
            event,
        )
    )

    horizon = (
        _identify_horizon(
            text
        )
    )

    step_days = (
        _recommended_step_days(
            horizon
        )
    )

    return {
        "available": True,

        "original_question": (
            question
        ),

        "normalised_question": (
            text
        ),

        "intent": {
            "domain": "career",

            "event": (
                event
            ),

            "event_label": (
                EVENT_LABELS.get(
                    event,
                    event,
                )
            ),

            "question_type": (
                question_type
            ),

            "direction": (
                direction
            ),

            "confidence": (
                event_confidence
            ),

            "matched_keywords": (
                matched_keywords
            ),
        },

        "forecast_horizon": (
            horizon
        ),

        "recommended_step_days": (
            step_days
        ),
    }