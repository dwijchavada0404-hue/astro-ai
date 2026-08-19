from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.marriage_forecast_v2 import scan_marriage_forecast_v2


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _peak_score(event_data: dict[str, Any]) -> float:
    primary = _safe_dict(event_data.get("primary_window"))
    peak = _safe_dict(primary.get("peak"))
    try:
        return round(float(peak.get("score") or 0.0), 3)
    except (TypeError, ValueError):
        return 0.0


def _marriage_event(forecast: dict[str, Any]) -> dict[str, Any]:
    events = _safe_dict(forecast.get("events"))
    return _safe_dict(events.get("marriage_timing"))


def _window(event_data: dict[str, Any]) -> dict[str, Any] | None:
    primary = event_data.get("primary_window")
    return primary if isinstance(primary, dict) and primary else None


def _comparison(past_score: float, future_score: float) -> str:
    delta = round(future_score - past_score, 3)
    if abs(delta) <= 0.08:
        return "similar_strength"
    return "future_stronger" if delta > 0 else "past_stronger"


def _future_language(relationship_status: str) -> str:
    if relationship_status == "married":
        return "future relationship / commitment-supportive period"
    if relationship_status in {"divorced", "widowed"}:
        return "future remarriage / commitment-supportive period"
    if relationship_status == "engaged":
        return "future wedding / formalisation-supportive period"
    return "future marriage-supportive period"


def analyze_marriage_timing_bidirectional_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    relationship_status: str = "unknown",
    lookback_years: int = 5,
    lookahead_years: int = 5,
    step_days: int = 14,
) -> dict[str, Any]:
    """Compare strongest historical and upcoming marriage-supportive windows.

    This is intended for ordinary questions such as "When will I get married?".
    The response carries both a historical calibration window and an upcoming
    window. Historical strength is never treated as proof that marriage occurred.
    For a user already known to be married, future peaks are described as broader
    relationship/commitment phases unless remarriage is explicitly intended.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10:
        raise ValueError("lookback_years must be between 1 and 10.")
    if not 1 <= lookahead_years <= 10:
        raise ValueError("lookahead_years must be between 1 and 10.")
    if not 1 <= step_days <= 31:
        raise ValueError("step_days must be between 1 and 31.")

    past_start = reference_moment - timedelta(days=365 * lookback_years)
    past_end = reference_moment - timedelta(days=1)
    future_start = reference_moment
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    past_forecast = scan_marriage_forecast_v2(chart, past_start, past_end, step_days=step_days)
    future_forecast = scan_marriage_forecast_v2(chart, future_start, future_end, step_days=step_days)

    past_event = _marriage_event(past_forecast)
    future_event = _marriage_event(future_forecast)
    past_window = _window(past_event)
    future_window = _window(future_event)
    past_score = _peak_score(past_event)
    future_score = _peak_score(future_event)

    if not past_window and not future_window:
        return {
            "available": False,
            "event": "marriage_timing_bidirectional",
            "model_version": "v1",
            "reason": "No qualifying historical or upcoming marriage-timing window was found.",
        }

    comparison = _comparison(past_score, future_score) if past_window and future_window else (
        "future_only" if future_window else "past_only"
    )
    future_label = _future_language(relationship_status)

    if past_window and future_window:
        answer = (
            "The chart shows a notable historical marriage-supportive period and also an upcoming "
            f"{future_label}. The two are provided together so the past window can act as context "
            "for the future forecast; a historical peak does not prove that a marriage occurred."
        )
    elif future_window:
        answer = f"The strongest qualifying result in the scan is an upcoming {future_label}."
    else:
        answer = (
            "A strong historical marriage-supportive period is present, but no qualifying upcoming "
            "window was found in the selected future horizon."
        )

    return {
        "available": True,
        "event": "marriage_timing_bidirectional",
        "model_version": "v1",
        "relationship_status": relationship_status,
        "reference_moment": reference_moment.isoformat(),
        "lookback_years": lookback_years,
        "lookahead_years": lookahead_years,
        "past": {
            "available": past_window is not None,
            "strongest_window": past_window,
            "strongest_score": past_score,
            "period_start": past_start.isoformat(),
            "period_end": past_end.isoformat(),
        },
        "future": {
            "available": future_window is not None,
            "strongest_window": future_window,
            "strongest_score": future_score,
            "period_start": future_start.isoformat(),
            "period_end": future_end.isoformat(),
            "interpretation": future_label,
        },
        "comparison": {
            "result": comparison,
            "score_delta_future_minus_past": round(future_score - past_score, 3),
        },
        "answer": answer,
        "limitation": (
            "Astrological timing windows are symbolic indicators, not guarantees of marriage or proof "
            "that a historical event occurred."
        ),
        "past_forecast": past_forecast,
        "future_forecast": future_forecast,
    }
