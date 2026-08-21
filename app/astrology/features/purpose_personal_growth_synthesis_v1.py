from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.purpose_personal_growth_event_intelligence_v1 import analyze_purpose_personal_growth_event_intelligence_v1
from app.astrology.features.purpose_personal_growth_reasoning_v1 import analyze_purpose_personal_growth_v1
from app.astrology.features.purpose_personal_growth_timing_v1 import analyze_purpose_personal_growth_timing_v1
from app.astrology.features.purpose_personal_growth_trajectory_v1 import analyze_purpose_personal_growth_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_purpose_personal_growth_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Produce a guarded synthesis of symbolic purpose and personal-growth themes."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_purpose_personal_growth_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "purpose_personal_growth_synthesis", "model_version": "v1", "reason": "Purpose natal foundation is unavailable."}

    timing = analyze_purpose_personal_growth_timing_v1(chart, reference_moment)
    events = analyze_purpose_personal_growth_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_purpose_personal_growth_trajectory_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))

    self_dev = _safe_float(themes.get("self_development"))
    creative = _safe_float(themes.get("creative_expression"))
    service = _safe_float(themes.get("service_contribution"))
    knowledge = _safe_float(themes.get("knowledge_guidance"))
    public = _safe_float(themes.get("public_contribution"))
    inner = _safe_float(themes.get("inner_growth"))

    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    future_self = _safe_float(future.get("self_growth_support_score"))
    future_contribution = _safe_float(future.get("contribution_support_score"))
    future_meaning = _safe_float(future.get("meaning_guidance_support_score"))
    future_inner = _safe_float(future.get("inner_growth_support_score"))

    self_authorship = _safe_float(trajectory.get("self_authorship_score")) if trajectory.get("available") else 0.0
    contribution_orientation = _safe_float(trajectory.get("contribution_orientation_score")) if trajectory.get("available") else 0.0
    meaning_orientation = _safe_float(trajectory.get("meaning_guidance_score")) if trajectory.get("available") else 0.0
    integration = _safe_float(trajectory.get("integration_score")) if trajectory.get("available") else 0.0

    self_development_score = _bounded(0.46 * self_dev + 0.20 * future_self + 0.18 * self_authorship + 0.16 * creative)
    contribution_score = _bounded(0.30 * service + 0.26 * public + 0.20 * future_contribution + 0.14 * contribution_orientation + 0.10 * knowledge)
    meaning_guidance_score = _bounded(0.42 * knowledge + 0.22 * future_meaning + 0.18 * meaning_orientation + 0.10 * inner + 0.08 * self_dev)
    inner_growth_score = _bounded(0.50 * inner + 0.22 * future_inner + 0.16 * integration + 0.12 * self_dev)
    creative_expression_score = _bounded(0.56 * creative + 0.18 * self_dev + 0.14 * self_authorship + 0.12 * future_self)
    integration_score = _bounded(0.24 * self_development_score + 0.22 * contribution_score + 0.20 * meaning_guidance_score + 0.18 * inner_growth_score + 0.16 * integration)

    score_map = {
        "self_development": self_development_score,
        "contribution": contribution_score,
        "meaning_guidance": meaning_guidance_score,
        "inner_growth": inner_growth_score,
        "creative_expression": creative_expression_score,
        "integration": integration_score,
    }
    strongest = max(score_map.items(), key=lambda item: item[1])

    if integration_score >= 0.66 and contribution_score >= 0.58:
        outlook = "integrated_growth_and_contribution"
    elif meaning_guidance_score >= 0.66:
        outlook = "meaning_and_guidance_emphasis"
    elif self_development_score >= 0.66:
        outlook = "self_authorship_and_growth_emphasis"
    elif inner_growth_score >= 0.64:
        outlook = "inner_reflection_and_growth_emphasis"
    elif creative_expression_score >= 0.64:
        outlook = "creative_self_expression_emphasis"
    else:
        outlook = "mixed_personal_growth_development"

    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _bounded(0.40 + 0.30 * coverage + 0.18 * strongest[1] + 0.12 * integration_score)

    return {
        "available": True,
        "event": "purpose_personal_growth_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "outlook": outlook,
        "confidence": confidence,
        "component_coverage": round(coverage, 3),
        "scores": score_map,
        "strongest_area": strongest[0],
        "strongest_area_score": strongest[1],
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None,
        "strongest_future_period": future or None,
        "historical_validation": {
            "status": "unconfirmed", "reality_override": True,
            "rule": "Known values, choices, roles and lived milestones override predictive assumptions. Historical astrology may interpret confirmed growth periods but must never manufacture a calling, transformation, leadership role or spiritual milestone.",
        },
        "answer": f"The combined Purpose & Personal Growth outlook is {outlook.replace('_', ' ')}. The result describes themes for reflection, not a fixed destiny or singular life purpose.",
        "limitation": "This synthesis cannot determine a fixed life purpose, moral worth, spiritual status, mandatory vocation, leadership destiny or guaranteed transformation. Personal values, choices and lived experience remain primary.",
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
