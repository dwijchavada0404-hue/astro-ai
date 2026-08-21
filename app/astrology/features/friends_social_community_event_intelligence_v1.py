from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.friends_social_community_timing_v1 import analyze_friends_social_community_timing_v1


EVENT_SCORE_KEYS = {
    "friendship_connection": "friendship_support_score",
    "network_collaboration": "networking_support_score",
    "community_participation": "community_support_score",
    "social_boundary_reset": "boundary_support_score",
}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _period_event(period: dict[str, Any] | None, event_key: str) -> dict[str, Any] | None:
    if not isinstance(period, dict):
        return None
    score_key = EVENT_SCORE_KEYS[event_key]
    score = _bounded(float(period.get(score_key) or 0.0))
    return {
        "event_key": event_key,
        "activation_score": score,
        "start": period.get("start"),
        "end": period.get("end"),
        "major_lord": period.get("major_lord"),
        "sub_lord": period.get("sub_lord"),
        "interpretation": {
            "friendship_connection": "symbolic support for friendship, peer connection or reciprocal social engagement",
            "network_collaboration": "symbolic support for networking, collaboration or useful peer exchange",
            "community_participation": "symbolic support for group participation, community belonging or shared activity",
            "social_boundary_reset": "symbolic emphasis on selectivity, boundaries or restructuring social commitments",
        }[event_key],
    }


def analyze_friends_social_community_event_intelligence_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Translate social timing into bounded event-theme activations, never factual social events."""
    timing = analyze_friends_social_community_timing_v1(chart, reference_moment)
    if not timing.get("available"):
        return {"available": False, "event": "friends_social_community_events", "model_version": "v1", "reason": timing.get("reason") or "Social timing is unavailable.", "timing": timing}

    past_period = (timing.get("past") or {}).get("strongest_period")
    present_period = (timing.get("present") or {}).get("active_period")
    future_period = (timing.get("future") or {}).get("strongest_period")
    events: dict[str, dict[str, Any]] = {}
    future_ranked: list[dict[str, Any]] = []
    for event_key in EVENT_SCORE_KEYS:
        past = _period_event(past_period, event_key)
        present = _period_event(present_period, event_key)
        future = _period_event(future_period, event_key)
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
        "event": "friends_social_community_events",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_future_event": future_ranked[0] if future_ranked else None,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Past social activation is not evidence that a friendship began or ended, betrayal occurred, a network opportunity happened, or community membership changed. Known social history overrides astrology.",
        },
        "answer": "Social event intelligence separates symbolic friendship, networking, community and boundary activations without asserting that specific interpersonal events will occur.",
        "limitation": "Activation scores are not probabilities. They cannot identify a future friend or enemy, judge a person's loyalty or trustworthiness, predict betrayal or conflict, guarantee popularity or networking success, or prove that a friendship/community event occurred.",
        "timing": timing,
    }
