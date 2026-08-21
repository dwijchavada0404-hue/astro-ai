from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.property_home_event_intelligence_v1 import analyze_property_home_event_intelligence_v1
from app.astrology.features.property_home_reasoning_v1 import analyze_property_home_v1
from app.astrology.features.property_home_timing_v1 import analyze_property_home_timing_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_property_home_trajectory_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Synthesize longer-term Property & Home trajectory, challenges and resilience."""
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
            "event": "property_home_trajectory",
            "model_version": "v1",
            "reason": "Property & Home natal foundation is unavailable.",
        }

    timing = analyze_property_home_timing_v1(chart, reference_moment)
    events = analyze_property_home_event_intelligence_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))

    stability = _safe_float(themes.get("home_stability"))
    acquisition = _safe_float(themes.get("property_acquisition"))
    accumulation = _safe_float(themes.get("asset_accumulation"))
    comfort = _safe_float(themes.get("home_comfort"))
    relocation = _safe_float(themes.get("relocation_change"))

    future_period = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    present_period = _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future_home = _safe_float(future_period.get("home_property_support_score"))
    present_home = _safe_float(present_period.get("home_property_support_score"))
    future_move = _safe_float(future_period.get("relocation_activation_score"))

    event_map = _safe_dict(events.get("events"))
    future_acquisition = _safe_float(_safe_dict(_safe_dict(event_map.get("property_acquisition")).get("future")).get("score"))
    future_sale = _safe_float(_safe_dict(_safe_dict(event_map.get("property_sale_disposal")).get("future")).get("score"))
    future_relocation = _safe_float(_safe_dict(_safe_dict(event_map.get("relocation")).get("future")).get("score"))

    accumulation_score = _bounded(0.40 * accumulation + 0.25 * acquisition + 0.20 * future_home + 0.15 * future_acquisition)
    stability_score = _bounded(0.48 * stability + 0.22 * comfort + 0.18 * present_home + 0.12 * future_home - 0.18 * relocation)
    mobility_score = _bounded(0.44 * relocation + 0.28 * future_move + 0.28 * future_relocation)
    challenge_score = _bounded(0.36 * relocation + 0.26 * future_sale + 0.20 * (1.0 - stability) + 0.18 * (1.0 - comfort))
    resilience_score = _bounded(0.34 * stability + 0.28 * accumulation + 0.20 * comfort + 0.18 * future_home)
    recovery_score = _bounded(0.38 * resilience_score + 0.26 * future_home + 0.20 * acquisition + 0.16 * accumulation)

    if accumulation_score >= 0.68 and stability_score >= 0.60:
        trajectory_pattern = "stable_asset_building"
    elif mobility_score >= 0.62:
        trajectory_pattern = "mobile_or_transitioning_home_pattern"
    elif challenge_score >= 0.62 and recovery_score >= 0.55:
        trajectory_pattern = "challenging_but_recoverable"
    else:
        trajectory_pattern = "mixed_gradual_development"

    if future_home > present_home + 0.08:
        near_term_direction = "strengthening"
    elif future_home + 0.08 < present_home:
        near_term_direction = "cooling_or_consolidating"
    elif future_relocation >= 0.60:
        near_term_direction = "change_or_mobility_emphasis"
    else:
        near_term_direction = "broadly_stable"

    return {
        "available": True,
        "event": "property_home_trajectory",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "accumulation_score": accumulation_score,
        "stability_score": stability_score,
        "mobility_score": mobility_score,
        "challenge_score": challenge_score,
        "resilience_score": resilience_score,
        "recovery_score": recovery_score,
        "trajectory_pattern": trajectory_pattern,
        "near_term_direction": near_term_direction,
        "timing_available": bool(timing.get("available")),
        "events_available": bool(events.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known property and residence history overrides symbolic trajectory assumptions. Past activation may help "
                "interpret confirmed history but must not create unverified ownership, sale, inheritance or relocation facts."
            ),
        },
        "answer": (
            f"The longer-term Property & Home trajectory is {trajectory_pattern.replace('_', ' ')}, with a "
            f"near-term direction of {near_term_direction.replace('_', ' ')}."
        ),
        "limitation": (
            "This trajectory analysis does not guarantee property accumulation, stable residence, purchase, sale, inheritance, "
            "financing, relocation, recovery from housing difficulty or investment returns."
        ),
        "components": {"natal": natal, "timing": timing, "events": events},
    }
