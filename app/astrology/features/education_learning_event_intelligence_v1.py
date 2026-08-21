from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.education_learning_reasoning_v1 import analyze_education_learning_v1
from app.astrology.features.education_learning_timing_v1 import analyze_education_learning_timing_v1


EVENT_LABELS = {
    "admission_or_enrolment": "admission, enrolment or start of a formal study phase",
    "exam_or_assessment": "examinations, assessments or evaluation-heavy study periods",
    "higher_study_transition": "transition into advanced study, specialization or postgraduate-style learning",
    "skill_or_certification": "skill-building, certification or structured professional learning",
    "research_or_deep_study": "research, investigation, thesis-style or depth-oriented learning",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _outlook(score: float) -> str:
    if score >= 0.75:
        return "strongly_active"
    if score >= 0.50:
        return "active"
    if score >= 0.25:
        return "mildly_active"
    return "weak_signal"


def _natal_scores(natal: dict[str, Any]) -> dict[str, float]:
    themes = _safe_dict(natal.get("theme_scores"))
    foundation = _safe_float(themes.get("foundational_learning"))
    higher = _safe_float(themes.get("higher_education"))
    analytical = _safe_float(themes.get("analytical_learning"))
    communication = _safe_float(themes.get("communication_learning"))
    research = _safe_float(themes.get("research_depth"))
    creative = _safe_float(themes.get("creative_learning"))
    return {
        "admission_or_enrolment": _bounded(0.52 * foundation + 0.30 * higher + 0.18 * communication),
        "exam_or_assessment": _bounded(0.40 * foundation + 0.32 * analytical + 0.18 * communication + 0.10 * research),
        "higher_study_transition": _bounded(0.62 * higher + 0.20 * foundation + 0.18 * research),
        "skill_or_certification": _bounded(0.40 * analytical + 0.34 * communication + 0.16 * foundation + 0.10 * creative),
        "research_or_deep_study": _bounded(0.58 * research + 0.22 * analytical + 0.12 * higher + 0.08 * foundation),
    }


def _timing_score(event: str, period: dict[str, Any]) -> float:
    study = _safe_float(period.get("study_support_score"))
    higher = _safe_float(period.get("higher_education_support_score"))
    skill = _safe_float(period.get("skill_learning_support_score"))
    research = _safe_float(period.get("research_support_score"))
    if event == "admission_or_enrolment":
        return 0.58 * study + 0.42 * higher
    if event == "exam_or_assessment":
        return 0.62 * study + 0.24 * skill + 0.14 * research
    if event == "higher_study_transition":
        return 0.72 * higher + 0.18 * study + 0.10 * research
    if event == "skill_or_certification":
        return 0.66 * skill + 0.24 * study + 0.10 * higher
    return 0.68 * research + 0.20 * higher + 0.12 * skill


def analyze_education_learning_event_intelligence_v1(
    chart: dict[str, Any], reference_moment: datetime
) -> dict[str, Any]:
    """Rank symbolic education events without converting activation into outcomes."""
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
            "event": "education_learning_event_intelligence",
            "model_version": "v1",
            "reason": "Education natal foundation is unavailable.",
        }

    timing = analyze_education_learning_timing_v1(chart, reference_moment)
    natal_scores = _natal_scores(natal)
    periods = {
        "past": _safe_dict(_safe_dict(timing.get("past")).get("strongest_period")) if timing.get("available") else {},
        "present": _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {},
        "future": _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {},
    }

    events: dict[str, Any] = {}
    for name, natal_score in natal_scores.items():
        buckets: dict[str, Any] = {}
        for bucket, period in periods.items():
            score = _bounded(0.60 * natal_score + 0.40 * _timing_score(name, period)) if period else natal_score
            buckets[bucket] = {
                "score": score,
                "outlook": _outlook(score),
                "timing_period": period or None,
                "historical_status": "unconfirmed" if bucket == "past" else None,
            }
        events[name] = {"label": EVENT_LABELS[name], "natal_strength": natal_score, **buckets}

    ranked_future = sorted(
        ((name, _safe_float(_safe_dict(data.get("future")).get("score"))) for name, data in events.items()),
        key=lambda item: item[1], reverse=True,
    )

    return {
        "available": True,
        "event": "education_learning_event_intelligence",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_future_event": ranked_future[0][0] if ranked_future else None,
        "strongest_future_event_score": ranked_future[0][1] if ranked_future else 0.0,
        "timing_available": bool(timing.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Past education-event windows are symbolic only. AstroAI must not state that admission, examination success, graduation, "
                "certification or research milestones occurred unless the user confirms them. Known facts override astrology."
            ),
        },
        "answer": "Education events are ranked from natal learning patterns and available dasha timing; scores describe activation, not outcome probability.",
        "limitation": (
            "This layer does not predict or guarantee admission, exam success, marks or grades, scholarships, graduation, certification, "
            "licensure, research completion, institution placement or employment outcomes."
        ),
    }
