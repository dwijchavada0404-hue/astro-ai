from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.purpose_personal_growth_reasoning_v1 import analyze_purpose_personal_growth_v1
from app.astrology.features.purpose_personal_growth_timing_v1 import analyze_purpose_personal_growth_timing_v1


EVENT_LABELS = {
    "identity_reorientation": "identity reorientation, self-definition or meaningful personal-growth phase",
    "creative_expression_phase": "creative expression, authorship or contribution through ideas/art",
    "service_contribution_phase": "service, responsibility or contribution-oriented phase",
    "teaching_mentoring_guidance": "teaching, mentoring, advising or guidance-oriented contribution",
    "public_contribution_phase": "visible contribution through leadership, work or responsibility",
    "inner_growth_reflection": "reflection, retreat, spiritual inquiry or inner-development phase",
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
    self_dev = _safe_float(themes.get("self_development"))
    creative = _safe_float(themes.get("creative_expression"))
    service = _safe_float(themes.get("service_contribution"))
    knowledge = _safe_float(themes.get("knowledge_guidance"))
    public = _safe_float(themes.get("public_contribution"))
    inner = _safe_float(themes.get("inner_growth"))
    return {
        "identity_reorientation": _bounded(0.68 * self_dev + 0.18 * inner + 0.14 * creative),
        "creative_expression_phase": _bounded(0.66 * creative + 0.20 * self_dev + 0.14 * public),
        "service_contribution_phase": _bounded(0.62 * service + 0.22 * public + 0.16 * knowledge),
        "teaching_mentoring_guidance": _bounded(0.64 * knowledge + 0.20 * service + 0.16 * public),
        "public_contribution_phase": _bounded(0.62 * public + 0.22 * service + 0.16 * self_dev),
        "inner_growth_reflection": _bounded(0.68 * inner + 0.18 * knowledge + 0.14 * self_dev),
    }


def _timing_score(event: str, period: dict[str, Any]) -> float:
    self_growth = _safe_float(period.get("self_growth_support_score"))
    contribution = _safe_float(period.get("contribution_support_score"))
    meaning = _safe_float(period.get("meaning_guidance_support_score"))
    inner = _safe_float(period.get("inner_growth_support_score"))
    if event == "identity_reorientation":
        return 0.70 * self_growth + 0.18 * inner + 0.12 * meaning
    if event == "creative_expression_phase":
        return 0.56 * self_growth + 0.26 * contribution + 0.18 * meaning
    if event == "service_contribution_phase":
        return 0.70 * contribution + 0.18 * meaning + 0.12 * self_growth
    if event == "teaching_mentoring_guidance":
        return 0.66 * meaning + 0.22 * contribution + 0.12 * self_growth
    if event == "public_contribution_phase":
        return 0.72 * contribution + 0.18 * self_growth + 0.10 * meaning
    return 0.72 * inner + 0.18 * meaning + 0.10 * self_growth


def analyze_purpose_personal_growth_event_intelligence_v1(
    chart: dict[str, Any], reference_moment: datetime
) -> dict[str, Any]:
    """Rank symbolic purpose/growth event themes without declaring destiny or factual milestones."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_purpose_personal_growth_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "purpose_personal_growth_event_intelligence",
            "model_version": "v1",
            "reason": "Purpose natal foundation is unavailable.",
        }

    timing = analyze_purpose_personal_growth_timing_v1(chart, reference_moment)
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
        "event": "purpose_personal_growth_event_intelligence",
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
                "Past purpose/growth windows are symbolic only. AstroAI must not state that the user found a calling, underwent a transformation, "
                "became a mentor/leader, reached spiritual attainment or completed a major contribution milestone unless the user confirms it."
            ),
        },
        "answer": "Purpose and growth events are ranked from natal themes and available dasha timing; scores describe symbolic activation, not destiny or event probability.",
        "limitation": (
            "This layer does not prove a calling, destiny, spiritual attainment, moral development, required vocation, leadership outcome, or life transformation. "
            "It cannot replace the user's actual values, choices, responsibilities and lived experience."
        ),
    }
