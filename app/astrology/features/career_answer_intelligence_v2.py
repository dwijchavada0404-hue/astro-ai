from typing import Any


# =========================================================
# EVENT LABELS
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


def _event_data(
    forecast: dict[str, Any],
    event_name: str,
) -> dict[str, Any]:
    events = _safe_dict(
        forecast.get(
            "events"
        )
    )

    return _safe_dict(
        events.get(
            event_name
        )
    )


def _window(
    event_data: dict[str, Any],
) -> dict[str, Any]:
    return _safe_dict(
        event_data.get(
            "window"
        )
    )


def _normalise_strength(
    value: Any,
) -> str:
    return str(
        value
        or "no_strong_window"
    )


def _normalise_confirmation(
    value: Any,
) -> str:
    return str(
        value
        or "none"
    )


# =========================================================
# OVERLAP DETECTION
# =========================================================

def _windows_overlap(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:

    first_start = first.get(
        "start"
    )

    first_end = first.get(
        "end"
    )

    second_start = second.get(
        "start"
    )

    second_end = second.get(
        "end"
    )

    values = (
        first_start,
        first_end,
        second_start,
        second_end,
    )

    if not all(
        isinstance(
            value,
            str,
        )
        and value
        for value in values
    ):
        return False

    return (
        first_start
        <= second_end
        and second_start
        <= first_end
    )


def _collect_overlaps(
    forecast: dict[str, Any],
    target_event: str,
    target_window: dict[str, Any],
) -> list[dict[str, Any]]:

    if not target_window:
        return []

    events = _safe_dict(
        forecast.get(
            "events"
        )
    )

    overlaps = []

    for (
        event_name,
        raw_event,
    ) in events.items():

        if event_name == target_event:
            continue

        event_data = _safe_dict(
            raw_event
        )

        if not event_data.get(
            "available"
        ):
            continue

        event_window = _window(
            event_data
        )

        if not _windows_overlap(
            target_window,
            event_window,
        ):
            continue

        role = "context"

        if event_name in (
            "promotion_recognition",
            "income_gains",
            "foreign_international_opportunity",
        ):
            role = "supportive"

        elif event_name == (
            "career_pressure_challenge"
        ):
            role = "challenging"

        elif event_name == (
            "job_change"
        ):
            role = "transition"

        overlaps.append(
            {
                "event": (
                    event_name
                ),
                "label": (
                    event_data.get(
                        "label",
                        EVENT_LABELS.get(
                            event_name,
                            event_name,
                        ),
                    )
                ),
                "role": (
                    role
                ),
                "outlook": (
                    event_data.get(
                        "outlook"
                    )
                ),
                "confidence": (
                    event_data.get(
                        "confidence"
                    )
                ),
                "start": (
                    event_window.get(
                        "start"
                    )
                ),
                "end": (
                    event_window.get(
                        "end"
                    )
                ),
                "peak_date": (
                    event_window.get(
                        "peak_date"
                    )
                ),
                "confirmation": (
                    event_window.get(
                        "confirmation"
                    )
                ),
            }
        )

    return overlaps


# =========================================================
# PROBABILITY CLASSIFICATION
# =========================================================

def _classify_probability(
    strength: str,
    confirmation: str,
) -> dict[str, Any]:
    """
    Convert forecast strength + confirmation type into
    a practical answer classification.

    This does not create new astrology.
    It interprets existing forecast output.
    """

    strength = _normalise_strength(
        strength
    )

    confirmation = (
        _normalise_confirmation(
            confirmation
        )
    )

    if (
        strength == "very_strong"
        and confirmation
        == "strong_confirmation"
    ):
        return {
            "level": (
                "strongly_likely"
            ),
            "score": 0.90,
            "language": (
                "strongly supported"
            ),
        }

    if (
        strength in (
            "very_strong",
            "strong",
        )
        and confirmation
        in (
            "confirmed",
            "strong_confirmation",
        )
    ):
        return {
            "level": (
                "likely"
            ),
            "score": 0.80,
            "language": (
                "well supported"
            ),
        }

    if (
        strength in (
            "strong",
            "moderate",
        )
        and confirmation
        == "dasha_only"
    ):
        return {
            "level": (
                "possible_but_not_confirmed"
            ),
            "score": 0.60,
            "language": (
                "possible, but not fully confirmed"
            ),
        }

    if (
        strength in (
            "strong",
            "moderate",
        )
        and confirmation
        == "transit_only"
    ):
        return {
            "level": (
                "temporary_or_transit_driven"
            ),
            "score": 0.50,
            "language": (
                "active mainly through transits"
            ),
        }

    if strength == "moderate":
        return {
            "level": (
                "moderately_supported"
            ),
            "score": 0.55,
            "language": (
                "moderately supported"
            ),
        }

    if strength in (
        "supportive",
        "active",
    ):
        return {
            "level": (
                "theme_active"
            ),
            "score": 0.45,
            "language": (
                "active as a theme"
            ),
        }

    if strength == "weak":
        return {
            "level": (
                "weak_signal"
            ),
            "score": 0.25,
            "language": (
                "weakly supported"
            ),
        }

    return {
        "level": (
            "no_clear_signal"
        ),
        "score": 0.15,
        "language": (
            "not clearly supported"
        ),
    }


# =========================================================
# SUPPORT / CHALLENGE FACTORS
# =========================================================

def _build_overlap_factors(
    overlaps: list[dict[str, Any]],
) -> tuple[
    list[str],
    list[str],
]:

    supporting = []

    challenging = []

    for item in overlaps:

        event_name = item.get(
            "event"
        )

        if event_name == (
            "career_pressure_challenge"
        ):
            challenging.append(
                "The same period overlaps with elevated "
                "career pressure, workload or responsibility."
            )

        elif event_name == (
            "foreign_international_opportunity"
        ):
            supporting.append(
                "Foreign or international career themes "
                "are active during part of the same period."
            )

        elif event_name == (
            "promotion_recognition"
        ):
            supporting.append(
                "Recognition or promotion themes overlap "
                "part of the same career window."
            )

        elif event_name == (
            "income_gains"
        ):
            supporting.append(
                "A separate professional-gains signal "
                "overlaps the same period."
            )

        elif event_name == (
            "job_change"
        ):
            supporting.append(
                "Professional transition themes overlap "
                "the same period."
            )

    return (
        supporting,
        challenging,
    )


# =========================================================
# EVENT-SPECIFIC NARRATIVE
# =========================================================

def _build_event_answer(
    event: str,
    direction: str,
    question_type: str,
    probability: dict[str, Any],
    window: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> str:

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak = window.get(
        "peak_date"
    )

    language = probability.get(
        "language"
    )

    if event == "job_change":

        answer = (
            f"A job change or professional transition is "
            f"{language} in the requested period. "
            f"The strongest window runs from {start} to {end}, "
            f"with peak activation around {peak}."
        )

        if any(
            item.get(
                "event"
            )
            == "career_pressure_challenge"
            for item in overlaps
        ):
            answer += (
                " The transition period also overlaps with "
                "higher professional pressure, so movement may "
                "be connected with restructuring, dissatisfaction, "
                "heavier responsibility or an active desire to change."
            )

        return answer

    if event == (
        "promotion_recognition"
    ):

        if question_type == "timing":
            return (
                f"The strongest promotion or recognition "
                f"window runs from {start} to {end}, "
                f"with peak activation around {peak}. "
                f"The signal is {language}."
            )

        return (
            f"Promotion or professional recognition is "
            f"{language} in the requested period. "
            f"The strongest window runs from {start} to {end}, "
            f"with peak activation around {peak}."
        )

    if event == "income_gains":

        return (
            f"Income or professional gains are "
            f"{language} in the requested period. "
            f"The strongest window runs from {start} to {end}, "
            f"with peak activation around {peak}."
        )

    if event == (
        "foreign_international_opportunity"
    ):

        answer = (
            f"A foreign or international-career opportunity is "
            f"{language} in the requested period. "
            f"The strongest window runs from {start} to {end}, "
            f"with peak activation around {peak}."
        )

        if probability.get(
            "level"
        ) == (
            "possible_but_not_confirmed"
        ):
            answer += (
                " The underlying Dasha supports the theme, "
                "but event-specific transits do not yet confirm "
                "it strongly enough to treat relocation or an "
                "overseas opportunity as highly likely."
            )

        return answer

    if event == (
        "career_pressure_challenge"
    ):

        if direction == "decrease":

            return (
                "Work pressure does not appear to reduce "
                "immediately. The strongest pressure window "
                f"runs from {start} to {end}, with peak "
                f"activation around {peak}. After this window "
                "ends, the specific elevated-pressure signal "
                "becomes weaker within the scanned period."
            )

        return (
            f"Career pressure is {language} during the "
            f"period from {start} to {end}, with peak "
            f"activation around {peak}."
        )

    return (
        "A relevant career event is active in the "
        "requested forecast period."
    )


# =========================================================
# NO-WINDOW ANSWER
# =========================================================

def _build_no_window_answer(
    event: str,
    direction: str,
) -> str:

    if (
        event == "income_gains"
        and direction == "increase"
    ):
        return (
            "The forecast does not identify a sufficiently "
            "strong standalone salary or income-growth window "
            "in the requested period. This means the present "
            "Dasha-transit combination does not provide enough "
            "independent confirmation to highlight a specific "
            "income-growth phase."
        )

    if event == (
        "promotion_recognition"
    ):
        return (
            "No sufficiently strong promotion or recognition "
            "window was identified in the requested period."
        )

    if event == "job_change":
        return (
            "No sufficiently strong job-change or professional-"
            "transition window was identified in the requested period."
        )

    if event == (
        "foreign_international_opportunity"
    ):
        return (
            "No sufficiently strong foreign or international-career "
            "window was identified in the requested period."
        )

    if event == (
        "career_pressure_challenge"
    ):
        return (
            "No distinct elevated career-pressure window was "
            "identified in the requested period."
        )

    return (
        "No sufficiently strong event-specific signal was "
        "identified in the requested period."
    )


# =========================================================
# GENERAL CAREER
# =========================================================

def _build_general_answer(
    forecast: dict[str, Any],
) -> dict[str, Any]:

    overall = _safe_dict(
        forecast.get(
            "overall"
        )
    )

    return {
        "available": True,

        "answer_type": (
            "general_career"
        ),

        "event": (
            "general_career"
        ),

        "event_label": (
            EVENT_LABELS[
                "general_career"
            ]
        ),

        "outcome": (
            overall.get(
                "outlook"
            )
        ),

        "probability_level": (
            "general_outlook"
        ),

        "probability_score": None,

        "confidence": (
            overall.get(
                "confidence"
            )
        ),

        "answer": (
            overall.get(
                "summary",
                (
                    "No clear general career forecast "
                    "was available."
                ),
            )
        ),

        "primary_window": {},

        "window": {},

        "supporting_factors": [],

        "challenging_factors": [],

        "overlapping_events": [],
    }


# =========================================================
# MAIN V2 ENGINE
# =========================================================

def generate_career_question_answer_v2(
    parsed_question: dict[str, Any],
    forecast: dict[str, Any],
) -> dict[str, Any]:
    """
    Career Answer Intelligence V2.

    This layer distinguishes:

        strong probability
        moderate probability
        active theme
        Dasha-only support
        transit-only support
        weak or absent signals
        positive / challenging overlaps

    It does not calculate new astrology.
    """

    if not isinstance(
        parsed_question,
        dict,
    ):
        raise ValueError(
            "parsed_question must be a dictionary."
        )

    if not isinstance(
        forecast,
        dict,
    ):
        raise ValueError(
            "forecast must be a dictionary."
        )

    intent = _safe_dict(
        parsed_question.get(
            "intent"
        )
    )

    event = str(
        intent.get(
            "event",
            "general_career",
        )
    )

    event_label = str(
        intent.get(
            "event_label",
            EVENT_LABELS.get(
                event,
                event,
            ),
        )
    )

    direction = str(
        intent.get(
            "direction",
            "neutral",
        )
    )

    question_type = str(
        intent.get(
            "question_type",
            "general_outlook",
        )
    )

    parser_confidence = float(
        intent.get(
            "confidence",
            0.0,
        )
        or 0.0
    )

    if event == "general_career":

        general = _build_general_answer(
            forecast
        )

        general[
            "parser_confidence"
        ] = parser_confidence

        general[
            "direction"
        ] = direction

        general[
            "question_type"
        ] = question_type

        return general

    target = _event_data(
        forecast,
        event,
    )

    available = bool(
        target.get(
            "available"
        )
    )

    forecast_confidence = (
        target.get(
            "confidence"
        )
    )

    target_window = _window(
        target
    )

    if not available:

        return {
            "available": True,

            "event": (
                event
            ),

            "event_label": (
                event_label
            ),

            "question_type": (
                question_type
            ),

            "direction": (
                direction
            ),

            "parser_confidence": (
                parser_confidence
            ),

            "confidence": (
                forecast_confidence
            ),

            "forecast_confidence": (
                forecast_confidence
            ),

            "outcome": (
                "no_strong_window"
            ),

            "probability_level": (
                "no_clear_signal"
            ),

            "probability_score": 0.15,

            "answer": (
                _build_no_window_answer(
                    event,
                    direction,
                )
            ),

            "primary_window": {},

            "window": {},

            "supporting_factors": [],

            "challenging_factors": [],

            "overlapping_events": [],
        }

    confirmation = (
        _normalise_confirmation(
            target_window.get(
                "confirmation"
            )
        )
    )

    strength = (
        _normalise_strength(
            target.get(
                "outlook"
            )
        )
    )

    probability = (
        _classify_probability(
            strength,
            confirmation,
        )
    )

    overlaps = (
        _collect_overlaps(
            forecast,
            event,
            target_window,
        )
    )

    (
        supporting,
        challenging,
    ) = _build_overlap_factors(
        overlaps
    )

    if confirmation == (
        "strong_confirmation"
    ):
        supporting.insert(
            0,
            (
                "The Dasha and transit pattern both "
                "reinforce this event."
            ),
        )

    elif confirmation == "confirmed":
        supporting.insert(
            0,
            (
                "The Dasha receives additional "
                "event-specific transit confirmation."
            ),
        )

    elif confirmation == "dasha_only":
        challenging.insert(
            0,
            (
                "The Dasha supports the theme, but "
                "event-specific transit confirmation "
                "is not yet strong."
            ),
        )

    elif confirmation == (
        "transit_only"
    ):
        challenging.insert(
            0,
            (
                "The event is mainly transit-driven "
                "without strong Dasha support."
            ),
        )

    answer = (
        _build_event_answer(
            event,
            direction,
            question_type,
            probability,
            target_window,
            overlaps,
        )
    )

    return {
        "available": True,

        "event": (
            event
        ),

        "event_label": (
            event_label
        ),

        "question_type": (
            question_type
        ),

        "direction": (
            direction
        ),

        "parser_confidence": (
            parser_confidence
        ),

        "confidence": (
            forecast_confidence
        ),

        "forecast_confidence": (
            forecast_confidence
        ),

        "outcome": (
            strength
        ),

        "probability_level": (
            probability.get(
                "level"
            )
        ),

        "probability_score": (
            probability.get(
                "score"
            )
        ),

        "probability_language": (
            probability.get(
                "language"
            )
        ),

        "confirmation": (
            confirmation
        ),

        "answer": (
            answer
        ),

        "primary_window": (
            target_window
        ),

        "window": (
            target_window
        ),

        "supporting_factors": (
            supporting
        ),

        "challenging_factors": (
            challenging
        ),

        "overlapping_events": (
            overlaps
        ),
    }