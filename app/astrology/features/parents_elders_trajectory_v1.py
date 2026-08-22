from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.parents_elders_event_intelligence_v1 import analyze_parents_elders_event_intelligence_v1
from app.astrology.features.parents_elders_reasoning_v1 import analyze_parents_elders_v1
from app.astrology.features.parents_elders_timing_v1 import analyze_parents_elders_timing_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_parents_elders_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize longer-term family-role patterns without predicting another person's fate."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")
    natal = analyze_parents_elders_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "parents_elders_trajectory", "model_version": "v1", "reason": "Parents & Elders natal foundation is unavailable."}
    timing = analyze_parents_elders_timing_v1(chart, reference_moment)
    events = analyze_parents_elders_event_intelligence_v1(chart, reference_moment)
    t = _d(natal.get("theme_scores"))
    present = _d(_d(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    support = _b(.46*_f(t.get("emotional_support")) + .20*_f(t.get("family_continuity")) + .18*_f(future.get("emotional_support_score")) + .16*_f(future.get("continuity_support_score")))
    guidance = _b(.52*_f(t.get("guidance_mentorship")) + .20*_f(t.get("authority_structure")) + .18*_f(future.get("guidance_support_score")) + .10*_f(t.get("family_continuity")))
    responsibility = _b(.52*_f(t.get("duty_responsibility")) + .20*_f(t.get("authority_structure")) + .18*_f(future.get("duty_support_score")) + .10*_f(t.get("independence_boundaries")))
    boundaries = _b(.56*_f(t.get("independence_boundaries")) + .22*_f(future.get("boundary_support_score")) + .12*_f(t.get("duty_responsibility")) + .10*(1.0-_f(t.get("emotional_support"))))
    continuity = _b(.54*_f(t.get("family_continuity")) + .20*_f(t.get("emotional_support")) + .18*_f(future.get("continuity_support_score")) + .08*_f(t.get("guidance_mentorship")))
    adaptability = _b(.24*support + .20*guidance + .20*responsibility + .16*boundaries + .20*continuity)

    if guidance >= .66 and responsibility >= .60:
        pattern = "guidance_and_responsibility_emphasis"
    elif support >= .66 and continuity >= .60:
        pattern = "support_and_family_continuity_emphasis"
    elif boundaries >= .66:
        pattern = "independence_and_boundary_emphasis"
    else:
        pattern = "balanced_family_role_development"

    present_overall, future_overall = _f(present.get("overall_activation_score")), _f(future.get("overall_activation_score"))
    if future_overall > present_overall + .08:
        direction = "family_role_activation_strengthening"
    elif _f(future.get("duty_support_score")) >= .60:
        direction = "responsibility_emphasis"
    elif _f(future.get("boundary_support_score")) >= .60:
        direction = "independence_and_boundaries_emphasis"
    else:
        direction = "broadly_steady_family_role_pattern"

    return {"available": True, "event": "parents_elders_trajectory", "model_version": "v1", "reference_moment": reference_moment.isoformat(), "support_continuity_score": support, "guidance_development_score": guidance, "responsibility_score": responsibility, "independence_boundary_score": boundaries, "family_continuity_score": continuity, "adaptability_score": adaptability, "trajectory_pattern": pattern, "near_term_direction": direction, "timing_available": bool(timing.get("available")), "events_available": bool(events.get("available")), "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known parent/elder relationships and family history override symbolic trajectory assumptions. Astrology must not manufacture illness, loss, conflict, reconciliation, caregiving or other family events."}, "answer": f"The longer-term Parents & Elders trajectory is {pattern.replace('_', ' ')}, with a near-term direction of {direction.replace('_', ' ')}.", "limitation": "This trajectory cannot predict another person's health, illness, lifespan, death, intentions or character, and cannot guarantee conflict, reconciliation, caregiving or family outcomes.", "components": {"natal": natal, "timing": timing, "events": events}}
