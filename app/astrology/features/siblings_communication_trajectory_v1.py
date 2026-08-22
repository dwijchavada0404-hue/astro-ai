from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.siblings_communication_event_intelligence_v1 import analyze_siblings_communication_event_intelligence_v1
from app.astrology.features.siblings_communication_reasoning_v1 import analyze_siblings_communication_v1
from app.astrology.features.siblings_communication_timing_v1 import analyze_siblings_communication_timing_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_siblings_communication_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize longer-term sibling/peer, communication and initiative patterns."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_siblings_communication_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "siblings_communication_trajectory", "model_version": "v1", "reason": "Siblings & Communication natal foundation is unavailable."}
    timing = analyze_siblings_communication_timing_v1(chart, reference_moment)
    events = analyze_siblings_communication_event_intelligence_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))
    present = _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    sibling = _safe_float(themes.get("sibling_bond")); communication = _safe_float(themes.get("communication_expression"))
    initiative = _safe_float(themes.get("initiative_courage")); learning = _safe_float(themes.get("learning_skills"))
    collaboration = _safe_float(themes.get("collaboration")); boundaries = _safe_float(themes.get("boundaries_competition"))

    relationship_continuity_score = _bounded(0.58 * sibling + 0.18 * collaboration + 0.14 * _safe_float(future.get("sibling_support_score")) + 0.10 * communication)
    communication_development_score = _bounded(0.54 * communication + 0.18 * learning + 0.18 * _safe_float(future.get("communication_support_score")) + 0.10 * initiative)
    initiative_skill_growth_score = _bounded(0.42 * initiative + 0.30 * learning + 0.18 * _safe_float(future.get("initiative_learning_support_score")) + 0.10 * communication)
    collaboration_score = _bounded(0.54 * collaboration + 0.18 * sibling + 0.18 * _safe_float(future.get("collaboration_support_score")) + 0.10 * communication)
    assertiveness_boundary_score = _bounded(0.62 * boundaries + 0.20 * _safe_float(future.get("boundary_support_score")) + 0.10 * initiative + 0.08 * (1.0 - sibling))
    adaptability_score = _bounded(0.28 * communication + 0.22 * learning + 0.18 * collaboration + 0.16 * initiative + 0.10 * sibling + 0.06 * (1.0 - boundaries))

    if communication_development_score >= 0.66 and initiative_skill_growth_score >= 0.60:
        pattern = "communication_and_skill_development"
    elif relationship_continuity_score >= 0.66 and collaboration_score >= 0.58:
        pattern = "relationship_and_collaboration_emphasis"
    elif assertiveness_boundary_score >= 0.66:
        pattern = "assertiveness_and_boundary_emphasis"
    else:
        pattern = "mixed_sibling_communication_development"

    present_comm = _safe_float(present.get("communication_support_score")); future_comm = _safe_float(future.get("communication_support_score"))
    if future_comm > present_comm + 0.08:
        direction = "communication_support_strengthening"
    elif _safe_float(future.get("initiative_learning_support_score")) >= 0.60:
        direction = "initiative_and_skill_emphasis"
    elif _safe_float(future.get("collaboration_support_score")) >= 0.60:
        direction = "collaboration_emphasis"
    elif _safe_float(future.get("boundary_support_score")) >= 0.60:
        direction = "assertiveness_and_boundaries_emphasis"
    else:
        direction = "broadly_steady_pattern"

    return {
        "available": True, "event": "siblings_communication_trajectory", "model_version": "v1", "reference_moment": reference_moment.isoformat(),
        "relationship_continuity_score": relationship_continuity_score, "communication_development_score": communication_development_score,
        "initiative_skill_growth_score": initiative_skill_growth_score, "collaboration_score": collaboration_score,
        "assertiveness_boundary_score": assertiveness_boundary_score, "adaptability_score": adaptability_score,
        "trajectory_pattern": pattern, "near_term_direction": direction,
        "timing_available": bool(timing.get("available")), "events_available": bool(events.get("available")),
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known sibling/peer relationships and communication history override symbolic trajectory assumptions. Astrology must not manufacture siblings, estrangement, reconciliation, conflict or communication events."},
        "answer": f"The longer-term Siblings & Communication trajectory is {pattern.replace('_', ' ')}, with a near-term direction of {direction.replace('_', ' ')}.",
        "limitation": "This trajectory cannot determine whether a sibling exists, identify a specific person's intentions or loyalty, predict estrangement/conflict/reconciliation, or guarantee communication, learning, courage or collaboration outcomes.",
        "components": {"natal": natal, "timing": timing, "events": events},
    }
