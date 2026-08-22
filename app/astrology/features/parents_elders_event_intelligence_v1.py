from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.parents_elders_timing_v1 import analyze_parents_elders_timing_v1


EVENT_SCORE_KEYS = {
    "guidance_mentorship": "guidance_support_score",
    "emotional_support": "emotional_support_score",
    "duty_responsibility": "duty_support_score",
    "authority_structure": "authority_support_score",
    "independence_boundaries": "boundary_support_score",
    "family_continuity": "continuity_support_score",
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
            "guidance_mentorship": "symbolic emphasis on guidance, mentorship or learning from senior figures",
            "emotional_support": "symbolic emphasis on emotional support, belonging or family reassurance",
            "duty_responsibility": "symbolic emphasis on family duty, responsibility or dependable contribution",
            "authority_structure": "symbolic emphasis on authority, structure, expectations or senior guidance",
            "independence_boundaries": "symbolic emphasis on autonomy, boundaries or role renegotiation",
            "family_continuity": "symbolic emphasis on continuity, tradition or intergenerational connection",
        }[event_key],
    }


def analyze_parents_elders_event_intelligence_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Translate Parents & Elders timing into symbolic event-theme activation, never factual events."""
    timing = analyze_parents_elders_timing_v1(chart, reference_moment)
    if not timing.get("available"):
        return {"available": False, "event": "parents_elders_events", "model_version": "v1", "reason": timing.get("reason") or "Parents & Elders timing is unavailable.", "timing": timing}

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
            "past": {"available": past is not None, "activation": past, "historical_status": "unconfirmed" if past else None},
            "present": {"available": present is not None, "activation": present},
            "future": {"available": future is not None, "activation": future},
        }
        if future:
            future_ranked.append(future)

    future_ranked.sort(key=lambda item: item["activation_score"], reverse=True)

    return {
        "available": True,
        "event": "parents_elders_events",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_future_event": future_ranked[0] if future_ranked else None,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Past family-role activation is not evidence that support, conflict, caregiving, illness, loss, reconciliation or another specific event occurred. Known family history overrides astrology.",
        },
        "answer": "Parents & Elders event intelligence separates symbolic guidance, support, duty, authority, boundary and continuity activations without asserting that a specific family event will occur.",
        "limitation": "Activation scores are not probabilities. They cannot diagnose or forecast a parent or elder's health, predict illness, lifespan or death, identify intentions or character, or guarantee conflict, reconciliation, caregiving or support outcomes.",
        "timing": timing,
    }
