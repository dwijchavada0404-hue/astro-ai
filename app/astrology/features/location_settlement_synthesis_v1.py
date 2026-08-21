from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.location_settlement_event_intelligence_v1 import analyze_location_settlement_event_intelligence_v1
from app.astrology.features.location_settlement_reasoning_v1 import analyze_location_settlement_v1
from app.astrology.features.location_settlement_timing_v1 import analyze_location_settlement_timing_v1
from app.astrology.features.location_settlement_trajectory_v1 import analyze_location_settlement_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_location_settlement_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Produce a guarded top-level Location & Foreign Settlement synthesis."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_location_settlement_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "location_settlement_synthesis", "model_version": "v1", "reason": "Location natal foundation is unavailable."}

    timing = analyze_location_settlement_timing_v1(chart, reference_moment)
    events = analyze_location_settlement_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_location_settlement_trajectory_v1(chart, reference_moment)

    themes = _safe_dict(natal.get("theme_scores"))
    exposure = _safe_float(themes.get("foreign_exposure"))
    residence = _safe_float(themes.get("long_distance_residence"))
    settlement = _safe_float(themes.get("foreign_settlement"))
    rooted = _safe_float(themes.get("rooted_home_base"))
    relocation = _safe_float(themes.get("domestic_relocation"))

    future = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {}
    future_exposure = _safe_float(future.get("foreign_exposure_score"))
    future_settlement = _safe_float(future.get("foreign_settlement_support_score"))
    future_relocation = _safe_float(future.get("relocation_activation_score"))

    trajectory_scores = _safe_dict(trajectory.get("scores")) if trajectory.get("available") else {}
    trajectory_settlement = _safe_float(trajectory_scores.get("foreign_settlement_trajectory"))
    adaptability = _safe_float(trajectory_scores.get("adaptability"))

    foreign_exposure_score = _bounded(0.58 * exposure + 0.24 * future_exposure + 0.18 * residence)
    relocation_score = _bounded(0.58 * relocation + 0.26 * future_relocation + 0.16 * residence)
    long_distance_residence_score = _bounded(0.48 * residence + 0.22 * exposure + 0.18 * future_settlement + 0.12 * adaptability)
    # Permanent-style settlement requires convergence; foreign exposure alone cannot dominate it.
    foreign_settlement_score = _bounded(0.38 * settlement + 0.24 * residence + 0.20 * future_settlement + 0.18 * trajectory_settlement)
    rooted_home_score = _bounded(0.72 * rooted + 0.18 * (1.0 - relocation) + 0.10 * (1.0 - settlement))

    if foreign_settlement_score >= 0.70 and long_distance_residence_score >= 0.62:
        outlook = "stronger_long_term_foreign_base_symbolism"
    elif foreign_exposure_score >= 0.62 and foreign_settlement_score < 0.58:
        outlook = "international_exposure_without_clear_settlement_convergence"
    elif relocation_score >= 0.60:
        outlook = "mobility_or_relocation_emphasis"
    elif rooted_home_score >= 0.64:
        outlook = "rooted_home_base_emphasis"
    else:
        outlook = "mixed_location_outlook"

    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _bounded(0.40 + 0.30 * coverage + 0.18 * max(foreign_settlement_score, rooted_home_score) + 0.12 * adaptability)

    return {
        "available": True,
        "event": "location_settlement_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "outlook": outlook,
        "confidence": confidence,
        "component_coverage": round(coverage, 3),
        "scores": {
            "rooted_home_base": rooted_home_score,
            "relocation": relocation_score,
            "foreign_exposure": foreign_exposure_score,
            "long_distance_residence": long_distance_residence_score,
            "foreign_settlement": foreign_settlement_score,
        },
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None,
        "strongest_future_period": future or None,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known real-world residence and migration facts override predictive assumptions. Historical astrology may interpret user-confirmed location milestones but must never manufacture them.",
        },
        "answer": (
            f"The combined Location & Foreign Settlement outlook is {outlook.replace('_', ' ')}. "
            "Foreign exposure, relocation, long-distance residence and longer-term settlement are evaluated separately."
        ),
        "limitation": (
            "This synthesis does not guarantee a move abroad, foreign employment or study, visa approval, immigration status, permanent residence, "
            "citizenship, return migration, or settlement in any specific country or city. Strong foreign exposure may remain travel, work, study, "
            "family links, clients or temporary residence rather than permanent settlement."
        ),
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
