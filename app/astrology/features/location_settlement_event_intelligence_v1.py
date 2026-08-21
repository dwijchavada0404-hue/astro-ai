from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.location_settlement_reasoning_v1 import analyze_location_settlement_v1
from app.astrology.features.location_settlement_timing_v1 import analyze_location_settlement_timing_v1


EVENT_LABELS = {
    "domestic_relocation": "residential relocation or meaningful change of home base",
    "foreign_travel_exposure": "foreign travel, international work/study or cross-cultural exposure",
    "long_distance_residence": "extended residence materially away from the place of origin",
    "foreign_settlement": "establishing a longer-term base outside the place of origin",
    "return_or_re_rooting": "return, re-rooting or renewed stability in a primary home base",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _outlook(score: float) -> str:
    if score >= 0.75:
        return "strongly_active"
    if score >= 0.50:
        return "active"
    if score >= 0.25:
        return "mildly_active"
    return "weak_signal"


def _natal_scores(natal: dict[str, Any]) -> dict[str, float]:
    themes = _safe_dict(natal.get("theme_scores"))
    rooted = _safe_float(themes.get("rooted_home_base"))
    relocation = _safe_float(themes.get("domestic_relocation"))
    exposure = _safe_float(themes.get("foreign_exposure"))
    residence = _safe_float(themes.get("long_distance_residence"))
    settlement = _safe_float(themes.get("foreign_settlement"))
    return {
        "domestic_relocation": _bounded(0.72 * relocation + 0.18 * residence + 0.10 * exposure),
        "foreign_travel_exposure": _bounded(0.66 * exposure + 0.18 * relocation + 0.16 * residence),
        "long_distance_residence": _bounded(0.58 * residence + 0.22 * exposure + 0.20 * settlement),
        # Settlement is intentionally the strictest event: residence + settlement evidence dominate.
        "foreign_settlement": _bounded(0.54 * settlement + 0.28 * residence + 0.12 * exposure + 0.06 * relocation),
        "return_or_re_rooting": _bounded(0.70 * rooted + 0.18 * (1.0 - relocation) + 0.12 * (1.0 - settlement)),
    }


def _timing_score(event: str, period: dict[str, Any]) -> float:
    relocation = _safe_float(period.get("relocation_activation_score"))
    exposure = _safe_float(period.get("foreign_exposure_score"))
    settlement = _safe_float(period.get("foreign_settlement_support_score"))
    if event == "domestic_relocation":
        return relocation
    if event == "foreign_travel_exposure":
        return exposure
    if event == "long_distance_residence":
        return 0.52 * exposure + 0.48 * settlement
    if event == "foreign_settlement":
        return 0.72 * settlement + 0.28 * exposure
    return 1.0 - max(relocation, settlement)


def analyze_location_settlement_event_intelligence_v1(
    chart: dict[str, Any], reference_moment: datetime
) -> dict[str, Any]:
    """Rank symbolic location events without turning activation into migration facts."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_location_settlement_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "location_settlement_event_intelligence", "model_version": "v1", "reason": "Location natal foundation is unavailable."}

    timing = analyze_location_settlement_timing_v1(chart, reference_moment)
    natal_scores = _natal_scores(natal)
    periods = {
        "past": _safe_dict(_safe_dict(timing.get("past")).get("strongest_period")) if timing.get("available") else {},
        "present": _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {},
        "future": _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {},
    }

    events: dict[str, Any] = {}
    for name, natal_score in natal_scores.items():
        windows: dict[str, Any] = {}
        for bucket, period in periods.items():
            score = _bounded(0.60 * natal_score + 0.40 * _timing_score(name, period)) if period else natal_score
            windows[bucket] = {
                "score": score,
                "outlook": _outlook(score),
                "timing_period": period or None,
                "historical_status": "unconfirmed" if bucket == "past" else None,
            }
        events[name] = {"label": EVENT_LABELS[name], "natal_strength": natal_score, **windows}

    ranked_future = sorted(
        ((name, _safe_float(_safe_dict(data.get("future")).get("score"))) for name, data in events.items()),
        key=lambda item: item[1], reverse=True,
    )
    return {
        "available": True,
        "event": "location_settlement_event_intelligence",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_future_event": ranked_future[0][0] if ranked_future else None,
        "strongest_future_event_score": ranked_future[0][1] if ranked_future else 0.0,
        "timing_available": bool(timing.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Past location-event windows are symbolic only. AstroAI must not state that travel, relocation, migration, settlement or return occurred unless the user confirms it. Known facts override astrology.",
        },
        "answer": "Location events are ranked from natal patterns and available dasha timing; scores describe activation, not event probability.",
        "limitation": (
            "This layer does not predict or guarantee travel, relocation, foreign employment or study, visa approval, immigration status, "
            "permanent residence, citizenship, return migration or settlement in a particular country or city."
        ),
    }
