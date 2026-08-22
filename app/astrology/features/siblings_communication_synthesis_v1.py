from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.siblings_communication_event_intelligence_v1 import analyze_siblings_communication_event_intelligence_v1
from app.astrology.features.siblings_communication_reasoning_v1 import analyze_siblings_communication_v1
from app.astrology.features.siblings_communication_timing_v1 import analyze_siblings_communication_timing_v1
from app.astrology.features.siblings_communication_trajectory_v1 import analyze_siblings_communication_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_siblings_communication_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Combine sibling/communication natal, timing, event and trajectory signals."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_siblings_communication_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "siblings_communication_synthesis", "model_version": "v1", "reason": "Siblings & Communication natal foundation is unavailable."}
    timing = analyze_siblings_communication_timing_v1(chart, reference_moment)
    events = analyze_siblings_communication_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_siblings_communication_trajectory_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))
    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    sibling_score = _bounded(0.46 * _safe_float(themes.get("sibling_bond")) + 0.18 * _safe_float(future.get("sibling_support_score")) + 0.22 * _safe_float(trajectory.get("relationship_continuity_score")) + 0.14 * _safe_float(themes.get("collaboration")))
    communication_score = _bounded(0.46 * _safe_float(themes.get("communication_expression")) + 0.18 * _safe_float(future.get("communication_support_score")) + 0.22 * _safe_float(trajectory.get("communication_development_score")) + 0.14 * _safe_float(themes.get("learning_skills")))
    initiative_learning_score = _bounded(0.28 * _safe_float(themes.get("initiative_courage")) + 0.26 * _safe_float(themes.get("learning_skills")) + 0.18 * _safe_float(future.get("initiative_learning_support_score")) + 0.28 * _safe_float(trajectory.get("initiative_skill_growth_score")))
    collaboration_score = _bounded(0.48 * _safe_float(themes.get("collaboration")) + 0.18 * _safe_float(future.get("collaboration_support_score")) + 0.24 * _safe_float(trajectory.get("collaboration_score")) + 0.10 * _safe_float(themes.get("communication_expression")))
    boundary_score = _bounded(0.52 * _safe_float(themes.get("boundaries_competition")) + 0.18 * _safe_float(future.get("boundary_support_score")) + 0.30 * _safe_float(trajectory.get("assertiveness_boundary_score")))
    adaptability_score = _bounded(0.34 * communication_score + 0.22 * initiative_learning_score + 0.18 * collaboration_score + 0.12 * sibling_score + 0.14 * _safe_float(trajectory.get("adaptability_score")))

    scores = {"sibling_peer_connection": sibling_score, "communication": communication_score, "initiative_learning": initiative_learning_score, "collaboration": collaboration_score, "boundaries_assertiveness": boundary_score, "adaptability": adaptability_score}
    strongest = max(scores.items(), key=lambda item: item[1])
    if communication_score >= 0.66 and initiative_learning_score >= 0.60:
        outlook = "communication_and_skill_growth_emphasis"
    elif sibling_score >= 0.66 and collaboration_score >= 0.58:
        outlook = "sibling_peer_and_collaboration_emphasis"
    elif boundary_score >= 0.66:
        outlook = "assertiveness_and_boundary_emphasis"
    else:
        outlook = "balanced_sibling_communication_development"

    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _bounded(0.40 + 0.30 * coverage + 0.18 * strongest[1] + 0.12 * adaptability_score)
    return {
        "available": True, "event": "siblings_communication_synthesis", "model_version": "v1", "reference_moment": reference_moment.isoformat(),
        "outlook": outlook, "confidence": confidence, "component_coverage": round(coverage, 3), "scores": scores,
        "strongest_area": strongest[0], "strongest_area_score": strongest[1],
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None, "strongest_future_period": future or None,
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known sibling/peer relationships, communication history and lived events override predictive assumptions. Historical astrology may interpret confirmed periods but must never manufacture siblings, conflict, estrangement, reconciliation or communication milestones."},
        "answer": f"The combined Siblings & Communication outlook is {outlook.replace('_', ' ')}. It describes symbolic tendencies rather than facts about specific people.",
        "limitation": "This synthesis cannot determine whether a sibling exists, identify a specific person's personality, intentions or loyalty, predict conflict/estrangement/reconciliation, or guarantee communication, courage, learning or collaboration outcomes.",
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
