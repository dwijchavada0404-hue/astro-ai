from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.family_children_direction_v1 import analyze_family_children_direction_v1
from app.astrology.features.family_children_events_v1 import analyze_family_children_events_v1
from app.astrology.features.family_children_reasoning_v1 import analyze_family_children_v1
from app.astrology.features.family_children_timing_v1 import analyze_family_children_timing_v1
from app.astrology.features.family_children_trajectory_v1 import analyze_family_children_trajectory_v1


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_family_children_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Combine Family & Children V1 components into one bounded synthesis surface."""
    natal = analyze_family_children_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "family_children_synthesis",
            "model_version": "v1",
            "reason": "Family & Children natal foundation is unavailable.",
        }

    direction = analyze_family_children_direction_v1(chart)
    timing = analyze_family_children_timing_v1(chart, reference_moment)
    events = analyze_family_children_events_v1(chart, reference_moment)
    trajectory = analyze_family_children_trajectory_v1(chart, reference_moment)

    direction_score = float(direction.get("primary_score") or 0.0)
    natal_score = float(natal.get("dominant_score") or 0.0)
    stability = float(trajectory.get("stability_score") or 0.0)
    resilience = float(trajectory.get("resilience_score") or 0.0)
    change_pressure = float(trajectory.get("change_pressure_score") or 0.0)
    strongest_event_score = float(events.get("strongest_event_score") or 0.0)

    future = ((timing.get("future") or {}).get("strongest_period") if timing.get("available") else None) or {}
    future_support = float(future.get("family_support_score") or 0.0)
    future_change = float(future.get("family_change_score") or 0.0)

    development_score = _bounded(
        0.20 * natal_score
        + 0.18 * direction_score
        + 0.18 * stability
        + 0.16 * resilience
        + 0.14 * strongest_event_score
        + 0.14 * future_support
        - 0.10 * change_pressure
    )
    confidence = _bounded(
        0.36
        + 0.14 * float(natal.get("confidence") or 0.0)
        + 0.14 * float(direction.get("confidence") or 0.0)
        + 0.18 * development_score
        + (0.08 if timing.get("available") else 0.0)
    )

    if development_score >= 0.68:
        outlook = "strong_supportive_development"
    elif development_score >= 0.45:
        outlook = "moderate_mixed_development"
    else:
        outlook = "limited_or_change_heavy_development"

    components = {
        "natal": natal,
        "direction": direction,
        "timing": timing,
        "events": events,
        "trajectory": trajectory,
    }

    return {
        "available": True,
        "event": "family_children_synthesis",
        "model_version": "v1",
        "family_development_score": development_score,
        "family_development_outlook": outlook,
        "confidence": confidence,
        "primary_direction": direction.get("primary_direction"),
        "primary_direction_label": direction.get("primary_direction_label"),
        "trajectory_pattern": trajectory.get("trajectory_pattern"),
        "near_term_direction": trajectory.get("near_term_direction"),
        "strongest_future_event": events.get("strongest_event"),
        "strongest_future_event_label": events.get("strongest_event_label"),
        "strongest_future_event_score": round(strongest_event_score, 3),
        "future_family_support_score": round(future_support, 3),
        "future_family_change_score": round(future_change, 3),
        "active_present_period": ((timing.get("present") or {}).get("active_period") if timing.get("available") else None),
        "strongest_future_period": future or None,
        "component_availability": {key: bool(value.get("available")) for key, value in components.items()},
        "components": components,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known family and children history overrides predictive assumptions. Past astrological windows may be used to interpret "
                "confirmed milestones, but must never establish conception, pregnancy, childbirth, adoption, parenthood, separation, "
                "bereavement or another family event as fact without user confirmation."
            ),
        },
        "children_question_boundary": (
            "Children-related astrology is expressed only as parenting, nurturing and family-responsibility symbolism. It cannot diagnose "
            "fertility or predict conception, pregnancy, childbirth, biological parenthood, adoption, number or sex of children."
        ),
        "answer": (
            f"The overall Family & Children pattern is {outlook.replace('_', ' ')}. The strongest direction is "
            f"{direction.get('primary_direction_label')}, with a longer-term trajectory of "
            f"{str(trajectory.get('trajectory_pattern') or '').replace('_', ' ')}."
        ),
        "limitation": (
            "This is symbolic astrological synthesis only. It is not fertility, reproductive-health, medical, legal, relationship or "
            "family-planning advice and does not predict or guarantee conception, pregnancy, childbirth, adoption, number or sex of children, "
            "or any specific family outcome."
        ),
    }
