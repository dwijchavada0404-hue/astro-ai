from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.purpose_personal_growth_event_intelligence_v1 import analyze_purpose_personal_growth_event_intelligence_v1
from app.astrology.features.purpose_personal_growth_reasoning_v1 import analyze_purpose_personal_growth_v1
from app.astrology.features.purpose_personal_growth_timing_v1 import analyze_purpose_personal_growth_timing_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_purpose_personal_growth_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize longer-term personal growth and contribution themes without fixed-destiny claims."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_purpose_personal_growth_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "purpose_personal_growth_trajectory", "model_version": "v1", "reason": "Purpose natal foundation is unavailable."}

    timing = analyze_purpose_personal_growth_timing_v1(chart, reference_moment)
    events = analyze_purpose_personal_growth_event_intelligence_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))

    self_development = _safe_float(themes.get("self_development"))
    creative = _safe_float(themes.get("creative_expression"))
    service = _safe_float(themes.get("service_contribution"))
    guidance = _safe_float(themes.get("knowledge_guidance"))
    public = _safe_float(themes.get("public_contribution"))
    inner = _safe_float(themes.get("inner_growth"))

    present = _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    present_self = _safe_float(present.get("self_growth_support_score"))
    future_self = _safe_float(future.get("self_growth_support_score"))
    future_contribution = _safe_float(future.get("contribution_support_score"))
    future_meaning = _safe_float(future.get("meaning_guidance_support_score"))
    future_inner = _safe_float(future.get("inner_growth_support_score"))

    self_authorship_score = _bounded(0.56 * self_development + 0.18 * creative + 0.14 * future_self + 0.12 * guidance)
    contribution_orientation_score = _bounded(0.38 * service + 0.34 * public + 0.18 * future_contribution + 0.10 * guidance)
    meaning_guidance_score = _bounded(0.48 * guidance + 0.20 * service + 0.18 * future_meaning + 0.14 * inner)
    creative_expression_score = _bounded(0.62 * creative + 0.18 * self_development + 0.12 * guidance + 0.08 * future_self)
    inner_development_score = _bounded(0.58 * inner + 0.18 * self_development + 0.16 * future_inner + 0.08 * guidance)
    integration_score = _bounded(0.24 * self_authorship_score + 0.22 * contribution_orientation_score + 0.20 * meaning_guidance_score + 0.17 * creative_expression_score + 0.17 * inner_development_score)

    if contribution_orientation_score >= 0.66 and meaning_guidance_score >= 0.58:
        trajectory_pattern = "contribution_and_guidance_development"
    elif self_authorship_score >= 0.66 and creative_expression_score >= 0.58:
        trajectory_pattern = "self_authored_creative_development"
    elif inner_development_score >= 0.66 and meaning_guidance_score >= 0.55:
        trajectory_pattern = "reflective_meaning_centered_growth"
    elif integration_score >= 0.62:
        trajectory_pattern = "integrated_personal_growth"
    else:
        trajectory_pattern = "mixed_personal_growth_development"

    if future_self > present_self + 0.08:
        near_term_direction = "self_development_support_strengthening"
    elif future_contribution >= 0.60:
        near_term_direction = "contribution_and_responsibility_emphasis"
    elif future_meaning >= 0.60:
        near_term_direction = "learning_guidance_and_meaning_emphasis"
    elif future_inner >= 0.60:
        near_term_direction = "reflection_and_inner_growth_emphasis"
    else:
        near_term_direction = "broadly_steady_growth_pattern"

    return {
        "available": True,
        "event": "purpose_personal_growth_trajectory",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "self_authorship_score": self_authorship_score,
        "contribution_orientation_score": contribution_orientation_score,
        "meaning_guidance_score": meaning_guidance_score,
        "creative_expression_score": creative_expression_score,
        "inner_development_score": inner_development_score,
        "integration_score": integration_score,
        "trajectory_pattern": trajectory_pattern,
        "near_term_direction": near_term_direction,
        "timing_available": bool(timing.get("available")),
        "events_available": bool(events.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known values, choices, responsibilities and lived experience override symbolic trajectory assumptions. Astrology must not manufacture a calling, transformation, leadership, mentoring or spiritual-development milestone.",
        },
        "answer": f"The longer-term personal-growth trajectory is {trajectory_pattern.replace('_', ' ')}, with a near-term direction of {near_term_direction.replace('_', ' ')}.",
        "limitation": "This trajectory is reflective symbolism only. It does not establish a fixed destiny, singular life purpose, moral worth, spiritual attainment, mandatory vocation or guaranteed personal transformation.",
        "components": {"natal": natal, "timing": timing, "events": events},
    }
