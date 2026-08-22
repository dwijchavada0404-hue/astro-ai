from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.travel_journeys_reasoning_v1 import analyze_travel_journeys_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _score_period(period: dict[str, Any], natal: dict[str, Any]) -> dict[str, Any]:
    themes = _safe_dict(natal.get("theme_scores"))
    lords = {str(period.get("major_lord") or ""), str(period.get("sub_lord") or "")}

    short_score = _bounded(
        0.46 * float(themes.get("short_journeys") or 0.0)
        + 0.18 * bool(lords & {"Mercury", "Moon"})
        + 0.10 * bool(lords & {"Mars"})
    )
    long_score = _bounded(
        0.46 * float(themes.get("long_distance_travel") or 0.0)
        + 0.20 * bool(lords & {"Jupiter", "Rahu"})
        + 0.08 * bool(lords & {"Moon"})
    )
    international_score = _bounded(
        0.46 * float(themes.get("international_exposure") or 0.0)
        + 0.22 * bool(lords & {"Rahu", "Jupiter"})
        + 0.08 * bool(lords & {"Mercury"})
    )
    work_study_score = _bounded(
        0.46 * float(themes.get("work_study_travel") or 0.0)
        + 0.18 * bool(lords & {"Mercury", "Jupiter"})
        + 0.10 * bool(lords & {"Saturn", "Sun"})
    )
    mobility_score = _bounded(
        0.46 * float(themes.get("recurring_mobility") or 0.0)
        + 0.18 * bool(lords & {"Moon", "Mercury", "Rahu"})
        + 0.08 * bool(lords & {"Mars"})
    )
    adaptability_score = _bounded(
        0.48 * float(themes.get("travel_adaptability") or 0.0)
        + 0.16 * bool(lords & {"Mercury", "Moon", "Jupiter"})
        + 0.08 * bool(lords & {"Rahu"})
    )

    return {
        **period,
        "short_journey_support_score": short_score,
        "long_distance_support_score": long_score,
        "international_support_score": international_score,
        "work_study_travel_support_score": work_study_score,
        "recurring_mobility_support_score": mobility_score,
        "travel_adaptability_support_score": adaptability_score,
        "overall_activation_score": _bounded(
            (short_score + long_score + international_score + work_study_score + mobility_score + adaptability_score) / 6.0
        ),
    }


def analyze_travel_journeys_timing_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Evaluate past/present/future travel activation without asserting trips or relocation."""
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_travel_journeys_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "travel_journeys_timing",
            "model_version": "v1",
            "reason": "Travel & Journeys natal foundation is unavailable.",
        }

    raw_periods = chart.get("dasha_periods")
    if not isinstance(raw_periods, list) or not raw_periods:
        return {
            "available": False,
            "event": "travel_journeys_timing",
            "model_version": "v1",
            "reason": "Dasha periods are required for Travel & Journeys timing intelligence.",
            "natal": natal,
        }

    scored: list[dict[str, Any]] = []
    for item in raw_periods:
        if not isinstance(item, dict):
            continue
        start = _parse_dt(item.get("start"))
        end = _parse_dt(item.get("end"))
        if start is None or end is None or start.tzinfo is None or end.tzinfo is None:
            continue
        scored.append(_score_period({**item, "start": start.isoformat(), "end": end.isoformat()}, natal))

    past = [p for p in scored if _parse_dt(p["end"]) <= reference_moment]
    present = [p for p in scored if _parse_dt(p["start"]) <= reference_moment < _parse_dt(p["end"])]
    future = [p for p in scored if _parse_dt(p["start"]) > reference_moment]

    def strongest(periods: list[dict[str, Any]]) -> dict[str, Any] | None:
        return max(periods, key=lambda p: p["overall_activation_score"]) if periods else None

    return {
        "available": True,
        "event": "travel_journeys_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"strongest_period": strongest(past), "historical_status": "unconfirmed"},
        "present": {"active_period": strongest(present)},
        "future": {"strongest_period": strongest(future)},
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Past travel activation is not evidence that a trip, foreign visit, work/study journey or relocation occurred. Known travel history overrides astrology.",
        },
        "limitation": "Timing scores are symbolic activation, not probabilities. They cannot guarantee a trip, destination, visa, immigration outcome, relocation, settlement, or travel safety/accident outcome.",
        "natal": natal,
    }
