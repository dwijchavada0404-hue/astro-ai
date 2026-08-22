from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.siblings_communication_timing_v1 import analyze_siblings_communication_timing_v1


EVENT_SCORE_KEYS = {
    "sibling_peer_connection": "sibling_support_score",
    "communication_expression": "communication_support_score",
    "initiative_skill_building": "initiative_learning_support_score",
    "collaboration_exchange": "collaboration_support_score",
    "boundary_assertiveness": "boundary_support_score",
}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _activation(period: dict[str, Any] | None, event_key: str) -> dict[str, Any] | None:
    if not isinstance(period, dict):
        return None
    return {
        "event_key": event_key,
        "activation_score": _bounded(float(period.get(EVENT_SCORE_KEYS[event_key]) or 0.0)),
        "start": period.get("start"), "end": period.get("end"),
        "major_lord": period.get("major_lord"), "sub_lord": period.get("sub_lord"),
        "interpretation": {
            "sibling_peer_connection": "symbolic emphasis on sibling or sibling-like peer connection",
            "communication_expression": "symbolic emphasis on communication, writing, speaking or everyday exchange",
            "initiative_skill_building": "symbolic emphasis on initiative, courage, practice and skill development",
            "collaboration_exchange": "symbolic emphasis on cooperation, teamwork or reciprocal exchange",
            "boundary_assertiveness": "symbolic emphasis on assertiveness, boundaries or competitive friction",
        }[event_key],
    }


def analyze_siblings_communication_event_intelligence_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Translate sibling/communication timing into bounded event-theme activation, not factual events."""
    timing = analyze_siblings_communication_timing_v1(chart, reference_moment)
    if not timing.get("available"):
        return {"available": False, "event": "siblings_communication_events", "model_version": "v1", "reason": timing.get("reason") or "Siblings & Communication timing is unavailable.", "timing": timing}

    past_period = (timing.get("past") or {}).get("strongest_period")
    present_period = (timing.get("present") or {}).get("active_period")
    future_period = (timing.get("future") or {}).get("strongest_period")
    events: dict[str, dict[str, Any]] = {}
    future_ranked: list[dict[str, Any]] = []
    for event_key in EVENT_SCORE_KEYS:
        past, present, future = (_activation(p, event_key) for p in (past_period, present_period, future_period))
        events[event_key] = {
            "past": {"available": past is not None, "activation": past, "historical_status": "unconfirmed" if past else None},
            "present": {"available": present is not None, "activation": present},
            "future": {"available": future is not None, "activation": future},
        }
        if future:
            future_ranked.append(future)
    future_ranked.sort(key=lambda item: item["activation_score"], reverse=True)

    return {
        "available": True, "event": "siblings_communication_events", "model_version": "v1",
        "reference_moment": reference_moment.isoformat(), "events": events,
        "strongest_future_event": future_ranked[0] if future_ranked else None,
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Past activation is not evidence that a sibling interaction, conflict, reconciliation, communication milestone or collaboration event occurred. Known history overrides astrology."},
        "answer": "Event intelligence separates symbolic sibling/peer, communication, initiative/skill, collaboration and boundary activations without asserting specific interpersonal events.",
        "limitation": "Activation scores are not probabilities. They cannot determine whether a sibling exists, identify a person's intentions or loyalty, predict conflict/estrangement/reconciliation, or guarantee communication, learning or collaboration outcomes.",
        "timing": timing,
    }
