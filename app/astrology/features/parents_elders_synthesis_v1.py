from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.parents_elders_event_intelligence_v1 import analyze_parents_elders_event_intelligence_v1
from app.astrology.features.parents_elders_reasoning_v1 import analyze_parents_elders_v1
from app.astrology.features.parents_elders_timing_v1 import analyze_parents_elders_timing_v1
from app.astrology.features.parents_elders_trajectory_v1 import analyze_parents_elders_trajectory_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_parents_elders_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Combine Parents & Elders natal, timing, event and trajectory signals."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")
    natal = analyze_parents_elders_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "parents_elders_synthesis", "model_version": "v1", "reason": "Parents & Elders natal foundation is unavailable."}
    timing = analyze_parents_elders_timing_v1(chart, reference_moment)
    events = analyze_parents_elders_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_parents_elders_trajectory_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    emotional = _b(.46*_f(themes.get("emotional_support")) + .18*_f(future.get("emotional_support_score")) + .24*_f(trajectory.get("support_continuity_score")) + .12*_f(themes.get("family_continuity")))
    guidance = _b(.48*_f(themes.get("guidance_mentorship")) + .18*_f(future.get("guidance_support_score")) + .24*_f(trajectory.get("guidance_development_score")) + .10*_f(themes.get("authority_structure")))
    responsibility = _b(.48*_f(themes.get("duty_responsibility")) + .18*_f(future.get("duty_support_score")) + .24*_f(trajectory.get("responsibility_score")) + .10*_f(themes.get("authority_structure")))
    boundaries = _b(.50*_f(themes.get("independence_boundaries")) + .18*_f(future.get("boundary_support_score")) + .26*_f(trajectory.get("independence_boundary_score")) + .06*_f(themes.get("duty_responsibility")))
    continuity = _b(.50*_f(themes.get("family_continuity")) + .18*_f(future.get("continuity_support_score")) + .24*_f(trajectory.get("family_continuity_score")) + .08*_f(themes.get("emotional_support")))
    adaptability = _b(.22*emotional + .20*guidance + .20*responsibility + .16*boundaries + .14*continuity + .08*_f(trajectory.get("adaptability_score")))
    scores = {"emotional_support": emotional, "guidance_mentorship": guidance, "duty_responsibility": responsibility, "independence_boundaries": boundaries, "family_continuity": continuity, "adaptability": adaptability}
    strongest = max(scores.items(), key=lambda item: item[1])
    if guidance >= .66 and responsibility >= .60:
        outlook = "guidance_and_responsibility_emphasis"
    elif emotional >= .66 and continuity >= .60:
        outlook = "support_and_family_continuity_emphasis"
    elif boundaries >= .66:
        outlook = "independence_and_boundary_emphasis"
    else:
        outlook = "balanced_parents_elders_development"
    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _b(.40 + .30*coverage + .18*strongest[1] + .12*adaptability)
    return {"available": True, "event": "parents_elders_synthesis", "model_version": "v1", "reference_moment": reference_moment.isoformat(), "outlook": outlook, "confidence": confidence, "component_coverage": round(coverage, 3), "scores": scores, "strongest_area": strongest[0], "strongest_area_score": strongest[1], "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None, "strongest_future_period": future or None, "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known parent/elder relationships and family history override predictive assumptions. Historical astrology may interpret confirmed periods but must never manufacture illness, loss, conflict, reconciliation, caregiving or other family events."}, "answer": f"The combined Parents & Elders outlook is {outlook.replace('_', ' ')}. It describes symbolic family-role themes rather than facts about another person.", "limitation": "This synthesis cannot predict a parent or elder's health, illness, lifespan, death, intentions or character, and cannot guarantee conflict, reconciliation, caregiving, support or family outcomes.", "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory}}
