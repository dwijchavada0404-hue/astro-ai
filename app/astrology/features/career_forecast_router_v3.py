from calendar import monthrange
from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.career_forecast_scanner import (
    scan_career_forecast,
)
from app.astrology.features.career_forecast_windows import (
    build_career_forecast_windows,
)
from app.astrology.features.career_forecast_narrative import (
    generate_career_forecast_narrative,
)


# =========================================================
# CONSTANTS
# =========================================================

FOLLOW_UP_BUFFER_DAYS = 75


EVENT_LABELS = {
    "job_change": "Job Change / Professional Transition",
    "promotion_recognition": "Promotion / Recognition",
    "income_gains": "Income / Professional Gains",
    "foreign_international_opportunity": (
        "Foreign / International Opportunity"
    ),
    "career_pressure_challenge": "Career Pressure / Challenge",
    "job_loss_risk": "Job Loss / Employment Risk",
    "general_career": "General Career Forecast",
}


EVENT_PHRASES = {
    "job_change": "job change or professional transition",
    "promotion_recognition": "promotion or professional recognition",
    "income_gains": "income or professional gains",
    "foreign_international_opportunity": (
        "foreign or international career opportunity"
    ),
    "career_pressure_challenge": (
        "career pressure or professional challenge"
    ),
    "job_loss_risk": "job-loss or employment-risk",
    "general_career": "general career prospects",
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value

    return []


def _event_data(
    forecast: dict[str, Any],
    event_name: str,
) -> dict[str, Any]:
    events = _safe_dict(
        forecast.get("events")
    )

    return _safe_dict(
        events.get(event_name)
    )


def _event_label(
    event_name: str,
) -> str:
    return EVENT_LABELS.get(
        event_name,
        event_name.replace(
            "_",
            " ",
        ).title(),
    )


def _event_phrase(
    event_name: str,
) -> str:
    return EVENT_PHRASES.get(
        event_name,
        event_name.replace(
            "_",
            " ",
        ),
    )


# =========================================================
# TIME HELPERS
# =========================================================

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


def _add_months(
    value: datetime,
    months: int,
) -> datetime:
    if months < 0:
        raise ValueError(
            "months must not be negative."
        )

    zero_based_month = (
        value.month
        - 1
        + months
    )

    year = (
        value.year
        + zero_based_month // 12
    )

    month = (
        zero_based_month
        % 12
    ) + 1

    final_day = min(
        value.day,
        monthrange(
            year,
            month,
        )[1],
    )

    return value.replace(
        year=year,
        month=month,
        day=final_day,
    )


def _parse_window_datetime(
    value: Any,
    tzinfo: Any,
) -> datetime | None:
    if not isinstance(
        value,
        str,
    ):
        return None

    try:
        parsed = datetime.fromisoformat(
            value
        )

    except ValueError:
        return None

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        parsed = parsed.replace(
            tzinfo=tzinfo
        )

    return parsed


# =========================================================
# SCORE HELPERS
# =========================================================

def _strength_score(
    value: Any,
) -> float:
    mapping = {
        "very_strong": 5.0,
        "strong": 4.0,
        "moderate": 3.0,
        "supportive": 2.5,
        "active": 2.0,
        "weak": 1.0,
        "no_strong_window": 0.0,
    }

    return float(
        mapping.get(
            str(
                value
                or "no_strong_window"
            ),
            0.0,
        )
    )


def _confirmation_score(
    value: Any,
) -> float:
    mapping = {
        "strong_confirmation": 2.0,
        "confirmed": 1.5,
        "dasha_only": 0.75,
        "transit_only": 0.5,
        "weak": 0.25,
        "none": 0.0,
    }

    return float(
        mapping.get(
            str(
                value
                or "none"
            ),
            0.0,
        )
    )


def _comparison_score(
    event_data: dict[str, Any],
) -> float:
    if not event_data.get(
        "available"
    ):
        return 0.0

    window = _safe_dict(
        event_data.get("window")
    )

    strength = _strength_score(
        event_data.get("outlook")
    )

    confirmation = _confirmation_score(
        window.get("confirmation")
    )

    confidence = float(
        event_data.get(
            "confidence",
            0.0,
        )
        or 0.0
    )

    combined_score = float(
        window.get(
            "combined_score",
            0.0,
        )
        or 0.0
    )

    transit_score = float(
        window.get(
            "transit_score",
            0.0,
        )
        or 0.0
    )

    result = (
        strength
        + confirmation
        + confidence * 0.75
        + combined_score * 0.50
        + transit_score * 0.25
    )

    return round(
        result,
        3,
    )


def _normalise_router_score(
    value: Any,
) -> float:
    try:
        score = float(
            value
            or 0.0
        )

    except (
        TypeError,
        ValueError,
    ):
        score = 0.0

    return round(
        max(
            0.0,
            min(
                1.0,
                score / 10.0,
            ),
        ),
        3,
    )


# =========================================================
# FORECAST EXECUTION
# =========================================================

def _run_forecast(
    chart: dict[str, Any],
    start: datetime,
    end: datetime,
    step_days: int,
) -> dict[str, Any]:
    if end <= start:
        raise ValueError(
            "Forecast end must be later than start."
        )

    scan = scan_career_forecast(
        chart,
        start,
        end,
        step_days=step_days,
    )

    windows = (
        build_career_forecast_windows(
            scan
        )
    )

    forecast = (
        generate_career_forecast_narrative(
            windows
        )
    )

    return {
        "scan": scan,
        "windows": windows,
        "forecast": forecast,
    }


# =========================================================
# WINDOW HELPERS
# =========================================================

def _windows_overlap(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:
    first_start = first.get("start")
    first_end = first.get("end")
    second_start = second.get("start")
    second_end = second.get("end")

    values = (
        first_start,
        first_end,
        second_start,
        second_end,
    )

    if not all(
        isinstance(value, str)
        and value
        for value in values
    ):
        return False

    return (
        first_start <= second_end
        and second_start <= first_end
    )


def _overlap_period(
    first: dict[str, Any],
    second: dict[str, Any],
) -> dict[str, Any]:
    if not _windows_overlap(
        first,
        second,
    ):
        return {
            "available": False,
        }

    return {
        "available": True,
        "start": max(
            str(first.get("start")),
            str(second.get("start")),
        ),
        "end": min(
            str(first.get("end")),
            str(second.get("end")),
        ),
    }


# =========================================================
# GENERIC QUESTION RANGE
# =========================================================

def _question_forecast_range(
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> tuple[
    datetime,
    datetime,
    int,
    str,
]:
    base_parser = _safe_dict(
        question_analysis.get(
            "base_parser"
        )
    )

    horizon = _safe_dict(
        base_parser.get(
            "forecast_horizon"
        )
    )

    horizon_type = str(
        horizon.get(
            "type",
            "months",
        )
    )

    step_days = int(
        base_parser.get(
            "recommended_step_days",
            7,
        )
        or 7
    )

    step_days = max(
        1,
        min(
            31,
            step_days,
        ),
    )

    if horizon_type == "months":
        months = max(
            1,
            int(
                horizon.get(
                    "value",
                    12,
                )
                or 12
            ),
        )

        return (
            reference_moment,
            _add_months(
                reference_moment,
                months,
            ),
            step_days,
            f"next_{months}_months",
        )

    if horizon_type == "years":
        years = max(
            1,
            int(
                horizon.get(
                    "value",
                    1,
                )
                or 1
            ),
        )

        return (
            reference_moment,
            _add_months(
                reference_moment,
                years * 12,
            ),
            step_days,
            f"next_{years}_years",
        )

    if horizon_type == "calendar_year":
        year = int(
            horizon.get("year")
        )

        tzinfo = reference_moment.tzinfo

        year_start = datetime(
            year,
            1,
            1,
            tzinfo=tzinfo,
        )

        year_end = datetime(
            year + 1,
            1,
            1,
            tzinfo=tzinfo,
        )

        if year == reference_moment.year:
            return (
                reference_moment,
                year_end,
                step_days,
                "remaining_calendar_year",
            )

        return (
            year_start,
            year_end,
            step_days,
            "calendar_year",
        )

    return (
        reference_moment,
        _add_months(
            reference_moment,
            12,
        ),
        7,
        "default_12_months",
    )


# =========================================================
# SINGLE-EVENT ROUTE
# =========================================================

def _single_event_probability(
    event_data: dict[str, Any],
) -> dict[str, Any]:
    available = bool(
        event_data.get(
            "available"
        )
    )

    if not available:
        return {
            "probability_level": (
                "not_strongly_supported"
            ),
            "probability_score": 0.30,
            "probability_language": (
                "not strongly supported"
            ),
        }

    outlook = str(
        event_data.get(
            "outlook",
            "active",
        )
    )

    mapping = {
        "very_strong": (
            "strongly_likely",
            0.90,
            "strongly supported",
        ),
        "strong": (
            "likely",
            0.80,
            "well supported",
        ),
        "moderate": (
            "possible",
            0.65,
            "moderately supported",
        ),
        "supportive": (
            "possible",
            0.60,
            "supported",
        ),
        "active": (
            "possible",
            0.55,
            "somewhat supported",
        ),
        "weak": (
            "weak",
            0.40,
            "weakly supported",
        ),
    }

    (
        level,
        score,
        language,
    ) = mapping.get(
        outlook,
        (
            "possible",
            0.55,
            "somewhat supported",
        ),
    )

    return {
        "probability_level": level,
        "probability_score": score,
        "probability_language": language,
    }


def _build_single_event_answer(
    event_name: str,
    question_type: str,
    direction: str,
    event_data: dict[str, Any],
    forecast: dict[str, Any],
) -> str:
    phrase = _event_phrase(
        event_name
    )

    available = bool(
        event_data.get(
            "available"
        )
    )

    window = _safe_dict(
        event_data.get(
            "window"
        )
    )

    outlook = str(
        event_data.get(
            "outlook",
            "no_strong_window",
        )
    )

    if not available:
        if (
            event_name == "income_gains"
            and direction == "increase"
        ):
            return (
                "The forecast does not identify a "
                "sufficiently strong separate income or "
                "salary-growth window in the requested "
                "period."
            )

        if (
            event_name
            == "career_pressure_challenge"
            and direction == "decrease"
        ):
            return (
                "The forecast does not identify a distinct "
                "career-pressure window strong enough to "
                "highlight a clear reduction pattern."
            )

        return (
            f"The forecast does not identify a sufficiently "
            f"strong {phrase} window in the requested period."
        )

    start = window.get("start")
    end = window.get("end")
    peak = window.get(
        "peak_date"
    )

    if event_name == "job_change":
        answer = (
            f"A {phrase} is "
            f"{outlook.replace('_', ' ')}ly supported "
            "in the requested period."
        )

        if start and end:
            answer += (
                f" The main window runs from {start} to "
                f"{end}."
            )

        if peak:
            answer += (
                f" Peak activation appears around {peak}."
            )

        pressure = _event_data(
            forecast,
            "career_pressure_challenge",
        )

        if pressure.get(
            "available"
        ):
            answer += (
                " The transition period also overlaps with "
                "meaningful professional pressure, so the "
                "change may be connected with restructuring, "
                "higher responsibility, dissatisfaction or "
                "an active desire to move."
            )

        return answer

    if event_name == "promotion_recognition":
        answer = (
            f"The forecast shows a "
            f"{outlook.replace('_', ' ')} promotion or "
            "professional-recognition signal."
        )

        if start and end:
            answer += (
                f" The main window runs from {start} to "
                f"{end}."
            )

        if peak:
            answer += (
                f" Peak activation appears around {peak}."
            )

        return answer

    if event_name == "income_gains":
        answer = (
            f"The forecast shows a "
            f"{outlook.replace('_', ' ')} income or "
            "professional-gains signal."
        )

        if start and end:
            answer += (
                f" The main window runs from {start} to "
                f"{end}."
            )

        if peak:
            answer += (
                f" Peak activation appears around {peak}."
            )

        return answer

    if (
        event_name
        == "foreign_international_opportunity"
    ):
        answer = (
            f"The forecast shows a "
            f"{outlook.replace('_', ' ')} foreign or "
            "international-career theme."
        )

        if start and end:
            answer += (
                f" The main window runs from {start} to "
                f"{end}."
            )

        if peak:
            answer += (
                f" Peak activation appears around {peak}."
            )

        confirmation = window.get(
            "confirmation"
        )

        if confirmation == "dasha_only":
            answer += (
                " The underlying Dasha supports the theme, "
                "but event-specific transit confirmation "
                "remains limited."
            )

        return answer

    if (
        event_name
        == "career_pressure_challenge"
    ):
        if direction == "decrease":
            answer = (
                "Work pressure does not appear to reduce "
                "immediately."
            )

            if start and end:
                answer += (
                    f" A stronger pressure phase runs from "
                    f"{start} to {end}."
                )

            if peak:
                answer += (
                    f" The pressure is strongest around "
                    f"{peak}."
                )

            answer += (
                " After that identified window, this "
                "specific elevated-pressure signal weakens "
                "within the scanned period."
            )

            return answer

        answer = (
            f"The forecast shows a "
            f"{outlook.replace('_', ' ')} career-pressure "
            "or professional-challenge phase."
        )

        if start and end:
            answer += (
                f" The main window runs from {start} to "
                f"{end}."
            )

        if peak:
            answer += (
                f" Peak activation appears around {peak}."
            )

        return answer

    if event_name == "general_career":
        overall = _safe_dict(
            forecast.get(
                "overall"
            )
        )

        return str(
            overall.get(
                "summary",
                (
                    "No clear general career forecast "
                    "was available for the requested period."
                ),
            )
        )

    return str(
        event_data.get(
            "summary",
            (
                f"A relevant {phrase} signal was "
                "identified in the requested period."
            ),
        )
    )


def _run_single_event_forecast(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    primary_event = str(
        question_analysis.get(
            "primary_event",
            "general_career",
        )
    )

    base_parser = _safe_dict(
        question_analysis.get(
            "base_parser"
        )
    )

    intent = _safe_dict(
        base_parser.get(
            "intent"
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

    (
        start,
        end,
        step_days,
        range_type,
    ) = _question_forecast_range(
        question_analysis,
        reference_moment,
    )

    package = _run_forecast(
        chart,
        start,
        end,
        step_days,
    )

    forecast = _safe_dict(
        package.get(
            "forecast"
        )
    )

    scan = _safe_dict(
        package.get(
            "scan"
        )
    )

    if primary_event == "general_career":
        overall = _safe_dict(
            forecast.get(
                "overall"
            )
        )

        return {
            "available": True,
            "route": "single_event",
            "event": "general_career",
            "event_label": (
                _event_label(
                    "general_career"
                )
            ),
            "question_type": question_type,
            "direction": direction,
            "parser_confidence": (
                parser_confidence
            ),
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "resolved_forecast_request": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "step_days": step_days,
                "range_type": range_type,
            },
            "outcome": overall.get(
                "outlook"
            ),
            "confidence": overall.get(
                "confidence"
            ),
            "answer": _build_single_event_answer(
                "general_career",
                question_type,
                direction,
                {},
                forecast,
            ),
            "overall": overall,
            "scan_metadata": {
                "available": scan.get(
                    "available"
                ),
                "start": scan.get(
                    "start"
                ),
                "end": scan.get(
                    "end"
                ),
                "step_days": scan.get(
                    "step_days"
                ),
                "snapshot_count": scan.get(
                    "snapshot_count"
                ),
            },
        }

    event = _event_data(
        forecast,
        primary_event,
    )

    window = _safe_dict(
        event.get(
            "window"
        )
    )

    probability = (
        _single_event_probability(
            event
        )
    )

    result = {
        "available": True,
        "route": "single_event",
        "event": primary_event,
        "event_label": _event_label(
            primary_event
        ),
        "question_type": question_type,
        "direction": direction,
        "parser_confidence": (
            parser_confidence
        ),
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "resolved_forecast_request": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "step_days": step_days,
            "range_type": range_type,
        },
        "forecast_available": bool(
            event.get(
                "available"
            )
        ),
        "outcome": event.get(
            "outlook"
        ),
        "confidence": event.get(
            "confidence"
        ),
        "forecast_confidence": (
            event.get(
                "confidence"
            )
        ),
        **probability,
        "confirmation": window.get(
            "confirmation"
        ),
        "answer": _build_single_event_answer(
            primary_event,
            question_type,
            direction,
            event,
            forecast,
        ),
        "window": window,
        "primary_window": window,
        "event_summary": event.get(
            "summary"
        ),
        "forecast_overall": forecast.get(
            "overall"
        ),
        "scan_metadata": {
            "available": scan.get(
                "available"
            ),
            "start": scan.get(
                "start"
            ),
            "end": scan.get(
                "end"
            ),
            "step_days": scan.get(
                "step_days"
            ),
            "snapshot_count": scan.get(
                "snapshot_count"
            ),
        },
    }

    return result


# =========================================================
# CALENDAR YEAR COMPARISON
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
        tzinfo=tzinfo,
    )

    year_end = datetime(
        year + 1,
        1,
        1,
        tzinfo=tzinfo,
    )

    if year < reference_moment.year:
        return (
            year_start,
            year_end,
            "historical_full_year",
        )

    if year == reference_moment.year:
        return (
            reference_moment,
            year_end,
            "remaining_current_year",
        )

    return (
        year_start,
        year_end,
        "future_full_year",
    )


def _comparison_strength(
    margin: float,
) -> str:
    if margin >= 1.5:
        return "clearly_better"

    if margin >= 0.5:
        return "moderately_better"

    if margin > 0:
        return "slightly_better"

    return "roughly_equal"


def _build_comparison_answer(
    target_event: str,
    best: dict[str, Any],
    second: dict[str, Any],
    strength: str,
) -> str:
    best_year = best.get("year")
    second_year = second.get("year")

    phrase = _event_phrase(
        target_event
    )

    best_window = _safe_dict(
        best.get("window")
    )

    second_window = _safe_dict(
        second.get("window")
    )

    if strength == "roughly_equal":
        answer = (
            f"The forecast does not show a meaningful "
            f"difference between {best_year} and "
            f"{second_year} for {phrase}."
        )

    else:
        answer = (
            f"{best_year} appears "
            f"{strength.replace('_', ' ')} than "
            f"{second_year} for {phrase}, based on "
            "forecast strength, Dasha-transit confirmation "
            "and event-window quality."
        )

    if best_window.get("peak_date"):
        answer += (
            f" The strongest identified window in "
            f"{best_year} peaks around "
            f"{best_window.get('peak_date')}."
        )

    if (
        strength != "roughly_equal"
        and second_window.get(
            "peak_date"
        )
    ):
        answer += (
            f" {second_year} still has a relevant window "
            f"around {second_window.get('peak_date')}, "
            "but its overall comparison score is lower."
        )

    return answer


def _run_calendar_year_comparison(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    comparison = _safe_dict(
        question_analysis.get(
            "comparison"
        )
    )

    years = []

    for value in _safe_list(
        comparison.get("values")
    ):
        year = int(value)

        if year not in years:
            years.append(year)

    if len(years) < 2:
        raise ValueError(
            "At least two calendar years are required "
            "for a comparison."
        )

    target_event = str(
        question_analysis.get(
            "primary_event",
            "general_career",
        )
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

        package = _run_forecast(
            chart,
            start,
            end,
            7,
        )

        forecast = _safe_dict(
            package.get("forecast")
        )

        event = _event_data(
            forecast,
            target_event,
        )

        scan = _safe_dict(
            package.get("scan")
        )

        results.append(
            {
                "year": year,
                "range_type": range_type,
                "event": target_event,
                "available": bool(
                    event.get(
                        "available"
                    )
                ),
                "outlook": event.get(
                    "outlook"
                ),
                "confidence": event.get(
                    "confidence"
                ),
                "comparison_score": (
                    _comparison_score(
                        event
                    )
                ),
                "window": _safe_dict(
                    event.get(
                        "window"
                    )
                ),
                "event_summary": event.get(
                    "summary"
                ),
                "forecast_overall": forecast.get(
                    "overall"
                ),
                "scan_metadata": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "step_days": 7,
                    "range_type": range_type,
                    "snapshot_count": scan.get(
                        "snapshot_count"
                    ),
                },
            }
        )

    ranked = sorted(
        results,
        key=lambda item: float(
            item.get(
                "comparison_score",
                0.0,
            )
            or 0.0
        ),
        reverse=True,
    )

    best = ranked[0]
    second = ranked[1]

    margin = round(
        float(
            best.get(
                "comparison_score",
                0.0,
            )
            or 0.0
        )
        - float(
            second.get(
                "comparison_score",
                0.0,
            )
            or 0.0
        ),
        3,
    )

    strength = _comparison_strength(
        margin
    )

    return {
        "available": True,
        "route": "calendar_year_comparison",
        "event": target_event,
        "comparison_type": "calendar_years",
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "future_aware": True,
        "current_year_trimmed": any(
            item.get(
                "range_type"
            )
            == "remaining_current_year"
            for item in results
        ),
        "years": years,
        "best_year": best.get(
            "year"
        ),
        "comparison_strength": strength,
        "margin": margin,
        "answer": _build_comparison_answer(
            target_event,
            best,
            second,
            strength,
        ),
        "ranked_results": ranked,
    }


# =========================================================
# MULTI-EVENT ROUTE
# =========================================================

def _multi_event_result(
    forecast: dict[str, Any],
    event_name: str,
) -> dict[str, Any]:
    event = _event_data(
        forecast,
        event_name,
    )

    return {
        "event": event_name,
        "event_label": _event_label(
            event_name
        ),
        "available": bool(
            event.get(
                "available"
            )
        ),
        "outlook": event.get(
            "outlook"
        ),
        "confidence": event.get(
            "confidence"
        ),
        "event_score": _comparison_score(
            event
        ),
        "summary": event.get(
            "summary"
        ),
        "window": _safe_dict(
            event.get(
                "window"
            )
        ),
    }


def _analyse_multi_event_relationship(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(results) < 2:
        return {
            "available": False,
            "relationship": (
                "insufficient_events"
            ),
            "overlap": {
                "available": False,
            },
        }

    first = results[0]
    second = results[1]

    overlap = _overlap_period(
        _safe_dict(
            first.get("window")
        ),
        _safe_dict(
            second.get("window")
        ),
    )

    first_available = bool(
        first.get(
            "available"
        )
    )

    second_available = bool(
        second.get(
            "available"
        )
    )

    if (
        first_available
        and second_available
        and overlap.get(
            "available"
        )
    ):
        relationship = (
            "both_supported_and_overlapping"
        )

    elif (
        first_available
        and second_available
    ):
        relationship = (
            "both_supported_but_separate"
        )

    elif first_available:
        relationship = (
            "first_event_supported"
        )

    elif second_available:
        relationship = (
            "second_event_supported"
        )

    else:
        relationship = (
            "neither_strongly_supported"
        )

    return {
        "available": True,
        "relationship": relationship,
        "first_event": first.get(
            "event"
        ),
        "second_event": second.get(
            "event"
        ),
        "overlap": overlap,
    }


def _build_multi_event_answer(
    results: list[dict[str, Any]],
    relationship: dict[str, Any],
) -> str:
    first = results[0]
    second = results[1]

    first_name = _event_phrase(
        str(
            first.get("event")
        )
    )

    second_name = _event_phrase(
        str(
            second.get("event")
        )
    )

    relation = str(
        relationship.get(
            "relationship"
        )
    )

    if relation == (
        "both_supported_and_overlapping"
    ):
        overlap = _safe_dict(
            relationship.get(
                "overlap"
            )
        )

        answer = (
            f"The forecast supports both {first_name} and "
            f"{second_name}. Their strongest windows "
            f"overlap from {overlap.get('start')} to "
            f"{overlap.get('end')}."
        )

        if {
            first.get("event"),
            second.get("event"),
        } == {
            "job_change",
            "income_gains",
        }:
            answer += (
                " This is consistent with improved income "
                "potential accompanying or following a job "
                "or role change."
            )

        return answer

    if relation == (
        "both_supported_but_separate"
    ):
        first_window = _safe_dict(
            first.get("window")
        )

        second_window = _safe_dict(
            second.get("window")
        )

        return (
            f"The forecast supports both {first_name} and "
            f"{second_name}, but their strongest windows "
            "are separate. "
            f"The {first_name} window runs from "
            f"{first_window.get('start')} to "
            f"{first_window.get('end')}, while the "
            f"{second_name} window runs from "
            f"{second_window.get('start')} to "
            f"{second_window.get('end')}."
        )

    if relation == "first_event_supported":
        return (
            f"The forecast shows a meaningful signal for "
            f"{first_name}, but no separately strong "
            f"{second_name} window was identified."
        )

    if relation == "second_event_supported":
        return (
            f"The forecast shows a meaningful signal for "
            f"{second_name}, but no separately strong "
            f"{first_name} window was identified."
        )

    return (
        f"No sufficiently strong standalone windows were "
        f"identified for either {first_name} or "
        f"{second_name}."
    )


def _run_multi_event_forecast(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    event_names = []

    for raw_item in _safe_list(
        question_analysis.get(
            "detected_events"
        )
    ):
        item = _safe_dict(
            raw_item
        )

        event_name = item.get(
            "event"
        )

        if (
            isinstance(
                event_name,
                str,
            )
            and event_name
            and event_name
            not in event_names
            and event_name
            != "job_loss_risk"
        ):
            event_names.append(
                event_name
            )

    if len(event_names) < 2:
        raise ValueError(
            "A multi-event question must contain at least "
            "two supported forecast events."
        )

    (
        start,
        end,
        step_days,
        range_type,
    ) = _question_forecast_range(
        question_analysis,
        reference_moment,
    )

    package = _run_forecast(
        chart,
        start,
        end,
        step_days,
    )

    forecast = _safe_dict(
        package.get(
            "forecast"
        )
    )

    scan = _safe_dict(
        package.get(
            "scan"
        )
    )

    results = [
        _multi_event_result(
            forecast,
            event_name,
        )
        for event_name in event_names
    ]

    relationship = (
        _analyse_multi_event_relationship(
            results
        )
    )

    return {
        "available": True,
        "route": "multi_event",
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "events": event_names,
        "event_count": len(
            event_names
        ),
        "resolved_forecast_request": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "step_days": step_days,
            "range_type": range_type,
        },
        "answer": _build_multi_event_answer(
            results,
            relationship,
        ),
        "relationship": relationship,
        "event_results": results,
        "ranked_events": sorted(
            results,
            key=lambda item: float(
                item.get(
                    "event_score",
                    0.0,
                )
                or 0.0
            ),
            reverse=True,
        ),
        "forecast_overall": forecast.get(
            "overall"
        ),
        "scan_metadata": {
            "available": scan.get(
                "available"
            ),
            "start": scan.get(
                "start"
            ),
            "end": scan.get(
                "end"
            ),
            "step_days": scan.get(
                "step_days"
            ),
            "snapshot_count": scan.get(
                "snapshot_count"
            ),
        },
    }


# =========================================================
# EMPLOYMENT-RISK ROUTE
# =========================================================

def _risk_component(
    forecast: dict[str, Any],
    event_name: str,
) -> dict[str, Any]:
    event = _event_data(
        forecast,
        event_name,
    )

    score = _comparison_score(
        event
    )

    return {
        "event": event_name,
        "label": _event_label(
            event_name
        ),
        "available": bool(
            event.get(
                "available"
            )
        ),
        "outlook": event.get(
            "outlook"
        ),
        "confidence": event.get(
            "confidence"
        ),
        "score": score,
        "normalized_evidence": (
            _normalise_router_score(
                score
            )
        ),
        "window": _safe_dict(
            event.get(
                "window"
            )
        ),
        "summary": event.get(
            "summary"
        ),
    }


def _employment_risk_score(
    pressure: dict[str, Any],
    transition: dict[str, Any],
    promotion: dict[str, Any],
    income: dict[str, Any],
) -> dict[str, Any]:
    pressure_evidence = float(
        pressure.get(
            "normalized_evidence",
            0.0,
        )
        or 0.0
    )

    transition_evidence = float(
        transition.get(
            "normalized_evidence",
            0.0,
        )
        or 0.0
    )

    promotion_evidence = float(
        promotion.get(
            "normalized_evidence",
            0.0,
        )
        or 0.0
    )

    income_evidence = float(
        income.get(
            "normalized_evidence",
            0.0,
        )
        or 0.0
    )

    overlap = _overlap_period(
        _safe_dict(
            pressure.get("window")
        ),
        _safe_dict(
            transition.get("window")
        ),
    )

    pressure_contribution = (
        pressure_evidence
        * 0.50
    )

    transition_contribution = (
        transition_evidence
        * 0.20
    )

    overlap_contribution = (
        0.12
        if overlap.get(
            "available"
        )
        else 0.0
    )

    promotion_offset = (
        promotion_evidence
        * 0.12
    )

    income_offset = (
        income_evidence
        * 0.08
    )

    supportive_offset = (
        promotion_offset
        + income_offset
    )

    instability_score = (
        pressure_contribution
        + transition_contribution
        + overlap_contribution
        - supportive_offset
    )

    instability_score = round(
        max(
            0.0,
            min(
                1.0,
                instability_score,
            ),
        ),
        2,
    )

    if instability_score >= 0.75:
        level = "high"

    elif instability_score >= 0.50:
        level = "elevated"

    elif instability_score >= 0.30:
        level = "moderate"

    else:
        level = "low"

    job_loss_score = round(
        min(
            instability_score
            * 0.55,
            0.49,
        ),
        2,
    )

    if job_loss_score >= 0.40:
        job_loss_level = (
            "moderate_unconfirmed"
        )

    elif job_loss_score >= 0.25:
        job_loss_level = (
            "low_to_moderate_unconfirmed"
        )

    else:
        job_loss_level = (
            "low_unconfirmed"
        )

    return {
        "risk_level": level,
        "risk_score": instability_score,
        "risk_basis": (
            "employment_instability_and_restructuring"
        ),
        "job_loss_specific_signal": (
            "unconfirmed"
        ),
        "job_loss_specific_level": (
            job_loss_level
        ),
        "job_loss_specific_score": (
            job_loss_score
        ),
        "pressure_transition_overlap": (
            overlap
        ),
        "evidence": {
            "pressure": round(
                pressure_evidence,
                3,
            ),
            "transition": round(
                transition_evidence,
                3,
            ),
            "promotion": round(
                promotion_evidence,
                3,
            ),
            "income": round(
                income_evidence,
                3,
            ),
        },
        "direct_job_loss_evidence_available": (
            False
        ),
    }


def _build_employment_risk_answer(
    result: dict[str, Any],
    pressure: dict[str, Any],
    transition: dict[str, Any],
    promotion: dict[str, Any],
    income: dict[str, Any],
) -> str:
    level = str(
        result.get(
            "risk_level",
            "low",
        )
    )

    if level == "high":
        answer = (
            "The forecast shows a high career-instability "
            "or restructuring signal in the requested "
            "period."
        )

    elif level == "elevated":
        answer = (
            "The forecast shows an elevated period of "
            "career instability, restructuring or "
            "professional uncertainty."
        )

    elif level == "moderate":
        answer = (
            "The forecast shows a moderate period of "
            "career instability or restructuring."
        )

    else:
        answer = (
            "The forecast does not show a strong "
            "career-instability signal in the requested "
            "period."
        )

    if (
        pressure.get(
            "available"
        )
        and transition.get(
            "available"
        )
    ):
        answer += (
            " Both career pressure and professional "
            "transition are active."
        )

    overlap = _safe_dict(
        result.get(
            "pressure_transition_overlap"
        )
    )

    if overlap.get(
        "available"
    ):
        answer += (
            f" Their strongest windows overlap from "
            f"{overlap.get('start')} to "
            f"{overlap.get('end')}."
        )

    if promotion.get(
        "available"
    ):
        peak = _safe_dict(
            promotion.get(
                "window"
            )
        ).get(
            "peak_date"
        )

        if peak:
            answer += (
                f" A separate recognition signal appears "
                f"around {peak}, providing a constructive "
                "alternative interpretation."
            )

    if income.get(
        "available"
    ):
        answer += (
            " Professional-gains support is also present."
        )

    answer += (
        " Importantly, the engine does not contain enough "
        "job-loss-specific evidence to classify involuntary "
        "employment loss as highly likely."
    )

    return answer


def _run_employment_risk_forecast(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    (
        start,
        end,
        step_days,
        range_type,
    ) = _question_forecast_range(
        question_analysis,
        reference_moment,
    )

    package = _run_forecast(
        chart,
        start,
        end,
        step_days,
    )

    forecast = _safe_dict(
        package.get(
            "forecast"
        )
    )

    scan = _safe_dict(
        package.get(
            "scan"
        )
    )

    pressure = _risk_component(
        forecast,
        "career_pressure_challenge",
    )

    transition = _risk_component(
        forecast,
        "job_change",
    )

    promotion = _risk_component(
        forecast,
        "promotion_recognition",
    )

    income = _risk_component(
        forecast,
        "income_gains",
    )

    result = _employment_risk_score(
        pressure,
        transition,
        promotion,
        income,
    )

    return {
        "available": True,
        "route": "employment_risk",
        "event": "job_loss_risk",
        "event_label": (
            "Job Loss / Employment Risk"
        ),
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "resolved_forecast_request": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "step_days": step_days,
            "range_type": range_type,
        },
        "risk_level": result.get(
            "risk_level"
        ),
        "risk_score": result.get(
            "risk_score"
        ),
        "risk_basis": result.get(
            "risk_basis"
        ),
        "job_loss_specific_signal": (
            result.get(
                "job_loss_specific_signal"
            )
        ),
        "job_loss_specific_level": (
            result.get(
                "job_loss_specific_level"
            )
        ),
        "job_loss_specific_score": (
            result.get(
                "job_loss_specific_score"
            )
        ),
        "answer": (
            _build_employment_risk_answer(
                result,
                pressure,
                transition,
                promotion,
                income,
            )
        ),
        "risk_analysis": result,
        "components": {
            "career_pressure_challenge": pressure,
            "job_change": transition,
            "promotion_recognition": promotion,
            "income_gains": income,
        },
        "forecast_overall": forecast.get(
            "overall"
        ),
        "scan_metadata": {
            "available": scan.get(
                "available"
            ),
            "start": scan.get(
                "start"
            ),
            "end": scan.get(
                "end"
            ),
            "step_days": scan.get(
                "step_days"
            ),
            "snapshot_count": scan.get(
                "snapshot_count"
            ),
        },
    }


# =========================================================
# FOLLOW-UP CONTEXT
# =========================================================

def _context_question_analysis(
    previous_context: dict[str, Any],
) -> dict[str, Any]:
    direct = _safe_dict(
        previous_context.get(
            "question_analysis"
        )
    )

    if direct:
        return direct

    direct = _safe_dict(
        previous_context.get(
            "understanding"
        )
    )

    if direct:
        return direct

    if previous_context.get(
        "primary_event"
    ):
        return previous_context

    return {}


def _context_route_result(
    previous_context: dict[str, Any],
) -> dict[str, Any]:
    result = _safe_dict(
        previous_context.get(
            "route_result"
        )
    )

    if result:
        return result

    return _safe_dict(
        previous_context.get(
            "result"
        )
    )


def _inherit_follow_up_event(
    previous_context: dict[str, Any],
) -> str:
    analysis = _context_question_analysis(
        previous_context
    )

    event = analysis.get(
        "primary_event"
    )

    if (
        isinstance(
            event,
            str,
        )
        and event
        and event
        != "general_career"
    ):
        return event

    result = _context_route_result(
        previous_context
    )

    event = result.get(
        "event"
    )

    if (
        isinstance(
            event,
            str,
        )
        and event
        and event
        != "general_career"
    ):
        return event

    events = _safe_list(
        result.get("events")
    )

    if (
        events
        and isinstance(
            events[0],
            str,
        )
    ):
        return events[0]

    return "general_career"


# =========================================================
# FOLLOW-UP MONTH
# =========================================================

def _resolve_follow_up_month(
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    month_reference = _safe_dict(
        question_analysis.get(
            "month_reference"
        )
    )

    months = _safe_list(
        month_reference.get(
            "months"
        )
    )

    if not months:
        raise ValueError(
            "Follow-up question does not contain a "
            "recognised month reference."
        )

    selected = _safe_dict(
        months[0]
    )

    month_number = int(
        selected.get("month")
    )

    month_name = str(
        selected.get("name")
    )

    year = reference_moment.year

    if month_number < reference_moment.month:
        year += 1

    tzinfo = reference_moment.tzinfo

    calendar_start = datetime(
        year,
        month_number,
        1,
        tzinfo=tzinfo,
    )

    if month_number == 12:
        month_end = datetime(
            year + 1,
            1,
            1,
            tzinfo=tzinfo,
        )

    else:
        month_end = datetime(
            year,
            month_number + 1,
            1,
            tzinfo=tzinfo,
        )

    requested_start = calendar_start

    if (
        year == reference_moment.year
        and month_number
        == reference_moment.month
    ):
        requested_start = reference_moment

    return {
        "month": month_number,
        "month_name": month_name,
        "year": year,
        "label": (
            f"{month_name} {year}"
        ),
        "start": requested_start,
        "calendar_start": calendar_start,
        "end": month_end,
    }


def _build_follow_up_buffer(
    month_data: dict[str, Any],
    reference_moment: datetime,
) -> tuple[
    datetime,
    datetime,
]:
    scan_start = (
        month_data[
            "calendar_start"
        ]
        - timedelta(
            days=FOLLOW_UP_BUFFER_DAYS
        )
    )

    scan_end = (
        month_data[
            "end"
        ]
        + timedelta(
            days=FOLLOW_UP_BUFFER_DAYS
        )
    )

    if scan_start < reference_moment:
        scan_start = reference_moment

    return (
        scan_start,
        scan_end,
    )


def _month_window_relationship(
    month_data: dict[str, Any],
    event_window: dict[str, Any],
) -> dict[str, Any]:
    if not event_window:
        return {
            "available": False,
            "relationship": (
                "no_event_window"
            ),
        }

    month_start = month_data[
        "start"
    ]

    month_end = month_data[
        "end"
    ]

    tzinfo = month_start.tzinfo

    event_start = (
        _parse_window_datetime(
            event_window.get(
                "start"
            ),
            tzinfo,
        )
    )

    event_end = (
        _parse_window_datetime(
            event_window.get(
                "end"
            ),
            tzinfo,
        )
    )

    if (
        event_start is None
        or event_end is None
    ):
        return {
            "available": False,
            "relationship": (
                "invalid_event_window"
            ),
        }

    if event_end < month_start:
        return {
            "available": True,
            "relationship": (
                "window_ended_before_month"
            ),
            "overlap": {
                "available": False,
            },
        }

    if event_start >= month_end:
        return {
            "available": True,
            "relationship": (
                "window_starts_after_month"
            ),
            "overlap": {
                "available": False,
            },
        }

    overlap_start = max(
        event_start,
        month_start,
    )

    overlap_end = min(
        event_end,
        month_end,
    )

    if (
        event_start < month_start
        and event_end < month_end
    ):
        relationship = (
            "window_carries_into_month_and_ends"
        )

    elif (
        event_start < month_start
        and event_end >= month_end
    ):
        relationship = (
            "month_inside_broader_window"
        )

    elif (
        event_start >= month_start
        and event_end < month_end
    ):
        relationship = (
            "window_starts_and_ends_in_month"
        )

    else:
        relationship = (
            "window_starts_in_month_and_continues"
        )

    return {
        "available": True,
        "relationship": relationship,
        "overlap": {
            "available": True,
            "start": (
                overlap_start.date().isoformat()
            ),
            "end": (
                overlap_end.date().isoformat()
            ),
        },
    }


def _build_follow_up_answer(
    event_name: str,
    month_data: dict[str, Any],
    event_data: dict[str, Any],
    relationship: dict[str, Any],
) -> str:
    label = str(
        month_data.get("label")
    )

    phrase = _event_phrase(
        event_name
    )

    if not event_data.get(
        "available"
    ):
        return (
            f"For {label}, the buffered forecast does not "
            f"identify a sufficiently strong {phrase} "
            "window affecting the month."
        )

    window = _safe_dict(
        event_data.get("window")
    )

    relation = str(
        relationship.get(
            "relationship"
        )
    )

    start = window.get("start")
    end = window.get("end")
    peak = window.get(
        "peak_date"
    )

    if relation == (
        "window_carries_into_month_and_ends"
    ):
        answer = (
            f"{label} remains part of a broader {phrase} "
            f"window that began before the month. The "
            f"broader window runs from {start} to {end}, "
            "so the signal is active during the earlier "
            "part of the month and then begins to ease."
        )

    elif relation == (
        "month_inside_broader_window"
    ):
        answer = (
            f"{label} sits inside a broader {phrase} "
            f"window running from {start} to {end}."
        )

    elif relation == (
        "window_starts_and_ends_in_month"
    ):
        answer = (
            f"A distinct {phrase} window falls within "
            f"{label}, running from {start} to {end}."
        )

    elif relation == (
        "window_starts_in_month_and_continues"
    ):
        answer = (
            f"A broader {phrase} window begins during "
            f"{label} and continues beyond the month, "
            f"running from {start} to {end}."
        )

    elif relation == (
        "window_ended_before_month"
    ):
        return (
            f"The stronger {phrase} window ends before "
            f"{label}, so the month itself is not part "
            "of the main activation period."
        )

    elif relation == (
        "window_starts_after_month"
    ):
        return (
            f"The stronger {phrase} window begins after "
            f"{label}, so the month itself is not the "
            "main activation period."
        )

    else:
        answer = (
            f"{label} overlaps a broader {phrase} window "
            f"running from {start} to {end}."
        )

    if peak:
        answer += (
            f" The broader window's strongest activation "
            f"occurs around {peak}."
        )

    return answer


def _run_follow_up_forecast(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
    previous_context: dict[str, Any],
) -> dict[str, Any]:
    if not previous_context:
        return {
            "available": False,
            "route": "follow_up",
            "requires_context": True,
            "reason": (
                "The follow-up question requires previous "
                "career-question context so the target "
                "event can be inherited."
            ),
        }

    inherited_event = (
        _inherit_follow_up_event(
            previous_context
        )
    )

    if inherited_event == "general_career":
        return {
            "available": False,
            "route": "follow_up",
            "requires_context": True,
            "reason": (
                "Previous context did not contain a "
                "specific career event to inherit."
            ),
        }

    month_data = (
        _resolve_follow_up_month(
            question_analysis,
            reference_moment,
        )
    )

    (
        buffered_start,
        buffered_end,
    ) = _build_follow_up_buffer(
        month_data,
        reference_moment,
    )

    package = _run_forecast(
        chart,
        buffered_start,
        buffered_end,
        3,
    )

    forecast = _safe_dict(
        package.get(
            "forecast"
        )
    )

    scan = _safe_dict(
        package.get(
            "scan"
        )
    )

    event = _event_data(
        forecast,
        inherited_event,
    )

    broader_window = _safe_dict(
        event.get(
            "window"
        )
    )

    relationship = (
        _month_window_relationship(
            month_data,
            broader_window,
        )
    )

    return {
        "available": True,
        "route": "follow_up_month",
        "requires_context": True,
        "context_used": True,
        "inherited_event": inherited_event,
        "event_label": _event_label(
            inherited_event
        ),
        "reference_moment": (
            reference_moment.isoformat()
        ),
        "resolved_month": {
            "month": month_data.get(
                "month"
            ),
            "month_name": month_data.get(
                "month_name"
            ),
            "year": month_data.get(
                "year"
            ),
            "label": month_data.get(
                "label"
            ),
        },
        "requested_month_scope": {
            "start": month_data[
                "start"
            ].isoformat(),
            "end": month_data[
                "end"
            ].isoformat(),
        },
        "buffered_scan_request": {
            "start": (
                buffered_start.isoformat()
            ),
            "end": (
                buffered_end.isoformat()
            ),
            "step_days": 3,
            "buffer_days": (
                FOLLOW_UP_BUFFER_DAYS
            ),
            "range_type": (
                "buffered_follow_up_month"
            ),
        },
        "month_window_relationship": (
            relationship
        ),
        "answer": _build_follow_up_answer(
            inherited_event,
            month_data,
            event,
            relationship,
        ),
        "event_result": {
            "event": inherited_event,
            "available": bool(
                event.get(
                    "available"
                )
            ),
            "outlook": event.get(
                "outlook"
            ),
            "confidence": event.get(
                "confidence"
            ),
            "score": _comparison_score(
                event
            ),
            "summary": event.get(
                "summary"
            ),
            "broader_window": (
                broader_window
            ),
        },
        "forecast_overall": forecast.get(
            "overall"
        ),
        "scan_metadata": {
            "available": scan.get(
                "available"
            ),
            "start": scan.get(
                "start"
            ),
            "end": scan.get(
                "end"
            ),
            "step_days": scan.get(
                "step_days"
            ),
            "snapshot_count": scan.get(
                "snapshot_count"
            ),
        },
    }


# =========================================================
# MAIN V3 ROUTER
# =========================================================

def route_career_question_v3(
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

    context = (
        previous_context
        if isinstance(
            previous_context,
            dict,
        )
        else {}
    )

    query_mode = str(
        question_analysis.get(
            "query_mode",
            "single_event",
        )
    )

    comparison = _safe_dict(
        question_analysis.get(
            "comparison"
        )
    )

    if (
        query_mode == "comparison"
        and comparison.get(
            "comparison_type"
        )
        == "calendar_years"
    ):
        return (
            _run_calendar_year_comparison(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    if query_mode == "multi_event":
        return (
            _run_multi_event_forecast(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    if query_mode == "risk":
        return (
            _run_employment_risk_forecast(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    if query_mode == "follow_up":
        return (
            _run_follow_up_forecast(
                chart,
                question_analysis,
                reference_moment,
                context,
            )
        )

    if query_mode == "single_event":
        return (
            _run_single_event_forecast(
                chart,
                question_analysis,
                reference_moment,
            )
        )

    return {
        "available": False,
        "route": query_mode,
        "event": question_analysis.get(
            "primary_event"
        ),
        "reason": (
            "This V3 routing mode has not yet been "
            "implemented."
        ),
    }