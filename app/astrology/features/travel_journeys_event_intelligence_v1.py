from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.travel_journeys_timing_v1 import analyze_travel_journeys_timing_v1


EVENT_SCORE_KEYS = {
    "short_journey_activity": "short_journey_support_score",
    "long_distance_travel": "long_distance_support_score",
    "international_exposure": "international_support_score",
    "work_study_travel": "work_study_travel_support_score",
    "recurring_mobility": "recurring_mobility_support_score",
    "travel_adaptability": "travel_adaptability_support_score",
}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _activation(period: dict[str, Any] | None, event_key: str) -> dict[str, Any] | None:
    if not isinstance(period, dict):
        return None
    return {
        "event_key": event_key,
        "activation_score": _bounded(float(period.get(EVENT_SCORE_KEYS[event_key]) or 0.0)),
        "start": period.get("start"),
        "end": period.get("end"),
        "major_lord": period.get("major_lord"),
        "sub_lord": period.get("sub_lord"),
        "interpretation": {
            "short_journey_activity": "symbolic emphasis on short-distance travel, local movement or brief journeys",
            "long_distance_travel": "symbolic emphasis on long-distance travel or materially extended journeys",
            "international_exposure": "symbolic emphasis on international or cross-cultural travel exposure",
            "work_study_travel": "symbolic emphasis on travel connected with work, study, training or professional activity",
            "recurring_mobility": "symbolic emphasis on repeated travel, commuting or recurring movement",
            "travel_adaptability": "symbolic emphasis on flexibility and adaptation to travel or changing environments",
        }[event_key],
    }


def analyze_travel_journeys_event_intelligence_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Translate Travel & Journeys timing into bounded event themes, never factual trips."""
    timing = analyze_travel_journeys_timing_v1(chart, reference_moment)
    if not timing.get("available"):
        return {
            "available": False,
            "event": "travel_journeys_events",
            "model_version": "v1",
            "reason": timing.get("reason") or "Travel & Journeys timing is unavailable.",
            "timing": timing,
        }

    past_period = (timing.get("past") or {}).get("strongest_period")
    present_period = (timing.get("present") or {}).get("active_period")
    future_period = (timing.get("future") or {}).get("strongest_period")

    events: dict[str, dict[str, Any]] = {}
    future_ranked: list[dict[str, Any]] = []
    for event_key in EVENT_SCORE_KEYS:
        past = _activation(past_period, event_key)
        present = _activation(present_period, event_key)
        future = _activation(future_period, event_key)
        events[event_key] = {
            "past": {
                "available": past is not None,
                "activation": past,
                "historical_status": "unconfirmed" if past else None,
            },
            "present": {"available": present is not None, "activation": present},
            "future": {"available": future is not None, "activation": future},
        }
        if future:
            future_ranked.append(future)

    future_ranked.sort(key=lambda item: item["activation_score"], reverse=True)

    return {
        "available": True,
        "event": "travel_journeys_events",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_future_event": future_ranked[0] if future_ranked else None,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Past travel activation is not evidence that a specific trip, foreign visit, work/study journey, relocation or settlement actually occurred. Known travel history overrides astrology.",
        },
        "answer": "Travel event intelligence separates symbolic short-distance, long-distance, international, work/study, recurring-mobility and adaptability activations without asserting that a specific trip will occur.",
        "limitation": "Activation scores are not probabilities. They cannot guarantee a trip, exact destination, date, visa or immigration outcome, relocation, permanent settlement, travel safety, accident, delay or disruption outcome.",
        "timing": timing,
    }
