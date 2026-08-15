from datetime import datetime
from typing import Any


EVENT_CONFIG = {
    "job_change": {
        "label": "Job Change / Professional Transition",
        "supportive_outlooks": {
            "strongly_supportive",
            "supportive",
            "active",
        },
    },
    "promotion_recognition": {
        "label": "Promotion / Recognition",
        "supportive_outlooks": {
            "strongly_supportive",
            "supportive",
            "active",
        },
    },
    "income_gains": {
        "label": "Income / Professional Gains",
        "supportive_outlooks": {
            "strongly_supportive",
            "supportive",
            "active",
        },
    },
    "foreign_international_opportunity": {
        "label": "Foreign / International Opportunity",
        "supportive_outlooks": {
            "strongly_supportive",
            "supportive",
            "active",
        },
    },
    "career_pressure_challenge": {
        "label": "Career Pressure / Challenge",
        "supportive_outlooks": {
            "high_pressure",
            "elevated_pressure",
            "moderate_pressure",
        },
    },
}


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _safe_list(
    value: Any,
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _parse_datetime(
    value: Any,
) -> datetime | None:
    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(
            value
        )

    except ValueError:
        return None


def _format_date(
    value: Any,
) -> str | None:
    if not isinstance(value, str):
        return None

    if len(value) >= 10:
        return value[:10]

    return value


def _extract_reasons(
    period: dict[str, Any],
    limit: int = 4,
) -> list[str]:
    results: list[str] = []

    for indicator in _safe_list(
        period.get("indicators")
    ):

        interpretation = indicator.get(
            "interpretation"
        )

        if not isinstance(
            interpretation,
            str,
        ):
            continue

        interpretation = (
            interpretation.strip()
        )

        if (
            interpretation
            and interpretation not in results
        ):
            results.append(
                interpretation
            )

        if len(results) >= limit:
            break

    return results


def _current_reference(
    current_dasha: dict[str, Any],
) -> datetime | None:
    """
    Use the current Antardasha start as the
    reference point for filtering old periods.
    """

    return _parse_datetime(
        current_dasha.get(
            "antardasha_start"
        )
    )


def _current_period_end(
    current_dasha: dict[str, Any],
) -> datetime | None:
    return _parse_datetime(
        current_dasha.get(
            "antardasha_end"
        )
    )


def _is_current_or_future(
    period: dict[str, Any],
    reference: datetime | None,
) -> bool:
    """
    Keep only the current period and periods that
    have not already ended.

    Strict > is intentional. It prevents the previous
    Antardasha, whose end equals the current period start,
    from appearing as an upcoming period.
    """

    if reference is None:
        return True

    period_end = _parse_datetime(
        period.get("end")
    )

    if period_end is None:
        return True

    return period_end > reference


def _is_same_period(
    period: dict[str, Any],
    current_dasha: dict[str, Any],
) -> bool:
    return (
        period.get("mahadasha")
        == current_dasha.get(
            "mahadasha"
        )
        and period.get("antardasha")
        == current_dasha.get(
            "antardasha"
        )
    )


def _period_start(
    period: dict[str, Any],
) -> datetime | None:
    return _parse_datetime(
        period.get("start")
    )


def _build_period_summary(
    period: dict[str, Any],
) -> dict[str, Any]:
    if not period:
        return {}

    return {
        "event": period.get(
            "event"
        ),
        "period": period.get(
            "period"
        ),
        "mahadasha": period.get(
            "mahadasha"
        ),
        "antardasha": period.get(
            "antardasha"
        ),
        "start": _format_date(
            period.get(
                "start"
            )
        ),
        "end": _format_date(
            period.get(
                "end"
            )
        ),
        "score": _safe_float(
            period.get(
                "score"
            )
        ),
        "outlook": period.get(
            "outlook"
        ),
        "scores": _safe_dict(
            period.get(
                "scores"
            )
        ),
        "reasons": _extract_reasons(
            period
        ),
    }


def _is_relevant_period(
    event_name: str,
    period: dict[str, Any],
) -> bool:
    config = EVENT_CONFIG.get(
        event_name,
        {},
    )

    allowed = config.get(
        "supportive_outlooks",
        set(),
    )

    return (
        period.get("outlook")
        in allowed
    )


def _select_current_period(
    periods: list[dict[str, Any]],
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    for period in periods:

        if _is_same_period(
            period,
            current_dasha,
        ):
            return period

    return {}


def _select_nearest_relevant(
    event_name: str,
    periods: list[dict[str, Any]],
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    """
    Select the nearest relevant period AFTER
    the current Antardasha.
    """

    current_end = _current_period_end(
        current_dasha
    )

    candidates: list[
        dict[str, Any]
    ] = []

    for period in periods:

        start = _period_start(
            period
        )

        if start is None:
            continue

        if (
            current_end is not None
            and start < current_end
        ):
            continue

        if not _is_relevant_period(
            event_name,
            period,
        ):
            continue

        candidates.append(
            period
        )

    if not candidates:
        return {}

    candidates.sort(
        key=lambda item: (
            _period_start(
                item
            )
            or datetime.max.replace(
                tzinfo=(
                    current_end.tzinfo
                    if current_end
                    else None
                )
            ),
            -_safe_float(
                item.get(
                    "score"
                )
            ),
        )
    )

    return candidates[0]


def _select_strongest_upcoming(
    event_name: str,
    periods: list[dict[str, Any]],
    current_dasha: dict[str, Any],
    horizon_years: int = 15,
) -> dict[str, Any]:
    """
    Select the strongest practical period within
    a near-to-medium-term horizon.
    """

    reference = _current_reference(
        current_dasha
    )

    if reference is None:
        return {}

    horizon_year = (
        reference.year
        + horizon_years
    )

    candidates: list[
        dict[str, Any]
    ] = []

    for period in periods:

        start = _period_start(
            period
        )

        if start is None:
            continue

        if start < reference:
            continue

        if start.year > horizon_year:
            continue

        if not _is_relevant_period(
            event_name,
            period,
        ):
            continue

        candidates.append(
            period
        )

    if not candidates:
        return {}

    candidates.sort(
        key=lambda item: (
            -_safe_float(
                item.get(
                    "score"
                )
            ),
            str(
                item.get(
                    "start",
                    "",
                )
            ),
        )
    )

    return candidates[0]


def _select_strongest_long_term(
    periods: list[dict[str, Any]],
    current_dasha: dict[str, Any],
    horizon_years: int = 20,
) -> dict[str, Any]:
    """
    Select the strongest meaningful long-term period
    within a practical future horizon.

    Raw Vimshottari calculations may extend for many
    decades. The user-facing layer intentionally avoids
    returning dates such as 2108 as practical career advice.
    """

    if not periods:
        return {}

    reference = _current_reference(
        current_dasha
    )

    if reference is None:
        return {}

    horizon_year = (
        reference.year
        + horizon_years
    )

    candidates: list[
        dict[str, Any]
    ] = []

    for period in periods:

        start = _period_start(
            period
        )

        if start is None:
            continue

        if start < reference:
            continue

        if start.year > horizon_year:
            continue

        candidates.append(
            period
        )

    if not candidates:
        return {}

    candidates.sort(
        key=lambda item: (
            -_safe_float(
                item.get(
                    "score"
                )
            ),
            str(
                item.get(
                    "start",
                    "",
                )
            ),
        )
    )

    return candidates[0]


def _select_chronological_windows(
    event_name: str,
    periods: list[dict[str, Any]],
    current_dasha: dict[str, Any],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Return useful current/future event windows
    in chronological order.
    """

    reference = _current_reference(
        current_dasha
    )

    candidates = [
        period
        for period in periods
        if (
            _is_current_or_future(
                period,
                reference,
            )
            and _is_relevant_period(
                event_name,
                period,
            )
        )
    ]

    candidates.sort(
        key=lambda item: (
            _period_start(
                item
            )
            or datetime.max.replace(
                tzinfo=(
                    reference.tzinfo
                    if reference
                    else None
                )
            ),
            -_safe_float(
                item.get(
                    "score"
                )
            ),
        )
    )

    return candidates[:limit]


def _build_event_summary(
    event_name: str,
    current_period: dict[str, Any],
    nearest_window: dict[str, Any],
    strongest_upcoming: dict[str, Any],
) -> str:
    label = EVENT_CONFIG.get(
        event_name,
        {},
    ).get(
        "label",
        event_name,
    )

    if event_name == (
        "career_pressure_challenge"
    ):

        if current_period:

            current_outlook = (
                current_period.get(
                    "outlook"
                )
            )

            return (
                f"{label}: the current period is classified as "
                f"{current_outlook}. This represents a "
                "period-specific pressure signal rather than "
                "a permanent career condition."
            )

        if nearest_window:

            return (
                f"{label}: the next notable pressure window is "
                f"{nearest_window.get('period')} from "
                f"{_format_date(nearest_window.get('start'))} "
                f"to {_format_date(nearest_window.get('end'))}."
            )

        return (
            f"{label}: no notable upcoming pressure "
            "window was identified."
        )

    parts: list[str] = []

    if current_period:

        parts.append(
            f"the current period shows "
            f"{current_period.get('outlook')} activation"
        )

    if nearest_window:

        parts.append(
            f"the next relevant window is "
            f"{nearest_window.get('period')} from "
            f"{_format_date(nearest_window.get('start'))} "
            f"to {_format_date(nearest_window.get('end'))}"
        )

    if (
        strongest_upcoming
        and (
            not nearest_window
            or strongest_upcoming.get(
                "period"
            )
            != nearest_window.get(
                "period"
            )
        )
    ):

        parts.append(
            f"the strongest practical upcoming window is "
            f"{strongest_upcoming.get('period')} from "
            f"{_format_date(strongest_upcoming.get('start'))} "
            f"to {_format_date(strongest_upcoming.get('end'))}"
        )

    if not parts:

        return (
            f"{label}: no sufficiently strong upcoming "
            "timing signal was identified."
        )

    return (
        f"{label}: "
        + "; ".join(
            parts
        )
        + "."
    )


def _synthesize_one_event(
    event_name: str,
    event_result: dict[str, Any],
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    periods = _safe_list(
        event_result.get(
            "periods"
        )
    )

    reference = _current_reference(
        current_dasha
    )

    future_periods = [
        period
        for period in periods
        if _is_current_or_future(
            period,
            reference,
        )
    ]

    current_raw = (
        _select_current_period(
            periods,
            current_dasha,
        )
    )

    nearest_raw = (
        _select_nearest_relevant(
            event_name,
            future_periods,
            current_dasha,
        )
    )

    strongest_upcoming_raw = (
        _select_strongest_upcoming(
            event_name,
            future_periods,
            current_dasha,
            horizon_years=15,
        )
    )

    strongest_long_term_raw = (
        _select_strongest_long_term(
            future_periods,
            current_dasha,
            horizon_years=20,
        )
    )

    chronological_raw = (
        _select_chronological_windows(
            event_name,
            future_periods,
            current_dasha,
            limit=5,
        )
    )

    summary = _build_event_summary(
        event_name,
        current_raw,
        nearest_raw,
        strongest_upcoming_raw,
    )

    return {
        "label": EVENT_CONFIG.get(
            event_name,
            {},
        ).get(
            "label",
            event_name,
        ),

        "summary": summary,

        "current_period": (
            _build_period_summary(
                current_raw
            )
            if current_raw
            else {}
        ),

        "nearest_relevant_window": (
            _build_period_summary(
                nearest_raw
            )
            if nearest_raw
            else {}
        ),

        "strongest_upcoming_window": (
            _build_period_summary(
                strongest_upcoming_raw
            )
            if strongest_upcoming_raw
            else {}
        ),

        "strongest_long_term_window": (
            _build_period_summary(
                strongest_long_term_raw
            )
            if strongest_long_term_raw
            else {}
        ),

        "upcoming_windows": [
            _build_period_summary(
                period
            )
            for period in chronological_raw
        ],

        "future_period_count": len(
            future_periods
        ),
    }


def synthesize_career_event_timing(
    career_event_timing: dict[str, Any],
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert raw event-specific Dasha rankings into
    practical current and future career-event windows.

    This layer intentionally separates:
    - current event signal
    - next relevant period
    - strongest practical upcoming period
    - strongest meaningful long-term period
    - chronological upcoming periods
    """

    if not career_event_timing.get(
        "available"
    ):

        return {
            "available": False,
            "reason": (
                "Career event timing analysis is unavailable."
            ),
        }

    raw_events = _safe_dict(
        career_event_timing.get(
            "events"
        )
    )

    results: dict[
        str,
        dict[str, Any],
    ] = {}

    for event_name in EVENT_CONFIG:

        raw_event = _safe_dict(
            raw_events.get(
                event_name
            )
        )

        results[event_name] = (
            _synthesize_one_event(
                event_name,
                raw_event,
                current_dasha,
            )
        )

    return {
        "available": True,

        "current_dasha": {
            "mahadasha": (
                current_dasha.get(
                    "mahadasha"
                )
            ),
            "antardasha": (
                current_dasha.get(
                    "antardasha"
                )
            ),
            "start": _format_date(
                current_dasha.get(
                    "antardasha_start"
                )
            ),
            "end": _format_date(
                current_dasha.get(
                    "antardasha_end"
                )
            ),
        },

        "events": results,
    }