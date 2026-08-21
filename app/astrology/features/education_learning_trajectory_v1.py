from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.education_learning_event_intelligence_v1 import analyze_education_learning_event_intelligence_v1
from app.astrology.features.education_learning_reasoning_v1 import analyze_education_learning_v1
from app.astrology.features.education_learning_timing_v1 import analyze_education_learning_timing_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_education_learning_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize longer-term learning development without predicting credentials or outcomes."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_education_learning_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "education_learning_trajectory", "model_version": "v1", "reason": "Education natal foundation is unavailable."}

    timing = analyze_education_learning_timing_v1(chart, reference_moment)
    events = analyze_education_learning_event_intelligence_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))

    foundation = _safe_float(themes.get("foundational_learning"))
    higher = _safe_float(themes.get("higher_education"))
    analytical = _safe_float(themes.get("analytical_learning"))
    communication = _safe_float(themes.get("communication_learning"))
    research = _safe_float(themes.get("research_depth"))
    creative = _safe_float(themes.get("creative_learning"))

    present = _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    present_study = _safe_float(present.get("study_support_score"))
    future_study = _safe_float(future.get("study_support_score"))
    future_higher = _safe_float(future.get("higher_education_support_score"))
    future_skill = _safe_float(future.get("skill_learning_support_score"))
    future_research = _safe_float(future.get("research_support_score"))

    breadth_score = _bounded(0.24 * foundation + 0.20 * analytical + 0.18 * communication + 0.14 * creative + 0.12 * higher + 0.12 * research)
    specialization_score = _bounded(0.34 * higher + 0.30 * research + 0.18 * analytical + 0.18 * future_higher)
    applied_learning_score = _bounded(0.34 * analytical + 0.28 * communication + 0.20 * future_skill + 0.18 * foundation)
    research_depth_score = _bounded(0.48 * research + 0.22 * analytical + 0.18 * future_research + 0.12 * higher)
    continuing_learning_score = _bounded(0.30 * foundation + 0.22 * communication + 0.18 * analytical + 0.16 * future_study + 0.14 * future_skill)
    transition_pressure_score = _bounded(0.36 * future_higher + 0.28 * future_study + 0.20 * future_research + 0.16 * (1.0 - foundation))

    if specialization_score >= 0.66 and research_depth_score >= 0.58:
        trajectory_pattern = "advanced_specialization_and_depth"
    elif applied_learning_score >= 0.66 and continuing_learning_score >= 0.58:
        trajectory_pattern = "applied_continuous_skill_growth"
    elif breadth_score >= 0.64 and specialization_score < 0.58:
        trajectory_pattern = "broad_multidisciplinary_learning"
    elif transition_pressure_score >= 0.62:
        trajectory_pattern = "education_or_skill_transition_phase"
    else:
        trajectory_pattern = "balanced_learning_development"

    if future_study > present_study + 0.08:
        near_term_direction = "learning_support_strengthening"
    elif future_study + 0.08 < present_study:
        near_term_direction = "formal_study_support_cooling"
    elif future_higher >= 0.60:
        near_term_direction = "higher_study_or_specialization_emphasis"
    elif future_skill >= 0.60:
        near_term_direction = "skill_development_emphasis"
    elif future_research >= 0.60:
        near_term_direction = "research_depth_emphasis"
    else:
        near_term_direction = "broadly_steady_learning_pattern"

    return {
        "available": True,
        "event": "education_learning_trajectory",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "breadth_score": breadth_score,
        "specialization_score": specialization_score,
        "applied_learning_score": applied_learning_score,
        "research_depth_score": research_depth_score,
        "continuing_learning_score": continuing_learning_score,
        "transition_pressure_score": transition_pressure_score,
        "trajectory_pattern": trajectory_pattern,
        "near_term_direction": near_term_direction,
        "timing_available": bool(timing.get("available")),
        "events_available": bool(events.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known education, qualifications and learning history override symbolic trajectory assumptions. Astrology must not create unverified admission, exam, graduation, certification or research facts.",
        },
        "answer": f"The longer-term learning trajectory is {trajectory_pattern.replace('_', ' ')}, with a near-term direction of {near_term_direction.replace('_', ' ')}.",
        "limitation": (
            "This trajectory describes symbolic learning development only. It does not guarantee admission, exam results, grades, graduation, scholarships, certification, licensure, research completion or employment."
        ),
        "components": {"natal": natal, "timing": timing, "events": events},
    }
