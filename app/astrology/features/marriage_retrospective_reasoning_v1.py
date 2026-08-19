from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.marriage_forecast_v2 import scan_marriage_forecast_v2


def _peak_score(event_data: dict[str, Any]) -> float:
    primary = event_data.get("primary_window") if isinstance(event_data, dict) else None
    if not isinstance(primary, dict):
        return 0.0
    peak = primary.get("peak")
    if not isinstance(peak, dict):
        return 0.0
    try:
        return float(peak.get("score") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def analyze_past_marriage_periods_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 10,
    step_days: int = 14,
) -> dict[str, Any]:
    """Find the strongest symbolic marriage period before reference_moment.

    The existing marriage forecast engine already supports arbitrary timezone-aware
    start/end dates up to a 10-year scan. This wrapper converts that capability into
    a retrospective answer and never treats a high-scoring period as proof that a
    marriage actually occurred.
    """
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if lookback_years < 1 or lookback_years > 10:
        raise ValueError("lookback_years must be between 1 and 10.")

    start = reference_moment - timedelta(days=365 * lookback_years)
    end = reference_moment - timedelta(days=1)
    forecast = scan_marriage_forecast_v2(chart, start, end, step_days=step_days)
    events = forecast.get("events") if isinstance(forecast.get("events"), dict) else {}
    marriage_event = events.get("marriage_timing") if isinstance(events.get("marriage_timing"), dict) else {}

    primary = marriage_event.get("primary_window") if isinstance(marriage_event, dict) else None
    available = isinstance(primary, dict) and bool(primary)

    if not available:
        return {
            "available": False,
            "event": "past_marriage_timing",
            "model_version": "v1",
            "lookback_years": lookback_years,
            "reason": "No qualifying historical marriage-timing window was found in the requested period.",
            "limitation": "Historical strength is symbolic evidence, not proof that a marriage actually occurred.",
        }

    return {
        "available": True,
        "event": "past_marriage_timing",
        "model_version": "v1",
        "lookback_years": lookback_years,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "strongest_window": primary,
        "strongest_score": round(_peak_score(marriage_event), 3),
        "answer": (
            "The strongest historical marriage-support period in the scanned range "
            "is the primary window shown below. This should be compared with the user's "
            "actual relationship history rather than treated as proof of an event."
        ),
        "limitation": "Historical strength is symbolic evidence, not proof that a marriage actually occurred.",
        "forecast": forecast,
    }
