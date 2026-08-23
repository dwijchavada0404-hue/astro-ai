from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.travel_journeys_event_intelligence_v1 import analyze_travel_journeys_event_intelligence_v1
from app.astrology.features.travel_journeys_reasoning_v1 import analyze_travel_journeys_v1
from app.astrology.features.travel_journeys_timing_v1 import analyze_travel_journeys_timing_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_travel_journeys_trajectory_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Synthesize longer-term travel and mobility patterns without inferring settlement."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_travel_journeys_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "travel_journeys_trajectory", "model_version": "v1", "reason": "Travel & Journeys natal foundation is unavailable."}
    timing = analyze_travel_journeys_timing_v1(chart, reference_moment)
    events = analyze_travel_journeys_event_intelligence_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    present = _d(_d(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    short = _b(.56*_f(themes.get("short_journeys")) + .22*_f(future.get("short_journey_support_score")) + .12*_f(themes.get("recurring_mobility")) + .10*_f(themes.get("travel_adaptability")))
    long = _b(.54*_f(themes.get("long_distance_travel")) + .24*_f(future.get("long_distance_support_score")) + .12*_f(themes.get("international_exposure")) + .10*_f(themes.get("travel_adaptability")))
    international = _b(.54*_f(themes.get("international_exposure")) + .24*_f(future.get("international_support_score")) + .12*_f(themes.get("long_distance_travel")) + .10*_f(themes.get("work_study_travel")))
    work_study = _b(.54*_f(themes.get("work_study_travel")) + .24*_f(future.get("work_study_travel_support_score")) + .12*_f(themes.get("long_distance_travel")) + .10*_f(themes.get("travel_adaptability")))
    mobility = _b(.54*_f(themes.get("recurring_mobility")) + .24*_f(future.get("recurring_mobility_support_score")) + .12*_f(themes.get("short_journeys")) + .10*_f(themes.get("travel_adaptability")))
    adaptability = _b(.54*_f(themes.get("travel_adaptability")) + .22*_f(future.get("travel_adaptability_support_score")) + .08*short + .08*long + .08*international)

    if international >= .66 and long >= .60:
        pattern = "international_and_long_distance_emphasis"
    elif work_study >= .66:
        pattern = "work_or_study_travel_emphasis"
    elif mobility >= .66 and short >= .58:
        pattern = "recurring_mobility_emphasis"
    else:
        pattern = "balanced_travel_mobility_pattern"

    present_overall = _f(present.get("overall_activation_score")); future_overall = _f(future.get("overall_activation_score"))
    if future_overall > present_overall + .08:
        direction = "travel_activation_strengthening"
    elif _f(future.get("international_support_score")) >= .60:
        direction = "international_exposure_emphasis"
    elif _f(future.get("work_study_travel_support_score")) >= .60:
        direction = "work_or_study_travel_emphasis"
    elif _f(future.get("recurring_mobility_support_score")) >= .60:
        direction = "recurring_mobility_emphasis"
    else:
        direction = "broadly_steady_travel_pattern"

    return {
        "available": True, "event": "travel_journeys_trajectory", "model_version": "v1", "reference_moment": reference_moment.isoformat(),
        "short_journey_score": short, "long_distance_score": long, "international_exposure_score": international,
        "work_study_travel_score": work_study, "recurring_mobility_score": mobility, "travel_adaptability_score": adaptability,
        "trajectory_pattern": pattern, "near_term_direction": direction,
        "timing_available": bool(timing.get("available")), "events_available": bool(events.get("available")),
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known travel history overrides symbolic trajectory assumptions. Astrology must not manufacture trips, destinations, visa outcomes, relocation, settlement, accidents or travel disruptions."},
        "answer": f"The longer-term Travel & Journeys trajectory is {pattern.replace('_', ' ')}, with a near-term direction of {direction.replace('_', ' ')}.",
        "limitation": "This trajectory cannot guarantee travel, identify an exact destination, predict visa/immigration approval, infer permanent relocation or settlement, or predict travel safety, accidents, delays or disruptions.",
        "components": {"natal": natal, "timing": timing, "events": events},
    }
