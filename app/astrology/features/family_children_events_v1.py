from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.family_children_direction_v1 import analyze_family_children_direction_v1
from app.astrology.features.family_children_timing_v1 import analyze_family_children_timing_v1


EVENT_LABELS = {
    "parenting_nurturing": "parenting, mentoring or nurturing responsibility",
    "family_growth_responsibility": "growth in family bonds or responsibilities",
    "family_structure_change": "change in family structure or domestic responsibilities",
    "intergenerational_support": "support involving elders, relatives or intergenerational family ties",
    "family_stability": "consolidation of family support and stability",
}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_family_children_events_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Score symbolic Family & Children event themes without asserting biological events."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    direction = analyze_family_children_direction_v1(chart)
    timing = analyze_family_children_timing_v1(chart, reference_moment)
    if not direction.get("available"):
        return {
            "available": False,
            "event": "family_children_events",
            "model_version": "v1",
            "reason": "Family & Children direction intelligence is unavailable.",
        }

    scores = direction.get("direction_scores") or {}
    future = ((timing.get("future") or {}).get("strongest_period") if timing.get("available") else None) or {}
    support = float(future.get("family_support_score") or 0.0)
    change = float(future.get("family_change_score") or 0.0)

    event_scores = {
        "parenting_nurturing": _bounded(0.70 * float(scores.get("parenting_nurturing") or 0.0) + 0.30 * support),
        "family_growth_responsibility": _bounded(0.62 * float(scores.get("family_growth") or 0.0) + 0.24 * support + 0.14 * change),
        "family_structure_change": _bounded(0.64 * float(scores.get("family_change") or 0.0) + 0.36 * change),
        "intergenerational_support": _bounded(0.72 * float(scores.get("intergenerational_support") or 0.0) + 0.28 * support),
        "family_stability": _bounded(0.72 * float(scores.get("family_stability") or 0.0) + 0.28 * support - 0.16 * change),
    }

    ranked = sorted(event_scores.items(), key=lambda item: item[1], reverse=True)
    strongest_event, strongest_score = ranked[0]
    return {
        "available": True,
        "event": "family_children_events",
        "model_version": "v1",
        "strongest_event": strongest_event,
        "strongest_event_label": EVENT_LABELS[strongest_event],
        "strongest_event_score": strongest_score,
        "event_scores": event_scores,
        "ranked_events": [
            {"event": key, "label": EVENT_LABELS[key], "score": score}
            for key, score in ranked
        ],
        "future_window": future or None,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Astrological family-event symbolism is not evidence that a biological or legal family milestone occurred. "
                "Known family history overrides predictive assumptions."
            ),
        },
        "children_question_boundary": (
            "A children-related score describes parenting, nurturing, mentoring or family-responsibility symbolism only. "
            "It must not be converted into a fertility, conception, pregnancy, childbirth, adoption, child-count or child-sex prediction."
        ),
        "answer": (
            f"The strongest symbolic family-event theme is {EVENT_LABELS[strongest_event]}. "
            "This describes a type of family responsibility or change, not a guaranteed real-world event."
        ),
        "limitation": (
            "This is symbolic astrological analysis only. It is not fertility, reproductive-health, medical, legal or adoption advice, "
            "and it does not predict or guarantee conception, pregnancy, childbirth, adoption, number or sex of children, or any family event."
        ),
    }
