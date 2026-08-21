from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.family_children_direction_v1 import analyze_family_children_direction_v1
from app.astrology.features.family_children_events_v1 import analyze_family_children_events_v1
from app.astrology.features.family_children_timing_v1 import analyze_family_children_timing_v1


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_family_children_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize longer-term family stability, responsibility, challenge and recovery patterns."""
    direction = analyze_family_children_direction_v1(chart)
    timing = analyze_family_children_timing_v1(chart, reference_moment)
    events = analyze_family_children_events_v1(chart, reference_moment)
    if not direction.get("available"):
        return {
            "available": False,
            "event": "family_children_trajectory",
            "model_version": "v1",
            "reason": "Family & Children direction intelligence is unavailable.",
        }

    ds = direction.get("direction_scores") or {}
    future = ((timing.get("future") or {}).get("strongest_period") if timing.get("available") else None) or {}
    future_support = float(future.get("family_support_score") or 0.0)
    future_change = float(future.get("family_change_score") or 0.0)
    event_scores = events.get("event_scores") or {}

    stability = _bounded(0.62 * float(ds.get("family_stability") or 0.0) + 0.22 * future_support + 0.16 * float(event_scores.get("family_stability") or 0.0) - 0.16 * future_change)
    responsibility_growth = _bounded(0.44 * float(ds.get("family_growth") or 0.0) + 0.28 * float(ds.get("parenting_nurturing") or 0.0) + 0.18 * future_support + 0.10 * future_change)
    change_pressure = _bounded(0.58 * float(ds.get("family_change") or 0.0) + 0.28 * future_change + 0.14 * float(event_scores.get("family_structure_change") or 0.0))
    support_network = _bounded(0.62 * float(ds.get("intergenerational_support") or 0.0) + 0.22 * future_support + 0.16 * stability)
    resilience = _bounded(0.42 * stability + 0.34 * support_network + 0.24 * responsibility_growth)
    recovery = _bounded(0.46 * resilience + 0.30 * future_support + 0.24 * max(0.0, 1.0 - change_pressure))

    if stability >= 0.62 and change_pressure < 0.48:
        trajectory_pattern = "stable_consolidation"
    elif responsibility_growth >= 0.62 and change_pressure >= 0.45:
        trajectory_pattern = "growth_with_adjustment"
    elif change_pressure >= 0.62:
        trajectory_pattern = "transition_and_restructuring"
    else:
        trajectory_pattern = "mixed_family_development"

    near_term_direction = (
        "supportive_consolidation" if future_support - future_change >= 0.16
        else "change_and_adjustment" if future_change - future_support >= 0.16
        else "balanced_support_and_change"
    )

    return {
        "available": True,
        "event": "family_children_trajectory",
        "model_version": "v1",
        "trajectory_pattern": trajectory_pattern,
        "near_term_direction": near_term_direction,
        "stability_score": stability,
        "responsibility_growth_score": responsibility_growth,
        "change_pressure_score": change_pressure,
        "support_network_score": support_network,
        "resilience_score": resilience,
        "recovery_score": recovery,
        "future_family_support_score": round(future_support, 3),
        "future_family_change_score": round(future_change, 3),
        "evidence": {
            "direction": direction,
            "timing": timing,
            "events": events,
        },
        "reality_override": {
            "known_facts_override": True,
            "rule": (
                "Known family circumstances and milestones override astrological inference. Changes in family responsibility or structure "
                "must not be translated into claims about conception, pregnancy, childbirth, adoption, separation, bereavement or another specific event unless confirmed."
            ),
        },
        "answer": (
            f"The longer-term Family & Children trajectory is {trajectory_pattern.replace('_', ' ')}, with a near-term pattern of "
            f"{near_term_direction.replace('_', ' ')}."
        ),
        "limitation": (
            "This is symbolic pattern analysis only. It is not fertility, medical, legal, relationship or family-planning advice and does not guarantee any family outcome."
        ),
    }
