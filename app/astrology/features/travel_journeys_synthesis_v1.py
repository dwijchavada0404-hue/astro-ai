from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.travel_journeys_event_intelligence_v1 import analyze_travel_journeys_event_intelligence_v1
from app.astrology.features.travel_journeys_reasoning_v1 import analyze_travel_journeys_v1
from app.astrology.features.travel_journeys_timing_v1 import analyze_travel_journeys_timing_v1
from app.astrology.features.travel_journeys_trajectory_v1 import analyze_travel_journeys_trajectory_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_travel_journeys_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Combine Travel & Journeys natal, timing, event and trajectory signals."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")
    natal = analyze_travel_journeys_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "travel_journeys_synthesis", "model_version": "v1", "reason": "Travel & Journeys natal foundation is unavailable."}
    timing = analyze_travel_journeys_timing_v1(chart, reference_moment)
    events = analyze_travel_journeys_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_travel_journeys_trajectory_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    short = _b(.44*_f(themes.get("short_journeys")) + .18*_f(future.get("short_journey_support_score")) + .28*_f(trajectory.get("short_journey_score")) + .10*_f(themes.get("recurring_mobility")))
    long = _b(.44*_f(themes.get("long_distance_travel")) + .18*_f(future.get("long_distance_support_score")) + .28*_f(trajectory.get("long_distance_score")) + .10*_f(themes.get("international_exposure")))
    international = _b(.44*_f(themes.get("international_exposure")) + .18*_f(future.get("international_support_score")) + .28*_f(trajectory.get("international_exposure_score")) + .10*_f(themes.get("long_distance_travel")))
    work_study = _b(.44*_f(themes.get("work_study_travel")) + .18*_f(future.get("work_study_travel_support_score")) + .28*_f(trajectory.get("work_study_travel_score")) + .10*_f(themes.get("travel_adaptability")))
    mobility = _b(.44*_f(themes.get("recurring_mobility")) + .18*_f(future.get("recurring_mobility_support_score")) + .28*_f(trajectory.get("recurring_mobility_score")) + .10*_f(themes.get("short_journeys")))
    adaptability = _b(.42*_f(themes.get("travel_adaptability")) + .18*_f(future.get("travel_adaptability_support_score")) + .30*_f(trajectory.get("travel_adaptability_score")) + .10*((short+long+international)/3))
    scores = {"short_journeys": short, "long_distance_travel": long, "international_exposure": international, "work_study_travel": work_study, "recurring_mobility": mobility, "travel_adaptability": adaptability}
    strongest = max(scores.items(), key=lambda item: item[1])
    if international >= .66 and long >= .60:
        outlook = "international_and_long_distance_emphasis"
    elif work_study >= .66:
        outlook = "work_or_study_travel_emphasis"
    elif mobility >= .66 and short >= .58:
        outlook = "recurring_mobility_emphasis"
    else:
        outlook = "balanced_travel_journeys_development"
    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _b(.40 + .30*coverage + .18*strongest[1] + .12*adaptability)
    return {
        "available": True, "event": "travel_journeys_synthesis", "model_version": "v1", "reference_moment": reference_moment.isoformat(),
        "outlook": outlook, "confidence": confidence, "component_coverage": round(coverage, 3), "scores": scores,
        "strongest_area": strongest[0], "strongest_area_score": strongest[1],
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None,
        "strongest_future_period": future or None,
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known travel history overrides predictive assumptions. Historical astrology may interpret confirmed travel periods but must never manufacture trips, destinations, visa outcomes, relocation, settlement, accidents or disruptions."},
        "answer": f"The combined Travel & Journeys outlook is {outlook.replace('_', ' ')}. It describes symbolic mobility themes rather than guaranteed trips or destinations.",
        "limitation": "This synthesis cannot guarantee travel, identify an exact destination, predict visa/immigration approval, infer permanent relocation or settlement, or predict travel safety, accidents, delays or disruptions.",
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
