from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.property_home_direction_v1 import analyze_property_home_direction_v1
from app.astrology.features.property_home_event_intelligence_v1 import analyze_property_home_event_intelligence_v1
from app.astrology.features.property_home_reasoning_v1 import analyze_property_home_v1
from app.astrology.features.property_home_timing_v1 import analyze_property_home_timing_v1
from app.astrology.features.property_home_trajectory_v1 import analyze_property_home_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _support_label(score: float) -> str:
    if score >= 0.72:
        return "strong"
    if score >= 0.52:
        return "moderate"
    return "limited"


def analyze_property_home_synthesis_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Combine Property & Home V1 layers into one bounded synthesis."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_property_home_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "property_home_synthesis",
            "model_version": "v1",
            "reason": "Property & Home natal foundation is unavailable.",
        }

    direction = analyze_property_home_direction_v1(chart)
    timing = analyze_property_home_timing_v1(chart, reference_moment)
    events = analyze_property_home_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_property_home_trajectory_v1(chart, reference_moment)

    natal_score = _safe_float(natal.get("dominant_score"))
    accumulation = _safe_float(trajectory.get("accumulation_score"))
    stability = _safe_float(trajectory.get("stability_score"))
    resilience = _safe_float(trajectory.get("resilience_score"))
    recovery = _safe_float(trajectory.get("recovery_score"))

    present_period = _safe_dict(_safe_dict(timing.get("present")).get("active_period"))
    future_period = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period"))
    present_support = _safe_float(present_period.get("home_property_support_score"))
    future_support = _safe_float(future_period.get("home_property_support_score"))
    support = max(present_support, future_support)

    development_score = round(min(
        1.0,
        0.27 * natal_score
        + 0.24 * accumulation
        + 0.18 * stability
        + 0.12 * resilience
        + 0.10 * recovery
        + 0.09 * support,
    ), 3)

    event_map = _safe_dict(events.get("events"))
    ranked_future = sorted(
        (
            (name, _safe_float(_safe_dict(data.get("future")).get("score")))
            for name, data in event_map.items()
            if isinstance(data, dict)
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    strongest_future_event = ranked_future[0][0] if ranked_future else None
    strongest_future_event_score = ranked_future[0][1] if ranked_future else 0.0

    component_availability = {
        "natal": bool(natal.get("available")),
        "direction": bool(direction.get("available")),
        "timing": bool(timing.get("available")),
        "events": bool(events.get("available")),
        "trajectory": bool(trajectory.get("available")),
    }
    available_count = sum(1 for value in component_availability.values() if value)
    confidence = round(min(0.95, 0.47 + 0.09 * available_count), 2)

    primary_direction = direction.get("primary_direction") if direction.get("available") else None
    primary_direction_label = direction.get("primary_direction_label") if direction.get("available") else None

    summary_parts = [f"Overall symbolic Property & Home development support is {_support_label(development_score)}"]
    if primary_direction_label:
        summary_parts.append(f"the strongest home/property direction is {primary_direction_label}")
    if trajectory.get("trajectory_pattern"):
        summary_parts.append(f"the broader trajectory is {str(trajectory.get('trajectory_pattern')).replace('_', ' ')}")
    if trajectory.get("near_term_direction"):
        summary_parts.append(f"the near-term pattern is {str(trajectory.get('near_term_direction')).replace('_', ' ')}")

    return {
        "available": True,
        "event": "property_home_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "property_home_development_score": development_score,
        "property_home_development_outlook": _support_label(development_score),
        "confidence": confidence,
        "component_availability": component_availability,
        "primary_direction": primary_direction,
        "primary_direction_label": primary_direction_label,
        "secondary_direction": direction.get("secondary_direction") if direction.get("available") else None,
        "secondary_direction_label": direction.get("secondary_direction_label") if direction.get("available") else None,
        "trajectory_pattern": trajectory.get("trajectory_pattern"),
        "near_term_direction": trajectory.get("near_term_direction"),
        "accumulation_score": accumulation,
        "stability_score": stability,
        "mobility_score": _safe_float(trajectory.get("mobility_score")),
        "challenge_score": _safe_float(trajectory.get("challenge_score")),
        "resilience_score": resilience,
        "recovery_score": recovery,
        "current_home_property_support_score": present_support if timing.get("available") else None,
        "future_home_property_support_score": future_support if timing.get("available") else None,
        "strongest_past_period": _safe_dict(_safe_dict(timing.get("past")).get("strongest_period")) or None,
        "active_present_period": present_period or None,
        "strongest_future_period": future_period or None,
        "strongest_future_event": strongest_future_event,
        "strongest_future_event_score": round(strongest_future_event_score, 3),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known ownership, residence, purchase, sale, inheritance, renovation and relocation facts override predictive "
                "assumptions. Past astrological windows may only help interpret milestones that the user has confirmed."
            ),
        },
        "components": {
            "natal": natal,
            "direction": direction,
            "timing": timing,
            "events": events,
            "trajectory": trajectory,
        },
        "answer": ". ".join(summary_parts) + ".",
        "limitation": (
            "This synthesis describes symbolic astrological tendencies only. It does not guarantee property ownership, purchase, "
            "sale, inheritance, financing approval, construction, renovation, relocation, residential stability, recovery from "
            "housing difficulty or investment returns, and should not replace legal, financial or real-estate advice."
        ),
    }
