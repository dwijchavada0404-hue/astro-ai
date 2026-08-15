from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.marriage_forecast_v2 import (
    scan_marriage_forecast_v2,
)


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _safe_list(
    value: Any,
) -> list[Any]:
    if isinstance(value, list):
        return value

    return []


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
# EXPLICIT HORIZON DETECTION
# =========================================================

def _question_has_explicit_horizon(
    question_analysis: dict[str, Any],
) -> bool:
    """
    Determine whether the user explicitly supplied a
    forecast horizon.

    This matters because the marriage question parser may
    provide a default 12-month horizon even when the user
    simply asks:

        "When will I get married?"

    In that situation, the router should search farther
    ahead instead of treating the parser default as an
    explicit user restriction.
    """

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

    # Calendar-year horizons are explicit by definition.
    if horizon_type == "calendar_year":
        return True

    explicit_markers = (
        "next month",
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
        "next year",
        "next 1 year",
        "next 2 years",
        "next 3 years",
        "this year",
        "this month",
    )

    if any(
        marker in question
        for marker in explicit_markers
    ):
        return True

    # Catch explicit calendar years such as:
    # "Will I marry in 2027?"
    for year in range(
        2020,
        2101,
    ):
        if str(year) in question:
            return True

    return False


# =========================================================
# FORECAST RANGE RESOLUTION
# =========================================================

