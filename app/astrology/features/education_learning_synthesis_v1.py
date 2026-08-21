from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.education_learning_event_intelligence_v1 import analyze_education_learning_event_intelligence_v1
from app.astrology.features.education_learning_reasoning_v1 import analyze_education_learning_v1
from app.astrology.features.education_learning_timing_v1 import analyze_education_learning_timing_v1
from app.astrology.features.education_learning_trajectory_v1 import analyze_education_learning_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_education_learning_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Produce a guarded top-level Education & Learning synthesis."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_education_learning_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "education_learning_synthesis",
            "model_version": "v1",
            "reason": "Education natal foundation is unavailable.",
        }

    timing = analyze_education_learning_timing_v1(chart, reference_moment)
    events = analyze_education_learning_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_education_learning_trajectory_v1(chart, reference_moment)

    themes = _safe_dict(natal.get("theme_scores"))
    foundation = _safe_float(themes.get("foundational_learning"))
    higher = _safe_float(themes.get("higher_education"))
    analytical = _safe_float(themes.get("analytical_learning"))
    communication = _safe_float(themes.get("communication_learning"))
    research = _safe_float(themes.get("research_depth"))
    creative = _safe_float(themes.get("creative_learning"))

    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    future_study = _safe_float(future.get("study_support_score"))
    future_higher = _safe_float(future.get("higher_education_support_score"))
    future_skill = _safe_float(future.get("skill_learning_support_score"))
    future_research = _safe_float(future.get("research_support_score"))

    breadth = _safe_float(trajectory.get("breadth_score")) if trajectory.get("available") else 0.0
    specialization = _safe_float(trajectory.get("specialization_score")) if trajectory.get("available") else 0.0
    applied = _safe_float(trajectory.get("applied_learning_score")) if trajectory.get("available") else 0.0
    continuing = _safe_float(trajectory.get("continuing_learning_score")) if trajectory.get("available") else 0.0

    study_continuity_score = _bounded(0.48 * foundation + 0.20 * future_study + 0.16 * continuing + 0.16 * communication)
    higher_education_score = _bounded(0.50 * higher + 0.22 * future_higher + 0.16 * specialization + 0.12 * foundation)
    skill_development_score = _bounded(0.30 * analytical + 0.26 * communication + 0.20 * future_skill + 0.14 * applied + 0.10 * creative)
    research_depth_score = _bounded(0.50 * research + 0.22 * future_research + 0.16 * specialization + 0.12 * analytical)
    learning_adaptability_score = _bounded(0.26 * breadth + 0.22 * continuing + 0.20 * analytical + 0.18 * communication + 0.14 * creative)

    strongest = max(
        {
            "study_continuity": study_continuity_score,
            "higher_education": higher_education_score,
            "skill_development": skill_development_score,
            "research_depth": research_depth_score,
            "learning_adaptability": learning_adaptability_score,
        }.items(),
        key=lambda item: item[1],
    )

    if higher_education_score >= 0.66 and research_depth_score >= 0.58:
        outlook = "advanced_study_and_depth_emphasis"
    elif skill_development_score >= 0.66:
        outlook = "applied_skill_development_emphasis"
    elif study_continuity_score >= 0.64:
        outlook = "steady_learning_continuity"
    elif learning_adaptability_score >= 0.62:
        outlook = "flexible_multidisciplinary_learning"
    else:
        outlook = "mixed_learning_development"

    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _bounded(0.40 + 0.30 * coverage + 0.18 * strongest[1] + 0.12 * learning_adaptability_score)

    return {
        "available": True,
        "event": "education_learning_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "outlook": outlook,
        "confidence": confidence,
        "component_coverage": round(coverage, 3),
        "scores": {
            "study_continuity": study_continuity_score,
            "higher_education": higher_education_score,
            "skill_development": skill_development_score,
            "research_depth": research_depth_score,
            "learning_adaptability": learning_adaptability_score,
        },
        "strongest_area": strongest[0],
        "strongest_area_score": strongest[1],
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None,
        "strongest_future_period": future or None,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known education history, qualifications, exam results and current study status override predictive assumptions. Historical astrology may interpret confirmed education milestones but must never manufacture them.",
        },
        "answer": (
            f"The combined Education & Learning outlook is {outlook.replace('_', ' ')}. "
            "Study continuity, higher education, skill development and research depth are evaluated separately."
        ),
        "limitation": (
            "This synthesis does not guarantee admission, examination success, marks, grades, scholarships, graduation, certification, licensure, research completion, institution placement or employment outcomes."
        ),
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
