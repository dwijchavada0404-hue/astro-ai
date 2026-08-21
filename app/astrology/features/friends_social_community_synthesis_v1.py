from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.friends_social_community_event_intelligence_v1 import analyze_friends_social_community_event_intelligence_v1
from app.astrology.features.friends_social_community_reasoning_v1 import analyze_friends_social_community_v1
from app.astrology.features.friends_social_community_timing_v1 import analyze_friends_social_community_timing_v1
from app.astrology.features.friends_social_community_trajectory_v1 import analyze_friends_social_community_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_friends_social_community_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Combine social natal, timing, event and trajectory signals into a guarded synthesis."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_friends_social_community_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "friends_social_community_synthesis", "model_version": "v1", "reason": "Social natal foundation is unavailable."}

    timing = analyze_friends_social_community_timing_v1(chart, reference_moment)
    events = analyze_friends_social_community_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_friends_social_community_trajectory_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))
    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    close_friendship = _safe_float(themes.get("close_friendship"))
    social_breadth = _safe_float(themes.get("social_breadth"))
    community = _safe_float(themes.get("community_belonging"))
    networking = _safe_float(themes.get("networking_collaboration"))
    communication = _safe_float(themes.get("communication_connection"))
    boundaries = _safe_float(themes.get("selective_boundaries"))

    friendship_score = _bounded(0.44 * close_friendship + 0.18 * communication + 0.18 * _safe_float(future.get("friendship_support_score")) + 0.20 * _safe_float(trajectory.get("friendship_depth_score")))
    network_score = _bounded(0.38 * networking + 0.20 * social_breadth + 0.18 * _safe_float(future.get("networking_support_score")) + 0.24 * _safe_float(trajectory.get("collaboration_score")))
    community_score = _bounded(0.44 * community + 0.18 * social_breadth + 0.18 * _safe_float(future.get("community_support_score")) + 0.20 * _safe_float(trajectory.get("community_orientation_score")))
    boundary_score = _bounded(0.52 * boundaries + 0.20 * _safe_float(future.get("boundary_support_score")) + 0.28 * _safe_float(trajectory.get("selectivity_boundary_score")))
    adaptability_score = _bounded(0.34 * communication + 0.20 * networking + 0.18 * community + 0.28 * _safe_float(trajectory.get("social_adaptability_score")))

    scores = {"friendship": friendship_score, "networking": network_score, "community": community_score, "boundaries": boundary_score, "adaptability": adaptability_score}
    strongest = max(scores.items(), key=lambda item: item[1])
    if friendship_score >= 0.66 and boundary_score >= 0.58:
        outlook = "selective_and_deep_social_connections"
    elif network_score >= 0.66 and adaptability_score >= 0.58:
        outlook = "network_and_collaboration_emphasis"
    elif community_score >= 0.66:
        outlook = "community_belonging_emphasis"
    elif boundary_score >= 0.66:
        outlook = "social_selectivity_and_boundary_emphasis"
    else:
        outlook = "balanced_social_development"

    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _bounded(0.40 + 0.30 * coverage + 0.18 * strongest[1] + 0.12 * adaptability_score)

    return {
        "available": True,
        "event": "friends_social_community_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "outlook": outlook,
        "confidence": confidence,
        "component_coverage": round(coverage, 3),
        "scores": scores,
        "strongest_area": strongest[0],
        "strongest_area_score": strongest[1],
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None,
        "strongest_future_period": future or None,
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known friendships, social history and community ties override predictive assumptions. Historical astrology may interpret confirmed periods but must never manufacture a friendship, betrayal, conflict, exclusion or networking event."},
        "answer": f"The combined Friends, Social Networks & Community outlook is {outlook.replace('_', ' ')}. It describes social themes, not facts about specific people.",
        "limitation": "This synthesis cannot identify future friends or enemies, determine loyalty or trustworthiness, predict betrayal/conflict, guarantee popularity, acceptance, networking success or community belonging, or prove that a social event occurred.",
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