def _resolve_forecast_request(
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    _require_timezone(
        reference_moment,
        "reference_moment",
    )

    horizon = _safe_dict(
        question_analysis.get(
            "forecast_horizon"
        )
    )

    event_name = str(
        question_analysis.get(
            "primary_event",
            "",
        )
        or ""
    )

    question_type = str(
        _safe_dict(
            question_analysis.get(
                "intent"
            )
        ).get(
            "question_type",
            "",
        )
        or ""
    )

    explicit_horizon = (
        _question_has_explicit_horizon(
            question_analysis
        )
    )

    step_days = int(
        question_analysis.get(
            "recommended_step_days",
            7,
        )
        or 7
    )

    # -----------------------------------------------------
    # OPEN-ENDED MARRIAGE TIMING QUESTION
    # -----------------------------------------------------
    #
    # Example:
    #
    #     "When will I get married?"
    #
    # The parser currently supplies a default 12-month
    # horizon. That default should NOT prevent the router
    # from discovering a stronger marriage window farther
    # ahead.
    #
    # We therefore scan 36 months for open-ended marriage
    # timing questions.
    # -----------------------------------------------------

    if (
        event_name == "marriage_timing"
        and question_type == "timing"
        and not explicit_horizon
    ):
        start = reference_moment

        end = (
            reference_moment
            + timedelta(
                days=365 * 3,
            )
        )

        return {
            "start": start,
            "end": end,
            "step_days": step_days,
            "range_type": (
                "open_ended_marriage_timing_36_months"
            ),
        }

    # -----------------------------------------------------
    # EXPLICIT CALENDAR YEAR
    # -----------------------------------------------------

    horizon_type = str(
        horizon.get(
            "type",
            "",
        )
        or ""
    )

    if horizon_type == "calendar_year":

        year = int(
            horizon.get(
                "year"
            )
        )

        start = datetime(
            year,
            1,
            1,
            0,
            0,
            0,
            tzinfo=reference_moment.tzinfo,
        )

        end = datetime(
            year,
            12,
            31,
            23,
            59,
            59,
            tzinfo=reference_moment.tzinfo,
        )

        return {
            "start": start,
            "end": end,
            "step_days": step_days,
            "range_type": (
                f"calendar_year_{year}"
            ),
        }

    # -----------------------------------------------------
    # MONTH HORIZON
    # -----------------------------------------------------

    if horizon_type == "months":

        months = int(
            horizon.get(
                "value",
                12,
            )
            or 12
        )

        start = reference_moment

        end = (
            reference_moment
            + timedelta(
                days=months * 30.4375,
            )
        )

        return {
            "start": start,
            "end": end,
            "step_days": step_days,
            "range_type": (
                f"next_{months}_months"
            ),
        }

    # -----------------------------------------------------
    # YEAR HORIZON
    # -----------------------------------------------------

    if horizon_type == "years":

        years = int(
            horizon.get(
                "value",
                1,
            )
            or 1
        )

        start = reference_moment

        end = (
            reference_moment
            + timedelta(
                days=365 * years,
            )
        )

        return {
            "start": start,
            "end": end,
            "step_days": step_days,
            "range_type": (
                f"next_{years}_years"
            ),
        }

    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    start = reference_moment

    end = (
        reference_moment
        + timedelta(
            days=365,
        )
    )

    return {
        "start": start,
        "end": end,
        "step_days": step_days,
        "range_type": "default_12_months",
    }


# =========================================================
# WINDOW RANKING
# =========================================================

def _window_rank(
    window: dict[str, Any],
) -> tuple[float, float, float, int]:
    """
    Rank forecast windows using:
        1. peak combined score
        2. average combined score
        3. average transit score
        4. number of supporting snapshots

    This prevents an earlier but weaker window from
    automatically winning simply because it occurs first.
    """

    peak = _safe_dict(
        window.get(
            "peak"
        )
    )

    peak_score = float(
        peak.get(
            "score",
            0.0,
        )
        or 0.0
    )

    average_score = float(
        window.get(
            "average_score",
            0.0,
        )
        or 0.0
    )

    average_transit_score = float(
        window.get(
            "average_transit_score",
            0.0,
        )
        or 0.0
    )

    snapshot_count = int(
        window.get(
            "snapshot_count",
            0,
        )
        or 0
    )

    return (
        peak_score,
        average_score,
        average_transit_score,
        snapshot_count,
    )


def _rank_event_windows(
    event_data: dict[str, Any],
) -> dict[str, Any]:

    primary = _safe_dict(
        event_data.get(
            "primary_window"
        )
    )

    secondary = _safe_list(
        event_data.get(
            "secondary_windows"
        )
    )

    windows = []

    if primary:
        windows.append(
            primary
        )

    for window in secondary:
        window = _safe_dict(
            window
        )

        if window:
            windows.append(
                window
            )

    if not windows:
        return event_data

    windows.sort(
        key=_window_rank,
        reverse=True,
    )

    result = dict(
        event_data
    )

    result[
        "primary_window"
    ] = windows[0]

    result[
        "secondary_windows"
    ] = windows[1:4]

    return result


# =========================================================
# PROBABILITY LANGUAGE
# =========================================================

def _probability_from_window(
    window: dict[str, Any],
) -> dict[str, Any]:

    peak = _safe_dict(
        window.get(
            "peak"
        )
    )

    peak_score = float(
        peak.get(
            "score",
            0.0,
        )
        or 0.0
    )

    confirmation = str(
        peak.get(
            "confirmation",
            "",
        )
        or ""
    )

    if (
        peak_score >= 0.75
        and confirmation
        == "strong_confirmation"
    ):
        return {
            "outcome": "strong",
            "probability_level": "likely",
            "probability_score": 0.85,
            "probability_language": (
                "strongly supported"
            ),
        }

    if peak_score >= 0.65:
        return {
            "outcome": "strong",
            "probability_level": "likely",
            "probability_score": 0.8,
            "probability_language": (
                "well supported"
            ),
        }

    if peak_score >= 0.55:
        return {
            "outcome": "moderate",
            "probability_level": "possible",
            "probability_score": 0.65,
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
# SINGLE EVENT ROUTING
# =========================================================

def _route_single_event(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:

    event_name = str(
        question_analysis.get(
            "primary_event",
            "",
        )
        or ""
    )

    event_label = str(
        question_analysis.get(
            "primary_event_label",
            event_name,
        )
        or event_name
    )

    intent = _safe_dict(
        question_analysis.get(
            "intent"
        )
    )

    request = (
        _resolve_forecast_request(
            question_analysis,
            reference_moment,
        )
    )

    forecast = (
        scan_marriage_forecast_v2(
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

    events = _safe_dict(
        forecast.get(
            "events"
        )
    )

    event_data = _safe_dict(
        events.get(
            event_name
        )
    )

    event_data = (
        _rank_event_windows(
            event_data
        )
    )

    primary_window = _safe_dict(
        event_data.get(
            "primary_window"
        )
    )

    if not primary_window:

        return {
            "available": True,
            "route": "single_event",
            "event": event_name,
            "event_label": event_label,
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
                event_data.get(
                    "confidence",
                    0.4,
                )
            ),
            "answer": (
                event_data.get(
                    "summary"
                )
            ),
            "window": {},
            "primary_window": {},
            "secondary_windows": [],
            "forecast_strongest_event": (
                forecast.get(
                    "strongest_event"
                )
            ),
        }

    peak = _safe_dict(
        primary_window.get(
            "peak"
        )
    )

    probability = (
        _probability_from_window(
            primary_window
        )
    )

    answer = (
        f"The strongest "
        f"{event_label.lower()} window runs from "
        f"{primary_window.get('start')} to "
        f"{primary_window.get('end')}, "
        f"with peak activation around "
        f"{peak.get('date')}."
    )

    return {
        "available": True,

        "route": "single_event",

        "event": event_name,

        "event_label": event_label,

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
            event_data.get(
                "confidence",
                0.72,
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

        "window": (
            primary_window
        ),

        "primary_window": (
            primary_window
        ),

        "peak_date": (
            peak.get(
                "date"
            )
        ),

        "event_summary": answer,

        "secondary_windows": (
            event_data.get(
                "secondary_windows",
                [],
            )
        ),

        "forecast_strongest_event": (
            forecast.get(
                "strongest_event"
            )
        ),

        "scan_metadata": (
            forecast.get(
                "forecast_period"
            )
        ),
    }


# =========================================================
# MAIN ROUTER
# =========================================================

def route_marriage_question_v2(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
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

    if query_mode == "single_event":
        return _route_single_event(
            chart,
            question_analysis,
            reference_moment,
        )

    return {
        "available": False,
        "route": query_mode,
        "reason": (
            "This router version currently handles "
            "single-event marriage questions."
        ),
    }