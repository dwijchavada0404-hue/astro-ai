from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.marriage_forecast_v2 import (
    scan_marriage_forecast_v2,
)

from app.astrology.features.marriage_forecast_router_v2 import (
    route_marriage_question_v2,
)

from app.astrology.features.spouse_meeting_forecast_v2 import (
    scan_spouse_meeting_forecast_v2,
)

from app.astrology.features.marriage_love_arranged_reasoning_v2 import (
    analyze_love_vs_arranged_marriage_v2,
)


# =========================================================
# EVENT LABELS
# =========================================================

EVENT_LABELS = {
    "marriage_timing": (
        "Marriage Timing"
    ),
    "relationship_commitment": (
        "Relationship / Commitment"
    ),
    "marriage_delay_challenge": (
        "Marriage Delay / Challenge"
    ),
    "relationship_stability": (
        "Relationship Stability"
    ),
    "foreign_intercultural_connection": (
        "Foreign / Intercultural Relationship"
    ),
    "spouse_traits": (
        "Spouse Traits / Partner Profile"
    ),
    "spouse_meeting": (
        "Meeting Future Spouse"
    ),
    "love_marriage": (
        "Love Marriage"
    ),
    "arranged_marriage": (
        "Arranged Marriage"
    ),
    "love_vs_arranged": (
        "Love vs Arranged Marriage"
    ),
    "general_marriage": (
        "General Marriage / Relationship Outlook"
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


def _require_timezone(
    value: datetime,
    field_name: str,
) -> None:

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            f"{field_name} must include a timezone offset."
        )


# =========================================================
# EXPLICIT HORIZON CHECK
# =========================================================

def _has_explicit_horizon(
    question_analysis: dict[str, Any],
) -> bool:

    question = str(
        question_analysis.get(
            "normalised_question",
            question_analysis.get(
                "original_question",
                "",
            ),
        )
        or ""
    ).lower()

    horizon = _safe_dict(
        question_analysis.get(
            "forecast_horizon"
        )
    )

    horizon_type = str(
        horizon.get(
            "type",
            "",
        )
        or ""
    )

    if horizon_type == (
        "calendar_year"
    ):
        return True

    markers = (
        "this month",
        "next month",
        "this year",
        "next year",
        "next 1 month",
        "next 2 months",
        "next 3 months",
        "next 4 months",
        "next 5 months",
        "next 6 months",
        "next 7 months",
        "next 8 months",
        "next 9 months",
        "next 10 months",
        "next 11 months",
        "next 12 months",
        "next 1 year",
        "next 2 years",
        "next 3 years",
    )

    if any(
        marker in question
        for marker in markers
    ):
        return True

    for year in range(
        2020,
        2101,
    ):

        if str(
            year
        ) in question:

            return True

    return False


# =========================================================
# SPOUSE-MEETING FORECAST RANGE
# =========================================================

def _resolve_spouse_meeting_request(
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    horizon = _safe_dict(
        question_analysis.get(
            "forecast_horizon"
        )
    )

    horizon_type = str(
        horizon.get(
            "type",
            "",
        )
        or ""
    )

    step_days = int(
        question_analysis.get(
            "recommended_step_days",
            7,
        )
        or 7
    )

    explicit_horizon = (
        _has_explicit_horizon(
            question_analysis
        )
    )

    intent = _safe_dict(
        question_analysis.get(
            "intent"
        )
    )

    question_type = str(
        intent.get(
            "question_type",
            "",
        )
        or ""
    )

    if (
        question_type == "timing"
        and not explicit_horizon
    ):

        return {
            "start": reference_moment,
            "end": (
                reference_moment
                + timedelta(
                    days=365 * 3,
                )
            ),
            "step_days": step_days,
            "range_type": (
                "open_ended_spouse_meeting_36_months"
            ),
        }

    if horizon_type == "calendar_year":

        year = int(
            horizon.get(
                "year"
            )
        )

        return {
            "start": datetime(
                year,
                1,
                1,
                0,
                0,
                0,
                tzinfo=reference_moment.tzinfo,
            ),
            "end": datetime(
                year,
                12,
                31,
                23,
                59,
                59,
                tzinfo=reference_moment.tzinfo,
            ),
            "step_days": step_days,
            "range_type": (
                f"calendar_year_{year}"
            ),
        }

    if horizon_type == "months":

        months = int(
            horizon.get(
                "value",
                12,
            )
            or 12
        )

        return {
            "start": reference_moment,
            "end": (
                reference_moment
                + timedelta(
                    days=months * 30.4375,
                )
            ),
            "step_days": step_days,
            "range_type": (
                f"next_{months}_months"
            ),
        }

    if horizon_type == "years":

        years = int(
            horizon.get(
                "value",
                1,
            )
            or 1
        )

        return {
            "start": reference_moment,
            "end": (
                reference_moment
                + timedelta(
                    days=365 * years,
                )
            ),
            "step_days": step_days,
            "range_type": (
                f"next_{years}_years"
            ),
        }

    return {
        "start": reference_moment,
        "end": (
            reference_moment
            + timedelta(
                days=365,
            )
        ),
        "step_days": step_days,
        "range_type": (
            "default_12_months"
        ),
    }


# =========================================================
# WINDOW HELPERS
# =========================================================

def _window_peak_score(
    window: dict[str, Any],
) -> float:

    peak = _safe_dict(
        window.get(
            "peak"
        )
    )

    return _safe_float(
        peak.get(
            "score"
        )
    )


def _event_comparison_score(
    event_data: dict[str, Any],
) -> float:

    if not event_data.get(
        "available"
    ):
        return 0.0

    primary = _safe_dict(
        event_data.get(
            "primary_window"
        )
    )

    if not primary:
        return 0.0

    peak_score = (
        _window_peak_score(
            primary
        )
    )

    average_score = _safe_float(
        primary.get(
            "average_score"
        )
    )

    transit_score = _safe_float(
        primary.get(
            "average_transit_score"
        )
    )

    return round(
        (
            peak_score * 0.55
            + average_score * 0.30
            + transit_score * 0.15
        ),
        3,
    )


# =========================================================
# CALENDAR YEAR RANGE
# =========================================================

def _calendar_year_range(
    year: int,
    reference_moment: datetime,
) -> tuple[
    datetime,
    datetime,
    str,
]:

    tzinfo = reference_moment.tzinfo

    year_start = datetime(
        year,
        1,
        1,
        0,
        0,
        0,
        tzinfo=tzinfo,
    )

    year_end = datetime(
        year + 1,
        1,
        1,
        0,
        0,
        0,
        tzinfo=tzinfo,
    )

    if year == reference_moment.year:

        start = max(
            reference_moment,
            year_start,
        )

        return (
            start,
            year_end,
            "remaining_current_year",
        )

    if year > reference_moment.year:

        return (
            year_start,
            year_end,
            "future_full_year",
        )

    return (
        year_start,
        year_end,
        "past_calendar_year",
    )


# =========================================================
# FORECAST EVENT LOOKUP
# =========================================================

def _forecast_event(
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


# =========================================================
# STANDARD SINGLE EVENT
# =========================================================

def _route_standard_single_event(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    return (
        route_marriage_question_v2(
            chart,
            question_analysis,
            reference_moment,
        )
    )


# =========================================================
# LOVE / ARRANGED ROUTE
# =========================================================

def _route_love_arranged(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    event_name = str(
        question_analysis.get(
            "primary_event",
            "love_vs_arranged",
        )
        or "love_vs_arranged"
    )

    intent = _safe_dict(
        question_analysis.get(
            "intent"
        )
    )

    analysis = (
        analyze_love_vs_arranged_marriage_v2(
            chart
        )
    )

    scores = _safe_dict(
        analysis.get(
            "scores"
        )
    )

    love_probability = _safe_float(
        scores.get(
            "love_probability"
        )
    )

    arranged_probability = _safe_float(
        scores.get(
            "arranged_probability"
        )
    )

    outcome = str(
        analysis.get(
            "outcome",
            "mixed_or_hybrid",
        )
    )

    if event_name == (
        "love_marriage"
    ):

        probability_score = (
            love_probability
        )

        probability_level = (
            "likely"
            if probability_score >= 0.68
            else (
                "possible"
                if probability_score >= 0.50
                else "less_likely"
            )
        )

        answer = (
            "The natal evidence gives love/self-choice "
            f"marriage a relative support score of "
            f"{round(probability_score * 100, 1)}%. "
            f"The overall pattern is classified as "
            f"{analysis.get('label')}."
        )

        relevant_indicators = (
            analysis.get(
                "love_indicators",
                [],
            )
        )

    elif event_name == (
        "arranged_marriage"
    ):

        probability_score = (
            arranged_probability
        )

        probability_level = (
            "likely"
            if probability_score >= 0.68
            else (
                "possible"
                if probability_score >= 0.50
                else "less_likely"
            )
        )

        answer = (
            "The natal evidence gives arranged/family-mediated "
            f"marriage a relative support score of "
            f"{round(probability_score * 100, 1)}%. "
            f"The overall pattern is classified as "
            f"{analysis.get('label')}."
        )

        relevant_indicators = (
            analysis.get(
                "arranged_indicators",
                [],
            )
        )

    else:

        probability_score = max(
            love_probability,
            arranged_probability,
        )

        probability_level = (
            "mixed"
            if outcome == "mixed_or_hybrid"
            else "leaning"
        )

        answer = (
            analysis.get(
                "summary"
            )
        )

        relevant_indicators = (
            analysis.get(
                "all_indicators",
                [],
            )
        )

    return {
        "available": True,

        "route": (
            "natal_evidence"
        ),

        "event": (
            event_name
        ),

        "event_label": (
            EVENT_LABELS.get(
                event_name,
                event_name,
            )
        ),

        "question_type": (
            intent.get(
                "question_type"
            )
        ),

        "direction": (
            intent.get(
                "direction"
            )
        ),

        "parser_confidence": (
            intent.get(
                "confidence"
            )
        ),

        "reference_moment": (
            reference_moment.isoformat()
        ),

        "evidence_engine": (
            "marriage_love_arranged_reasoning_v2"
        ),

        "forecast_type": (
            "natal_pattern"
        ),

        "outcome": (
            outcome
        ),

        "label": (
            analysis.get(
                "label"
            )
        ),

        "confidence": (
            analysis.get(
                "confidence"
            )
        ),

        "probability_level": (
            probability_level
        ),

        "probability_score": round(
            probability_score,
            3,
        ),

        "answer": (
            answer
        ),

        "scores": (
            scores
        ),

        "love_probability": (
            love_probability
        ),

        "arranged_probability": (
            arranged_probability
        ),

        "relevant_indicators": (
            relevant_indicators
        ),

        "love_indicators": (
            analysis.get(
                "love_indicators",
                [],
            )
        ),

        "arranged_indicators": (
            analysis.get(
                "arranged_indicators",
                [],
            )
        ),

        "general_indicators": (
            analysis.get(
                "general_indicators",
                [],
            )
        ),

        "chart_context": (
            analysis.get(
                "chart_context",
                {},
            )
        ),

        "analysis": (
            analysis
        ),
    }


# =========================================================
# SPOUSE MEETING PROBABILITY
# =========================================================

def _spouse_meeting_probability(
    window: dict[str, Any],
) -> dict[str, Any]:

    peak = _safe_dict(
        window.get(
            "peak"
        )
    )

    peak_score = _safe_float(
        peak.get(
            "score"
        )
    )

    confirmation = str(
        peak.get(
            "confirmation",
            "",
        )
        or ""
    )

    if (
        peak_score >= 0.82
        and confirmation
        == "strong_meeting_signal"
    ):

        return {
            "outcome": "very_strong",
            "probability_level": "likely",
            "probability_score": 0.90,
            "probability_language": (
                "strongly supported"
            ),
        }

    if peak_score >= 0.70:

        return {
            "outcome": "strong",
            "probability_level": "likely",
            "probability_score": 0.82,
            "probability_language": (
                "well supported"
            ),
        }

    if peak_score >= 0.60:

        return {
            "outcome": "moderate",
            "probability_level": "possible",
            "probability_score": 0.68,
            "probability_language": (
                "moderately supported"
            ),
        }

    return {
        "outcome": "weak",
        "probability_level": "uncertain",
        "probability_score": 0.45,
        "probability_language": (
            "weakly supported"
        ),
    }


# =========================================================
# SPOUSE MEETING ROUTE
# =========================================================

def _route_spouse_meeting(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    request = (
        _resolve_spouse_meeting_request(
            question_analysis,
            reference_moment,
        )
    )

    forecast = (
        scan_spouse_meeting_forecast_v2(
            chart,
            request[
                "start"
            ],
            request[
                "end"
            ],
            step_days=request[
                "step_days"
            ],
        )
    )

    intent = _safe_dict(
        question_analysis.get(
            "intent"
        )
    )

    primary = _safe_dict(
        forecast.get(
            "primary_window"
        )
    )

    if not primary:

        return {
            "available": True,
            "route": "single_event",
            "event": "spouse_meeting",
            "event_label": (
                EVENT_LABELS[
                    "spouse_meeting"
                ]
            ),
            "question_type": (
                intent.get(
                    "question_type"
                )
            ),
            "direction": (
                intent.get(
                    "direction"
                )
            ),
            "parser_confidence": (
                intent.get(
                    "confidence"
                )
            ),
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "forecast_engine": (
                "spouse_meeting_forecast_v2"
            ),
            "resolved_forecast_request": {
                "start": request[
                    "start"
                ].isoformat(),
                "end": request[
                    "end"
                ].isoformat(),
                "step_days": request[
                    "step_days"
                ],
                "range_type": request[
                    "range_type"
                ],
            },
            "forecast_available": False,
            "outcome": "no_strong_window",
            "confidence": (
                forecast.get(
                    "confidence",
                    0.4,
                )
            ),
            "answer": (
                forecast.get(
                    "summary"
                )
            ),
            "primary_window": {},
            "secondary_windows": [],
            "scan_metadata": (
                forecast.get(
                    "forecast_period"
                )
            ),
        }

    peak = _safe_dict(
        primary.get(
            "peak"
        )
    )

    probability = (
        _spouse_meeting_probability(
            primary
        )
    )

    answer = (
        "The strongest spouse-meeting opportunity "
        f"runs from {primary.get('start')} to "
        f"{primary.get('end')}, with peak activation "
        f"around {peak.get('date')}."
    )

    return {
        "available": True,
        "route": "single_event",
        "event": "spouse_meeting",
        "event_label": (
            EVENT_LABELS[
                "spouse_meeting"
            ]
        ),
        "question_type": (
            intent.get(
                "question_type"
            )
        ),
        "direction": (
            intent.get(
                "direction"
            )
        ),
        "parser_confidence": (
            intent.get(
                "confidence"
            )
        ),
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "forecast_engine": (
            "spouse_meeting_forecast_v2"
        ),
        "resolved_forecast_request": {
            "start": request[
                "start"
            ].isoformat(),
            "end": request[
                "end"
            ].isoformat(),
            "step_days": request[
                "step_days"
            ],
            "range_type": request[
                "range_type"
            ],
        },
        "forecast_available": True,
        "outcome": (
            probability[
                "outcome"
            ]
        ),
        "confidence": (
            forecast.get(
                "confidence",
                0.70,
            )
        ),
        "probability_level": (
            probability[
                "probability_level"
            ]
        ),
        "probability_score": (
            probability[
                "probability_score"
            ]
        ),
        "probability_language": (
            probability[
                "probability_language"
            ]
        ),
        "confirmation": (
            peak.get(
                "confirmation"
            )
        ),
        "answer": answer,
        "window": primary,
        "primary_window": primary,
        "peak_date": (
            peak.get(
                "date"
            )
        ),
        "event_summary": answer,
        "secondary_windows": (
            forecast.get(
                "secondary_windows",
                [],
            )
        ),
        "scan_metadata": (
            forecast.get(
                "forecast_period"
            )
        ),
    }


# =========================================================
# CALENDAR YEAR COMPARISON
# =========================================================

def _route_calendar_year_comparison(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    comparison = _safe_dict(
        question_analysis.get(
            "comparison"
        )
    )

    years = [
        int(
            year
        )
        for year in _safe_list(
            comparison.get(
                "values"
            )
        )
    ]

    if len(
        years
    ) < 2:

        raise ValueError(
            "Calendar-year comparison requires at least "
            "two years."
        )

    event_name = str(
        question_analysis.get(
            "primary_event",
            "marriage_timing",
        )
        or "marriage_timing"
    )

    engine_event = (
        event_name
        if event_name
        in (
            "marriage_timing",
            "relationship_commitment",
            "marriage_delay_challenge",
        )
        else "marriage_timing"
    )

    results = []

    for year in years:

        (
            start,
            end,
            range_type,
        ) = _calendar_year_range(
            year,
            reference_moment,
        )

        forecast = (
            scan_marriage_forecast_v2(
                chart,
                start,
                end,
                step_days=7,
            )
        )

        event_data = (
            _forecast_event(
                forecast,
                engine_event,
            )
        )

        comparison_score = (
            _event_comparison_score(
                event_data
            )
        )

        results.append(
            {
                "year": year,
                "range_type": range_type,
                "event": engine_event,
                "available": bool(
                    event_data.get(
                        "available"
                    )
                ),
                "outlook": (
                    event_data.get(
                        "outlook",
                        "no_strong_window",
                    )
                ),
                "confidence": (
                    event_data.get(
                        "confidence",
                        0.4,
                    )
                ),
                "comparison_score": (
                    comparison_score
                ),
                "primary_window": (
                    event_data.get(
                        "primary_window",
                        {},
                    )
                ),
                "secondary_windows": (
                    event_data.get(
                        "secondary_windows",
                        [],
                    )
                ),
                "summary": (
                    event_data.get(
                        "summary"
                    )
                ),
                "scan_metadata": (
                    forecast.get(
                        "forecast_period"
                    )
                ),
            }
        )

    ranked = sorted(
        results,
        key=lambda item: (
            _safe_float(
                item.get(
                    "comparison_score"
                )
            )
        ),
        reverse=True,
    )

    best = ranked[
        0
    ]

    second = ranked[
        1
    ]

    margin = round(
        (
            _safe_float(
                best.get(
                    "comparison_score"
                )
            )
            - _safe_float(
                second.get(
                    "comparison_score"
                )
            )
        ),
        3,
    )

    if margin >= 0.12:

        comparison_strength = (
            "clearly_stronger"
        )

        answer = (
            f"{best['year']} shows the stronger "
            f"{EVENT_LABELS.get(engine_event, engine_event).lower()} "
            f"signal compared with {second['year']}."
        )

    elif margin >= 0.05:

        comparison_strength = (
            "moderately_stronger"
        )

        answer = (
            f"{best['year']} appears somewhat better than "
            f"{second['year']} for "
            f"{EVENT_LABELS.get(engine_event, engine_event).lower()}."
        )

    else:

        comparison_strength = (
            "roughly_equal"
        )

        answer = (
            "The forecast does not show a large difference "
            f"between {best['year']} and {second['year']} "
            f"for "
            f"{EVENT_LABELS.get(engine_event, engine_event).lower()}."
        )

    return {
        "available": True,
        "route": (
            "calendar_year_comparison"
        ),
        "event": engine_event,
        "event_label": (
            EVENT_LABELS.get(
                engine_event,
                engine_event,
            )
        ),
        "comparison_type": (
            "calendar_years"
        ),
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "years": years,
        "best_year": (
            best[
                "year"
            ]
        ),
        "comparison_strength": (
            comparison_strength
        ),
        "margin": margin,
        "answer": answer,
        "ranked_results": ranked,
    }


# =========================================================
# CONTEXT EVENT EXTRACTION
# =========================================================

def _extract_context_event(
    previous_context: dict[str, Any] | None,
) -> str | None:

    if not isinstance(
        previous_context,
        dict,
    ):
        return None

    prior_analysis = _safe_dict(
        previous_context.get(
            "question_analysis"
        )
    )

    event_name = str(
        prior_analysis.get(
            "primary_event",
            "",
        )
        or ""
    )

    if event_name:

        return event_name

    prior_result = _safe_dict(
        previous_context.get(
            "route_result"
        )
    )

    event_name = str(
        prior_result.get(
            "event",
            "",
        )
        or ""
    )

    if event_name:

        return event_name

    return None


# =========================================================
# FOLLOW-UP ROUTE
# =========================================================

def _route_follow_up(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
    previous_context: dict[str, Any] | None,
) -> dict[str, Any]:

    inherited_event = (
        _extract_context_event(
            previous_context
        )
    )

    if not inherited_event:

        return {
            "available": False,
            "route": "follow_up",
            "requires_context": True,
            "context_used": False,
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "reason": (
                "A previous marriage question is required "
                "to interpret this follow-up."
            ),
        }

    inherited_analysis = dict(
        question_analysis
    )

    inherited_analysis[
        "query_mode"
    ] = "single_event"

    inherited_analysis[
        "primary_event"
    ] = inherited_event

    inherited_analysis[
        "primary_event_label"
    ] = (
        EVENT_LABELS.get(
            inherited_event,
            inherited_event,
        )
    )

    inherited_intent = dict(
        _safe_dict(
            question_analysis.get(
                "intent"
            )
        )
    )

    inherited_intent[
        "event"
    ] = inherited_event

    inherited_intent[
        "event_label"
    ] = (
        EVENT_LABELS.get(
            inherited_event,
            inherited_event,
        )
    )

    inherited_analysis[
        "intent"
    ] = inherited_intent

    if inherited_event == (
        "spouse_meeting"
    ):

        result = (
            _route_spouse_meeting(
                chart,
                inherited_analysis,
                reference_moment,
            )
        )

    elif inherited_event in (
        "love_vs_arranged",
        "love_marriage",
        "arranged_marriage",
    ):

        result = (
            _route_love_arranged(
                chart,
                inherited_analysis,
                reference_moment,
            )
        )

    elif inherited_event in (
        "marriage_timing",
        "relationship_commitment",
        "marriage_delay_challenge",
    ):

        result = (
            _route_standard_single_event(
                chart,
                inherited_analysis,
                reference_moment,
            )
        )

    else:

        return {
            "available": False,
            "route": "follow_up",
            "requires_context": True,
            "context_used": True,
            "inherited_event": (
                inherited_event
            ),
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "reason": (
                "The previous event is understood, but "
                "its forecast engine is not yet implemented."
            ),
        }

    wrapped = dict(
        result
    )

    wrapped[
        "route"
    ] = "follow_up"

    wrapped[
        "requires_context"
    ] = True

    wrapped[
        "context_used"
    ] = True

    wrapped[
        "inherited_event"
    ] = (
        inherited_event
    )

    return wrapped


# =========================================================
# UNSUPPORTED SPECIAL EVENT
# =========================================================

def _unsupported_special_event(
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    event_name = str(
        question_analysis.get(
            "primary_event",
            "general_marriage",
        )
    )

    return {
        "available": False,
        "route": "single_event",
        "event": event_name,
        "event_label": (
            EVENT_LABELS.get(
                event_name,
                event_name,
            )
        ),
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "reason": (
            "The question is understood correctly, but a "
            "dedicated evidence engine for this marriage "
            "event has not yet been implemented."
        ),
    }


# =========================================================
# MAIN ROUTER
# =========================================================

def route_marriage_question_v3(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
    previous_context: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if not isinstance(
        chart,
        dict,
    ):
        raise ValueError(
            "chart must be a dictionary."
        )

    if not isinstance(
        question_analysis,
        dict,
    ):
        raise ValueError(
            "question_analysis must be a dictionary."
        )

    if not isinstance(
        reference_moment,
        datetime,
    ):
        raise ValueError(
            "reference_moment must be a datetime."
        )

    _require_timezone(
        reference_moment,
        "reference_moment",
    )

    query_mode = str(
        question_analysis.get(
            "query_mode",
            "single_event",
        )
        or "single_event"
    )

    event_name = str(
        question_analysis.get(
            "primary_event",
            "general_marriage",
        )
        or "general_marriage"
    )

    if query_mode == (
        "follow_up"
    ):

        return (
            _route_follow_up(
                chart,
                question_analysis,
                reference_moment,
                previous_context,
            )
        )

    if query_mode == (
        "comparison"
    ):

        return (
            _route_calendar_year_comparison(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    if (
        query_mode == "single_event"
        and event_name in (
            "marriage_timing",
            "relationship_commitment",
            "marriage_delay_challenge",
        )
    ):

        return (
            _route_standard_single_event(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    if (
        query_mode == "single_event"
        and event_name
        == "spouse_meeting"
    ):

        return (
            _route_spouse_meeting(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    if (
        query_mode == "single_event"
        and event_name in (
            "love_vs_arranged",
            "love_marriage",
            "arranged_marriage",
        )
    ):

        return (
            _route_love_arranged(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    if query_mode == (
        "single_event"
    ):

        return (
            _unsupported_special_event(
                question_analysis,
                reference_moment,
            )
        )

    return {
        "available": False,
        "route": query_mode,
        "event": event_name,
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "reason": (
            "This Marriage Forecast Router V3 mode "
            "is not yet implemented."
        ),
    }
