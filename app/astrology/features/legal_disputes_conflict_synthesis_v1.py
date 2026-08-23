from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.legal_disputes_conflict_event_intelligence_v1 import analyze_legal_disputes_conflict_event_intelligence_v1
from app.astrology.features.legal_disputes_conflict_reasoning_v1 import analyze_legal_disputes_conflict_v1
from app.astrology.features.legal_disputes_conflict_timing_v1 import analyze_legal_disputes_conflict_timing_v1
from app.astrology.features.legal_disputes_conflict_trajectory_v1 import analyze_legal_disputes_conflict_trajectory_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_legal_disputes_conflict_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Combine legal/conflict natal, timing, event and trajectory signals without predicting legal outcomes."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_legal_disputes_conflict_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "legal_disputes_conflict_synthesis", "model_version": "v1", "reason": "Legal, Disputes & Conflict natal foundation is unavailable."}

    timing = analyze_legal_disputes_conflict_timing_v1(chart, reference_moment)
    events = analyze_legal_disputes_conflict_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_legal_disputes_conflict_trajectory_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    dispute = _b(.44*_f(themes.get("dispute_engagement")) + .18*_f(future.get("dispute_activation_score")) + .28*_f(trajectory.get("dispute_engagement_score")) + .10*_f(themes.get("competition_assertiveness")))
    negotiation = _b(.44*_f(themes.get("negotiation_mediation")) + .18*_f(future.get("negotiation_support_score")) + .28*_f(trajectory.get("negotiation_mediation_score")) + .10*_f(themes.get("resolution_capacity")))
    complexity = _b(.44*_f(themes.get("complexity_endurance")) + .18*_f(future.get("complexity_endurance_score")) + .28*_f(trajectory.get("complexity_endurance_score")) + .10*_f(themes.get("dispute_engagement")))
    principles = _b(.44*_f(themes.get("principles_fairness")) + .18*_f(future.get("principles_fairness_score")) + .28*_f(trajectory.get("principles_fairness_score")) + .10*_f(themes.get("negotiation_mediation")))
    competition = _b(.44*_f(themes.get("competition_assertiveness")) + .18*_f(future.get("competition_assertiveness_score")) + .28*_f(trajectory.get("competition_assertiveness_score")) + .10*_f(themes.get("dispute_engagement")))
    resolution = _b(.44*_f(themes.get("resolution_capacity")) + .18*_f(future.get("resolution_support_score")) + .28*_f(trajectory.get("resolution_capacity_score")) + .10*_f(themes.get("negotiation_mediation")))

    scores = {
        "dispute_engagement": dispute,
        "negotiation_mediation": negotiation,
        "complexity_endurance": complexity,
        "principles_fairness": principles,
        "competition_assertiveness": competition,
        "resolution_capacity": resolution,
    }
    strongest = max(scores.items(), key=lambda item: item[1])
    if negotiation >= .66 and resolution >= .60:
        outlook = "negotiation_and_resolution_emphasis"
    elif competition >= .66 and dispute >= .60:
        outlook = "assertive_conflict_engagement_emphasis"
    elif complexity >= .66:
        outlook = "complexity_and_endurance_emphasis"
    else:
        outlook = "balanced_conflict_management_development"

    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _b(.40 + .30*coverage + .18*strongest[1] + .12*resolution)

    return {
        "available": True,
        "event": "legal_disputes_conflict_synthesis",
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
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known legal history and actual outcomes override predictive assumptions. Historical astrology may interpret confirmed periods but must never manufacture disputes, litigation, arrests, liability findings, judgments, regulatory actions, settlement amounts or wins/losses.",
        },
        "answer": f"The combined Legal, Disputes & Conflict outlook is {outlook.replace('_', ' ')}. It describes symbolic conflict-management themes rather than a legal prediction.",
        "limitation": "This synthesis is not legal advice and cannot predict guilt, liability, court verdicts, arrest, imprisonment, criminal outcomes, regulatory action, exact dispute outcomes, settlement amounts, or whether a matter will be won or lost.",
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
