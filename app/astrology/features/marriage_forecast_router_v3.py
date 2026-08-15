from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.marriage_forecast_v2 import (
    scan_marriage_forecast_v2,
)

from app.astrology.features.marriage_forecast_router_v2 import (
    route_marriage_question_v2,
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

    tzinfo = (
        reference_moment.tzinfo
    )

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
# SPOUSE MEETING ROUTE
# =========================================================

def _route_spouse_meeting(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """
    Phase-1 spouse-meeting timing proxy.

    The current marriage forecast engine does not yet
    contain a dedicated spouse_meeting event.

    Relationship / commitment activation is therefore
    used as the timing proxy, while the output clearly
    records that proxy relationship.
    """

    proxy_analysis = dict(
        question_analysis
    )

    proxy_analysis[
        "primary_event"
    ] = (
        "relationship_commitment"
    )

    proxy_analysis[
        "primary_event_label"
    ] = (
        EVENT_LABELS[
            "relationship_commitment"
        ]
    )

    proxy_intent = dict(
        _safe_dict(
            question_analysis.get(
                "intent"
            )
        )
    )

    proxy_intent[
        "event"
    ] = (
        "relationship_commitment"
    )

    proxy_intent[
        "event_label"
    ] = (
        EVENT_LABELS[
            "relationship_commitment"
        ]
    )

    proxy_analysis[
        "intent"
    ] = (
        proxy_intent
    )

    # Open-ended meeting questions should search far enough
    # ahead to discover the strongest relationship-opening
    # period, similar to open-ended marriage timing.
    question = str(
        question_analysis.get(
            "normalised_question",
            "",
        )
        or ""
    )

    if (
        proxy_intent.get(
            "question_type"
        )
        == "timing"
        and not any(
            token in question
            for token in (
                "next month",
                "next 3 months",
                "next 6 months",
                "next 12 months",
                "next year",
                "2026",
                "2027",
                "2028",
                "2029",
                "2030",
            )
        )
    ):
        proxy_analysis[
            "primary_event"
        ] = (
            "marriage_timing"
        )

        proxy_analysis[
            "primary_event_label"
        ] = (
            EVENT_LABELS[
                "marriage_timing"
            ]
        )

        proxy_intent[
            "event"
        ] = (
            "marriage_timing"
        )

        proxy_intent[
            "event_label"
        ] = (
            EVENT_LABELS[
                "marriage_timing"
            ]
        )

    proxy_result = (
        route_marriage_question_v2(
            chart,
            proxy_analysis,
            reference_moment,
        )
    )

    if not proxy_result.get(
        "forecast_available"
    ):

        return {
            "available": True,
            "route": "single_event",
            "event": "spouse_meeting",
            "event_label": (
                EVENT_LABELS[
                    "spouse_meeting"
                ]
            ),
            "proxy_event": (
                proxy_result.get(
                    "event"
                )
            ),
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "forecast_available": False,
            "answer": (
                "No sufficiently strong relationship-opening "
                "window was identified in the requested period."
            ),
            "primary_window": {},
            "secondary_windows": [],
            "proxy_result": (
                proxy_result
            ),
        }

    primary = _safe_dict(
        proxy_result.get(
            "primary_window"
        )
    )

    peak = _safe_dict(
        primary.get(
            "peak"
        )
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
            _safe_dict(
                question_analysis.get(
                    "intent"
                )
            ).get(
                "question_type"
            )
        ),

        "reference_moment": (
            reference_moment.isoformat()
        ),

        "proxy_event": (
            proxy_result.get(
                "event"
            )
        ),

        "proxy_reason": (
            "Dedicated spouse-meeting timing is not yet "
            "separately modelled. The current result uses "
            "the strongest marriage/relationship activation "
            "window as a meeting-opportunity proxy."
        ),

        "resolved_forecast_request": (
            proxy_result.get(
                "resolved_forecast_request"
            )
        ),

        "forecast_available": True,

        "outcome": (
            proxy_result.get(
                "outcome"
            )
        ),

        "confidence": (
            proxy_result.get(
                "confidence"
            )
        ),

        "probability_level": (
            proxy_result.get(
                "probability_level"
            )
        ),

        "probability_score": (
            proxy_result.get(
                "probability_score"
            )
        ),

        "confirmation": (
            proxy_result.get(
                "confirmation"
            )
        ),

        "answer": (
            "The strongest current meeting-opportunity "
            f"proxy runs from {primary.get('start')} to "
            f"{primary.get('end')}, with peak activation "
            f"around {peak.get('date')}."
        ),

        "primary_window": (
            primary
        ),

        "secondary_windows": (
            proxy_result.get(
                "secondary_windows",
                [],
            )
        ),

        "peak_date": (
            peak.get(
                "date"
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

    # At this stage only the three forecast-engine events
    # can be directly compared.
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

                "range_type": (
                    range_type
                ),

                "event": (
                    engine_event
                ),

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
            f"The forecast does not show a large difference "
            f"between {best['year']} and {second['year']} for "
            f"{EVENT_LABELS.get(engine_event, engine_event).lower()}."
        )

    return {
        "available": True,

        "route": (
            "calendar_year_comparison"
        ),

        "event": (
            engine_event
        ),

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

        "years": (
            years
        ),

        "best_year": (
            best[
                "year"
            ]
        ),

        "comparison_strength": (
            comparison_strength
        ),

        "margin": (
            margin
        ),

        "answer": (
            answer
        ),

        "ranked_results": (
            ranked
        ),
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
    ] = (
        "single_event"
    )

    inherited_analysis[
        "primary_event"
    ] = (
        inherited_event
    )

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
    ] = (
        inherited_event
    )

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
    ] = (
        inherited_intent
    )

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
                "The previous event is understood, but its "
                "forecast engine is not yet implemented."
            ),
        }

    wrapped = dict(
        result
    )

    wrapped[
        "route"
    ] = (
        "follow_up"
    )

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

        "route": (
            "single_event"
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
    """
    Marriage Forecast Router V3.

    Supported:

        standard single-event marriage forecasts
        spouse-meeting proxy forecasts
        calendar-year comparisons
        conversational follow-ups

    Parsed but not yet forecasted:

        love vs arranged marriage
        love marriage
        arranged marriage
        foreign/intercultural relationship
        spouse traits
        relationship stability
    """

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

    # -----------------------------------------------------
    # FOLLOW-UP
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # COMPARISON
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # STANDARD FORECAST EVENTS
    # -----------------------------------------------------

    if (
        query_mode
        == "single_event"
        and event_name
        in (
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

    # -----------------------------------------------------
    # SPOUSE MEETING
    # -----------------------------------------------------

    if (
        query_mode
        == "single_event"
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

    # -----------------------------------------------------
    # SPECIAL EVENTS NOT YET MODELLED
    # -----------------------------------------------------

    if (
        query_mode
        == "single_event"
    ):

        return (
            _unsupported_special_event(
                question_analysis,
                reference_moment,
            )
        )

    return {
        "available": False,

        "route": (
            query_mode
        ),

        "event": (
            event_name
        ),

        "reference_moment": (
            reference_moment.isoformat()
        ),

        "reason": (
            "This Marriage Forecast Router V3 mode is not "
            "yet implemented."
        ),
    }
