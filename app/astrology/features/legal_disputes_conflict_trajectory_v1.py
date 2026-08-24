from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.legal_disputes_conflict_event_intelligence_v1 import analyze_legal_disputes_conflict_event_intelligence_v1
from app.astrology.features.legal_disputes_conflict_reasoning_v1 import analyze_legal_disputes_conflict_v1
from app.astrology.features.legal_disputes_conflict_timing_v1 import analyze_legal_disputes_conflict_timing_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_legal_disputes_conflict_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize longer-term conflict-management patterns without predicting legal outcomes."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_legal_disputes_conflict_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "legal_disputes_conflict_trajectory", "model_version": "v1", "reason": "Legal, Disputes & Conflict natal foundation is unavailable."}
    timing = analyze_legal_disputes_conflict_timing_v1(chart, reference_moment)
    events = analyze_legal_disputes_conflict_event_intelligence_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    present = _d(_d(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    dispute = _b(.56*_f(themes.get("dispute_engagement")) + .24*_f(future.get("dispute_activation_score")) + .10*_f(themes.get("competition_assertiveness")) + .10*_f(themes.get("complexity_endurance")))
    negotiation = _b(.56*_f(themes.get("negotiation_mediation")) + .24*_f(future.get("negotiation_support_score")) + .10*_f(themes.get("resolution_capacity")) + .10*_f(themes.get("principles_fairness")))
    complexity = _b(.56*_f(themes.get("complexity_endurance")) + .24*_f(future.get("complexity_endurance_score")) + .10*_f(themes.get("dispute_engagement")) + .10*_f(themes.get("resolution_capacity")))
    principles = _b(.56*_f(themes.get("principles_fairness")) + .24*_f(future.get("principles_fairness_score")) + .10*_f(themes.get("negotiation_mediation")) + .10*_f(themes.get("resolution_capacity")))
    competition = _b(.56*_f(themes.get("competition_assertiveness")) + .24*_f(future.get("competition_assertiveness_score")) + .10*_f(themes.get("dispute_engagement")) + .10*_f(themes.get("complexity_endurance")))
    resolution = _b(.56*_f(themes.get("resolution_capacity")) + .24*_f(future.get("resolution_support_score")) + .10*_f(themes.get("negotiation_mediation")) + .10*_f(themes.get("principles_fairness")))

    if negotiation >= .66 and resolution >= .60:
        pattern = "negotiation_and_resolution_emphasis"
    elif competition >= .66 and dispute >= .60:
        pattern = "assertive_conflict_engagement_emphasis"
    elif complexity >= .66:
        pattern = "complexity_and_endurance_emphasis"
    else:
        pattern = "balanced_conflict_management_pattern"

    present_overall = _f(present.get("overall_activation_score")); future_overall = _f(future.get("overall_activation_score"))
    if future_overall > present_overall + .08:
        direction = "conflict_management_activation_strengthening"
    elif _f(future.get("resolution_support_score")) >= .60:
        direction = "resolution_support_emphasis"
    elif _f(future.get("negotiation_support_score")) >= .60:
        direction = "negotiation_support_emphasis"
    else:
        direction = "broadly_steady_conflict_management_pattern"

    return {
        "available": True, "event": "legal_disputes_conflict_trajectory", "model_version": "v1", "reference_moment": reference_moment.isoformat(),
        "dispute_engagement_score": dispute, "negotiation_mediation_score": negotiation, "complexity_endurance_score": complexity,
        "principles_fairness_score": principles, "competition_assertiveness_score": competition, "resolution_capacity_score": resolution,
        "trajectory_pattern": pattern, "near_term_direction": direction, "timing_available": bool(timing.get("available")), "events_available": bool(events.get("available")),
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known legal history and real outcomes override symbolic trajectory assumptions. Astrology must not manufacture disputes, litigation, arrests, liability findings, judgments, regulatory actions or settlements."},
        "answer": f"The longer-term Legal, Disputes & Conflict trajectory is {pattern.replace('_', ' ')}, with a near-term direction of {direction.replace('_', ' ')}.",
        "limitation": "This trajectory is not legal advice and cannot predict guilt, liability, court verdicts, arrest, imprisonment, criminal outcomes, regulatory action, exact dispute outcomes, settlement amounts, or whether a case will be won or lost.",
        "components": {"natal": natal, "timing": timing, "events": events},
    }
