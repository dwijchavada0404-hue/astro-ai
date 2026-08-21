from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.location_settlement_event_intelligence_v1 import analyze_location_settlement_event_intelligence_v1
from app.astrology.features.location_settlement_reasoning_v1 import analyze_location_settlement_v1
from app.astrology.features.location_settlement_timing_v1 import analyze_location_settlement_timing_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_location_settlement_trajectory_v1(
    chart: dict[str, Any], reference_moment: datetime
) -> dict[str, Any]:
    """Synthesize long-run rootedness, mobility, foreign exposure and settlement tension."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_location_settlement_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "location_settlement_trajectory", "model_version": "v1", "reason": "Location natal foundation is unavailable."}

    timing = analyze_location_settlement_timing_v1(chart, reference_moment)
    events = analyze_location_settlement_event_intelligence_v1(chart, reference_moment)
    themes = _safe_dict(natal.get("theme_scores"))

    rooted = _safe_float(themes.get("rooted_home_base"))
    mobility = _safe_float(themes.get("domestic_relocation"))
    exposure = _safe_float(themes.get("foreign_exposure"))
    residence = _safe_float(themes.get("long_distance_residence"))
    settlement = _safe_float(themes.get("foreign_settlement"))

    future_period = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    future_mobility = _safe_float(future_period.get("relocation_activation_score"))
    future_exposure = _safe_float(future_period.get("foreign_exposure_score"))
    future_settlement = _safe_float(future_period.get("foreign_settlement_support_score"))

    stability_score = _bounded(0.68 * rooted + 0.18 * (1.0 - mobility) + 0.14 * (1.0 - settlement))
    mobility_trajectory = _bounded(0.48 * mobility + 0.24 * residence + 0.28 * future_mobility)
    international_trajectory = _bounded(0.42 * exposure + 0.24 * residence + 0.18 * future_exposure + 0.16 * future_settlement)
    settlement_trajectory = _bounded(0.46 * settlement + 0.28 * residence + 0.16 * future_settlement + 0.10 * exposure)
    change_pressure = _bounded(0.46 * mobility + 0.26 * future_mobility + 0.16 * exposure + 0.12 * settlement)
    adaptability = _bounded(0.34 + 0.24 * mobility + 0.22 * exposure + 0.20 * rooted)
    re_rooting_capacity = _bounded(0.52 * rooted + 0.26 * adaptability + 0.22 * (1.0 - change_pressure))

    if settlement_trajectory >= 0.68 and international_trajectory >= 0.62:
        trajectory = "strong_international_residence_settlement_theme"
    elif international_trajectory >= 0.58:
        trajectory = "international_exposure_with_location_mobility"
    elif mobility_trajectory >= 0.55:
        trajectory = "relocation_or_multi_base_trajectory"
    elif stability_score >= 0.60:
        trajectory = "rooted_home_base_trajectory"
    else:
        trajectory = "mixed_location_trajectory"

    return {
        "available": True,
        "event": "location_settlement_trajectory",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "trajectory": trajectory,
        "scores": {
            "home_base_stability": stability_score,
            "mobility_trajectory": mobility_trajectory,
            "international_trajectory": international_trajectory,
            "foreign_settlement_trajectory": settlement_trajectory,
            "location_change_pressure": change_pressure,
            "adaptability": adaptability,
            "re_rooting_capacity": re_rooting_capacity,
        },
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None,
        "timing_available": bool(timing.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Trajectory describes symbolic location patterns, not a factual migration biography. Confirmed residence and migration history always overrides inferred past patterns.",
        },
        "answer": "The trajectory layer compares rootedness, mobility, international exposure, longer-distance residence, change pressure and the capacity to establish or re-establish a stable base.",
        "limitation": (
            "A strong international or foreign-settlement trajectory does not guarantee emigration, permanent residence, citizenship or life abroad. "
            "It may manifest through repeated travel, international work or clients, study, family links, temporary residence or multiple home bases."
        ),
    }
