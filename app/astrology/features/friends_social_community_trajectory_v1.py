from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.friends_social_community_event_intelligence_v1 import analyze_friends_social_community_event_intelligence_v1
from app.astrology.features.friends_social_community_reasoning_v1 import analyze_friends_social_community_v1
from app.astrology.features.friends_social_community_timing_v1 import analyze_friends_social_community_timing_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_friends_social_community_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize long-term social patterns without predicting specific people or inevitable social outcomes."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_friends_social_community_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "friends_social_community_trajectory", "model_version": "v1", "reason": "Social natal foundation is unavailable."}

    timing = analyze_friends_social_community_timing_v1(chart, reference_moment)
    events = analyze_friends_social_community_event_intelligence_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))

    close_friendship = _safe_float(themes.get("close_friendship"))
    social_breadth = _safe_float(themes.get("social_breadth"))
    community = _safe_float(themes.get("community_belonging"))
    networking = _safe_float(themes.get("networking_collaboration"))
    communication = _safe_float(themes.get("communication_connection"))
    boundaries = _safe_float(themes.get("selective_boundaries"))

    present = _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    present_friendship = _safe_float(present.get("friendship_support_score"))
    future_friendship = _safe_float(future.get("friendship_support_score"))
    future_networking = _safe_float(future.get("networking_support_score"))
    future_community = _safe_float(future.get("community_support_score"))
    future_boundaries = _safe_float(future.get("boundary_support_score"))

    friendship_depth_score = _bounded(0.54 * close_friendship + 0.18 * communication + 0.16 * future_friendship + 0.12 * (1.0 - boundaries))
    social_breadth_score = _bounded(0.54 * social_breadth + 0.18 * networking + 0.16 * future_networking + 0.12 * community)
    community_orientation_score = _bounded(0.52 * community + 0.18 * social_breadth + 0.18 * future_community + 0.12 * communication)
    collaboration_score = _bounded(0.48 * networking + 0.20 * communication + 0.18 * future_networking + 0.14 * community)
    selectivity_boundary_score = _bounded(0.62 * boundaries + 0.18 * future_boundaries + 0.12 * (1.0 - social_breadth) + 0.08 * close_friendship)
    social_adaptability_score = _bounded(0.26 * communication + 0.22 * networking + 0.18 * community + 0.16 * close_friendship + 0.10 * future_friendship + 0.08 * (1.0 - boundaries))

    if friendship_depth_score >= 0.66 and selectivity_boundary_score >= 0.56:
        trajectory_pattern = "selective_but_deep_social_bonds"
    elif social_breadth_score >= 0.66 and collaboration_score >= 0.58:
        trajectory_pattern = "expansive_network_and_collaboration"
    elif community_orientation_score >= 0.66:
        trajectory_pattern = "community_centered_social_development"
    elif selectivity_boundary_score >= 0.66 and social_breadth_score < 0.56:
        trajectory_pattern = "selective_social_structure"
    else:
        trajectory_pattern = "mixed_social_development"

    if future_friendship > present_friendship + 0.08:
        near_term_direction = "friendship_support_strengthening"
    elif future_networking >= 0.60:
        near_term_direction = "networking_and_collaboration_emphasis"
    elif future_community >= 0.60:
        near_term_direction = "community_participation_emphasis"
    elif future_boundaries >= 0.60:
        near_term_direction = "social_boundaries_and_selectivity_emphasis"
    else:
        near_term_direction = "broadly_steady_social_pattern"

    return {
        "available": True,
        "event": "friends_social_community_trajectory",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "friendship_depth_score": friendship_depth_score,
        "social_breadth_score": social_breadth_score,
        "community_orientation_score": community_orientation_score,
        "collaboration_score": collaboration_score,
        "selectivity_boundary_score": selectivity_boundary_score,
        "social_adaptability_score": social_adaptability_score,
        "trajectory_pattern": trajectory_pattern,
        "near_term_direction": near_term_direction,
        "timing_available": bool(timing.get("available")),
        "events_available": bool(events.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known friendships, social history, community ties and interpersonal experiences override symbolic trajectory assumptions. Astrology must not manufacture specific friendships, betrayals, conflicts, exclusions or network events.",
        },
        "answer": f"The longer-term social trajectory is {trajectory_pattern.replace('_', ' ')}, with a near-term direction of {near_term_direction.replace('_', ' ')}.",
        "limitation": "This trajectory does not determine who will become a friend, whether someone is loyal or trustworthy, whether betrayal/conflict will occur, or whether the user will be popular, isolated, accepted or rejected by a group.",
        "components": {"natal": natal, "timing": timing, "events": events},
    }
