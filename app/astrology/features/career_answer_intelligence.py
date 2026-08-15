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
# STRENGTH LANGUAGE
# =========================================================

STRENGTH_LABELS = {
    "very_strong": "very strong",
    "strong": "strong",
    "moderate": "moderate",
    "supportive": "supportive",
    "active": "active",
    "weak": "weak",
    "no_strong_window": (
        "no separately strong"
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


def _strength_text(
    value: Any,
) -> str:
    text = str(
        value
        or "active"
    )

    return STRENGTH_LABELS.get(
        text,
        text.replace(
            "_",
            " ",
        ),
    )


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


# =========================================================
# DATE OVERLAP
# =========================================================

def _windows_overlap(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:
    """
    Compare ISO date strings.

    Current forecast windows use YYYY-MM-DD,
    so lexical comparison is safe.
    """

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


# =========================================================
# TARGET EXTRACTION
# =========================================================

def _target_context(
    parsed_question: dict[str, Any],
    forecast: dict[str, Any],
) -> dict[str, Any]:

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

    question_type = str(
        intent.get(
            "question_type",
            "general_outlook",
        )
    )

    direction = str(
        intent.get(
            "direction",
            "neutral",
        )
    )

    parser_confidence = float(
        intent.get(
            "confidence",
            0.0,
        )
        or 0.0
    )

    target = (
        _event_data(
            forecast,
            event,
        )
        if event
        != "general_career"
        else {}
    )

    target_window = (
        _window(
            target
        )
    )

    return {
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
        "target": (
            target
        ),
        "target_window": (
            target_window
        ),
    }


# =========================================================
# OVERLAPPING EVENTS
# =========================================================

def _collect_overlapping_events(
    forecast: dict[str, Any],
    target_event: str,
    target_window: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Find forecast events whose primary windows overlap
    the target event's window.
    """

    if not target_window:
        return []

    events = _safe_dict(
        forecast.get(
            "events"
        )
    )

    overlaps: list[
        dict[str, Any]
    ] = []

    for (
        event_name,
        raw_data,
    ) in events.items():

        if (
            event_name
            == target_event
        ):
            continue

        event_data = (
            _safe_dict(
                raw_data
            )
        )

        if not event_data.get(
            "available"
        ):
            continue

        other_window = (
            _window(
                event_data
            )
        )

        if not _windows_overlap(
            target_window,
            other_window,
        ):
            continue

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
                    other_window.get(
                        "start"
                    )
                ),
                "end": (
                    other_window.get(
                        "end"
                    )
                ),
                "peak_date": (
                    other_window.get(
                        "peak_date"
                    )
                ),
                "confirmation": (
                    other_window.get(
                        "confirmation"
                    )
                ),
            }
        )

    return overlaps


# =========================================================
# SUPPORT / CHALLENGE INTERPRETATION
# =========================================================

def _classify_overlap(
    event_name: str,
) -> str:
    if event_name in (
        "promotion_recognition",
        "income_gains",
        "foreign_international_opportunity",
    ):
        return "supportive"

    if event_name == (
        "career_pressure_challenge"
    ):
        return "challenging"

    if event_name == (
        "job_change"
    ):
        return "transition"

    return "context"


def _enrich_overlaps(
    overlaps: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    enriched: list[
        dict[str, Any]
    ] = []

    for overlap in overlaps:

        item = dict(
            overlap
        )

        item[
            "role"
        ] = _classify_overlap(
            str(
                overlap.get(
                    "event"
                )
            )
        )

        enriched.append(
            item
        )

    return enriched


# =========================================================
# GENERAL CAREER ANSWER
# =========================================================

def _general_career_answer(
    forecast: dict[str, Any],
) -> dict[str, Any]:

    overall = _safe_dict(
        forecast.get(
            "overall"
        )
    )

    strongest_event = (
        overall.get(
            "strongest_event"
        )
    )

    confidence = (
        overall.get(
            "confidence"
        )
    )

    return {
        "answer_type": (
            "general_career"
        ),
        "outcome": (
            overall.get(
                "outlook"
            )
        ),
        "confidence": (
            confidence
        ),
        "forecast_confidence": (
            confidence
        ),
        "answer": (
            overall.get(
                "summary",
                (
                    "No clear general career forecast "
                    "was available for the requested period."
                ),
            )
        ),
        "strongest_event": (
            strongest_event
        ),
        "primary_window": {},
        "window": {},
        "supporting_factors": [],
        "challenging_factors": [],
        "overlapping_events": [],
    }


# =========================================================
# NO-WINDOW ANSWERS
# =========================================================

def _no_window_answer(
    event: str,
    event_label: str,
    question_type: str,
    direction: str,
    target: dict[str, Any],
) -> str:

    readable_label = (
        event_label.lower()
    )

    if (
        event
        == "income_gains"
        and direction == "increase"
    ):
        return (
            "The forecast does not identify a sufficiently "
            "strong separate income or salary-growth window "
            "during the requested period. This does not mean "
            "income cannot change; it means the current "
            "Dasha-transit scan does not show a strong enough "
            "independent signal to highlight a specific period."
        )

    if direction == "decrease":
        return (
            f"The forecast does not identify a sufficiently "
            f"clear decrease in {readable_label} during the "
            "requested period."
        )

    if question_type == "timing":
        return (
            f"No sufficiently strong {readable_label} "
            "window was identified in the requested period."
        )

    return (
        f"No sufficiently strong {readable_label} "
        "signal was identified in the requested period."
    )


# =========================================================
# JOB CHANGE ANSWER
# =========================================================

def _job_change_answer(
    target: dict[str, Any],
    window: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> tuple[
    str,
    list[str],
    list[str],
]:

    strength = _strength_text(
        target.get(
            "outlook"
        )
    )

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak = window.get(
        "peak_date"
    )

    confirmation = window.get(
        "confirmation"
    )

    supporting: list[str] = []
    challenging: list[str] = []

    answer = (
        f"The forecast shows a {strength} possibility "
        f"of job change or professional transition. "
        f"The main window runs from {start} to {end}, "
        f"with peak activation around {peak}."
    )

    if confirmation == (
        "strong_confirmation"
    ):
        supporting.append(
            "The Dasha and transit pattern both reinforce "
            "the professional-transition theme."
        )

    for overlap in overlaps:

        overlap_event = (
            overlap.get(
                "event"
            )
        )

        if overlap_event == (
            "career_pressure_challenge"
        ):
            challenging.append(
                "The transition window overlaps with a "
                "strong career-pressure phase, suggesting "
                "that increased responsibility, workload, "
                "restructuring or dissatisfaction may be "
                "part of the background to the change."
            )

        elif overlap_event == (
            "promotion_recognition"
        ):
            supporting.append(
                "A recognition or promotion signal also "
                "overlaps part of the broader career period, "
                "so the transition may involve improved "
                "visibility or responsibility."
            )

        elif overlap_event == (
            "foreign_international_opportunity"
        ):
            supporting.append(
                "Foreign or international career themes are "
                "also active in the background during part "
                "of the transition period."
            )

        elif overlap_event == (
            "income_gains"
        ):
            supporting.append(
                "The transition overlaps with a separate "
                "professional-gains signal."
            )

    if challenging:
        answer += (
            " The same broader period also carries "
            "meaningful professional pressure, so the change "
            "may emerge through restructuring, heavier "
            "responsibility, dissatisfaction or an active "
            "desire to move rather than through an entirely "
            "effortless opportunity."
        )

    return (
        answer,
        supporting,
        challenging,
    )


# =========================================================
# PROMOTION ANSWER
# =========================================================

def _promotion_answer(
    target: dict[str, Any],
    window: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> tuple[
    str,
    list[str],
    list[str],
]:

    strength = _strength_text(
        target.get(
            "outlook"
        )
    )

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak = window.get(
        "peak_date"
    )

    supporting: list[str] = []
    challenging: list[str] = []

    answer = (
        f"The forecast identifies a {strength} "
        f"promotion or professional-recognition window "
        f"from {start} to {end}, with peak activation "
        f"around {peak}."
    )

    for overlap in overlaps:

        event_name = overlap.get(
            "event"
        )

        if event_name == (
            "career_pressure_challenge"
        ):
            challenging.append(
                "Recognition may come with heavier "
                "responsibility, workload or expectations."
            )

        elif event_name == (
            "income_gains"
        ):
            supporting.append(
                "A professional-gains signal overlaps the "
                "recognition period."
            )

        elif event_name == (
            "job_change"
        ):
            supporting.append(
                "The recognition signal overlaps with a "
                "professional-transition theme, so visibility "
                "could arise through a role change or expanded "
                "responsibility."
            )

    return (
        answer,
        supporting,
        challenging,
    )


# =========================================================
# INCOME ANSWER
# =========================================================

def _income_answer(
    target: dict[str, Any],
    window: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> tuple[
    str,
    list[str],
    list[str],
]:

    strength = _strength_text(
        target.get(
            "outlook"
        )
    )

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak = window.get(
        "peak_date"
    )

    supporting: list[str] = []
    challenging: list[str] = []

    answer = (
        f"The forecast identifies a {strength} "
        f"income or professional-gains window from "
        f"{start} to {end}, with peak activation "
        f"around {peak}."
    )

    for overlap in overlaps:

        event_name = overlap.get(
            "event"
        )

        if event_name == (
            "promotion_recognition"
        ):
            supporting.append(
                "Promotion or recognition themes overlap "
                "the gains window."
            )

        elif event_name == (
            "job_change"
        ):
            supporting.append(
                "Professional transition also overlaps "
                "the gains period, so income improvement "
                "could be connected with a change in role "
                "or employer."
            )

        elif event_name == (
            "career_pressure_challenge"
        ):
            challenging.append(
                "The period also contains career-pressure "
                "signals, so gains may come with increased "
                "responsibility or workload."
            )

    return (
        answer,
        supporting,
        challenging,
    )


# =========================================================
# FOREIGN ANSWER
# =========================================================

def _foreign_answer(
    target: dict[str, Any],
    window: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> tuple[
    str,
    list[str],
    list[str],
]:

    strength = _strength_text(
        target.get(
            "outlook"
        )
    )

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak = window.get(
        "peak_date"
    )

    confirmation = window.get(
        "confirmation"
    )

    supporting: list[str] = []
    challenging: list[str] = []

    answer = (
        f"The forecast shows a {strength} foreign or "
        f"international-career theme from {start} to {end}, "
        f"with peak activation around {peak}."
    )

    if confirmation == "dasha_only":

        challenging.append(
            "The Dasha supports foreign or international "
            "career themes, but event-specific transits do "
            "not yet provide strong confirmation."
        )

        answer += (
            " The underlying Dasha supports the theme, "
            "but the transit pattern does not yet provide "
            "strong enough event-specific confirmation to "
            "treat relocation or an overseas opportunity "
            "as a highly confirmed outcome."
        )

    else:

        supporting.append(
            "The foreign-career theme receives additional "
            "transit confirmation."
        )

    for overlap in overlaps:

        event_name = overlap.get(
            "event"
        )

        if event_name == "job_change":

            supporting.append(
                "A job-change or professional-transition "
                "signal overlaps the foreign-career theme."
            )

        elif event_name == (
            "career_pressure_challenge"
        ):

            challenging.append(
                "The same period also carries elevated "
                "professional pressure or responsibility."
            )

    return (
        answer,
        supporting,
        challenging,
    )


# =========================================================
# PRESSURE ANSWER
# =========================================================

def _pressure_answer(
    target: dict[str, Any],
    window: dict[str, Any],
    overlaps: list[dict[str, Any]],
    direction: str,
) -> tuple[
    str,
    list[str],
    list[str],
]:

    strength = _strength_text(
        target.get(
            "outlook"
        )
    )

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak = window.get(
        "peak_date"
    )

    supporting: list[str] = []
    challenging: list[str] = []

    challenging.append(
        "The forecast contains a distinct period of "
        "elevated professional pressure, responsibility "
        "or workload."
    )

    if direction == "decrease":

        answer = (
            "The forecast does not show work pressure "
            "reducing immediately. Instead, it identifies "
            f"a {strength} career-pressure phase from "
            f"{start} to {end}, with the strongest "
            f"activation around {peak}. After the identified "
            "pressure window ends, this specific elevated "
            "signal weakens within the scanned period."
        )

    else:

        answer = (
            f"The forecast identifies a {strength} "
            f"career-pressure phase from {start} to {end}, "
            f"with peak activation around {peak}."
        )

    for overlap in overlaps:

        event_name = overlap.get(
            "event"
        )

        if event_name == "job_change":

            supporting.append(
                "The pressure phase overlaps with a strong "
                "professional-transition signal, suggesting "
                "that workload, restructuring or dissatisfaction "
                "may contribute to career movement."
            )

        elif event_name == (
            "promotion_recognition"
        ):

            supporting.append(
                "Some of the pressure may be connected with "
                "greater professional visibility or responsibility."
            )

    return (
        answer,
        supporting,
        challenging,
    )


# =========================================================
# MAIN ANSWER ENGINE
# =========================================================

def generate_career_question_answer(
    parsed_question: dict[str, Any],
    forecast: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate an intelligent deterministic answer to a
    parsed career question.

    The function does not calculate astrology itself.

    It interprets already-computed forecast output by
    combining:

        target event
        question type
        requested direction
        target forecast window
        overlapping career events
        supportive factors
        challenging factors
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

    context = _target_context(
        parsed_question,
        forecast,
    )

    event = context[
        "event"
    ]

    event_label = context[
        "event_label"
    ]

    question_type = context[
        "question_type"
    ]

    direction = context[
        "direction"
    ]

    parser_confidence = context[
        "parser_confidence"
    ]

    # -----------------------------------------------------
    # GENERAL CAREER
    # -----------------------------------------------------

    if event == "general_career":

        general = (
            _general_career_answer(
                forecast
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

            **general,
        }

    target = context[
        "target"
    ]

    target_window = context[
        "target_window"
    ]

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

    # -----------------------------------------------------
    # NO STRONG WINDOW
    # -----------------------------------------------------

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

            "answer": (
                _no_window_answer(
                    event,
                    event_label,
                    question_type,
                    direction,
                    target,
                )
            ),

            "primary_window": {},

            "window": {},

            "supporting_factors": [],

            "challenging_factors": [],

            "overlapping_events": [],
        }

    raw_overlaps = (
        _collect_overlapping_events(
            forecast,
            event,
            target_window,
        )
    )

    overlaps = (
        _enrich_overlaps(
            raw_overlaps
        )
    )

    # -----------------------------------------------------
    # EVENT-SPECIFIC INTERPRETATION
    # -----------------------------------------------------

    if event == "job_change":

        (
            answer,
            supporting,
            challenging,
        ) = _job_change_answer(
            target,
            target_window,
            overlaps,
        )

    elif event == (
        "promotion_recognition"
    ):

        (
            answer,
            supporting,
            challenging,
        ) = _promotion_answer(
            target,
            target_window,
            overlaps,
        )

    elif event == "income_gains":

        (
            answer,
            supporting,
            challenging,
        ) = _income_answer(
            target,
            target_window,
            overlaps,
        )

    elif event == (
        "foreign_international_opportunity"
    ):

        (
            answer,
            supporting,
            challenging,
        ) = _foreign_answer(
            target,
            target_window,
            overlaps,
        )

    elif event == (
        "career_pressure_challenge"
    ):

        (
            answer,
            supporting,
            challenging,
        ) = _pressure_answer(
            target,
            target_window,
            overlaps,
            direction,
        )

    else:

        answer = str(
            target.get(
                "summary",
                (
                    "A relevant career signal was identified "
                    "in the requested period."
                ),
            )
        )

        supporting = []

        challenging = []

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
            target.get(
                "outlook"
            )
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