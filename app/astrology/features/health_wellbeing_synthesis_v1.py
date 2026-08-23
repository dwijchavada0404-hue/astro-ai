from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.health_wellbeing_event_intelligence_v1 import analyze_health_wellbeing_event_intelligence_v1
from app.astrology.features.health_wellbeing_reasoning_v1 import analyze_health_wellbeing_v1
from app.astrology.features.health_wellbeing_timing_v1 import analyze_health_wellbeing_timing_v1
from app.astrology.features.health_wellbeing_trajectory_v1 import analyze_health_wellbeing_trajectory_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_health_wellbeing_synthesis_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Combine symbolic wellbeing signals while preserving strict medical boundaries."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_health_wellbeing_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "health_wellbeing_synthesis", "model_version": "v1", "reason": "Health & Wellbeing natal foundation is unavailable."}

    timing = analyze_health_wellbeing_timing_v1(chart, reference_moment)
    events = analyze_health_wellbeing_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_health_wellbeing_trajectory_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    energy = _b(.44*_f(themes.get("vitality_energy")) + .18*_f(future.get("vitality_support_score")) + .28*_f(trajectory.get("energy_management_score")) + .10*_f(themes.get("stress_balance")))
    routine = _b(.44*_f(themes.get("routine_discipline")) + .18*_f(future.get("routine_support_score")) + .28*_f(trajectory.get("routine_consistency_score")) + .10*_f(themes.get("preventive_self_care")))
    resilience = _b(.44*_f(themes.get("recovery_resilience")) + .18*_f(future.get("recovery_support_score")) + .28*_f(trajectory.get("resilience_habits_score")) + .10*_f(themes.get("rest_restoration")))
    balance = _b(.44*_f(themes.get("stress_balance")) + .18*_f(future.get("stress_balance_support_score")) + .28*_f(trajectory.get("stress_balance_score")) + .10*_f(themes.get("rest_restoration")))
    rest = _b(.44*_f(themes.get("rest_restoration")) + .18*_f(future.get("rest_support_score")) + .28*_f(trajectory.get("rest_restoration_score")) + .10*_f(themes.get("stress_balance")))
    self_care = _b(.44*_f(themes.get("preventive_self_care")) + .18*_f(future.get("self_care_support_score")) + .28*_f(trajectory.get("preventive_self_care_score")) + .10*_f(themes.get("routine_discipline")))
    adaptability = _b(.18*energy + .20*routine + .20*resilience + .16*balance + .14*rest + .12*self_care)

    scores = {
        "energy_management": energy,
        "routine_consistency": routine,
        "resilience_habits": resilience,
        "stress_balance": balance,
        "rest_restoration": rest,
        "preventive_self_care": self_care,
        "adaptability": adaptability,
    }
    strongest = max(scores.items(), key=lambda item: item[1])

    if routine >= .66 and self_care >= .60:
        outlook = "routine_and_preventive_self_care_emphasis"
    elif resilience >= .66 and balance >= .60:
        outlook = "resilience_and_stress_balance_emphasis"
    elif rest >= .66:
        outlook = "rest_and_restoration_emphasis"
    elif energy >= .66:
        outlook = "energy_management_emphasis"
    else:
        outlook = "balanced_wellbeing_development"

    coverage = sum(bool(item.get("available")) for item in (natal, timing, events, trajectory)) / 4.0
    confidence = _b(.40 + .30*coverage + .18*strongest[1] + .12*adaptability)

    return {
        "available": True,
        "event": "health_wellbeing_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "outlook": outlook,
        "confidence": confidence,
        "component_coverage": round(coverage, 3),
        "scores": scores,
        "strongest_area": strongest[0],
        "strongest_area_score": strongest[1],
        "strongest_future_event": events.get("strongest_future_event") if events.get("available") else None,
        "strongest_future_period": future or None,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known symptoms, diagnoses, medical history, treatment and clinician advice override astrology. Historical astrology may interpret confirmed lifestyle periods but must never manufacture illness, injury, diagnosis, treatment response or recovery events.",
        },
        "answer": f"The combined Health & Wellbeing outlook is {outlook.replace('_', ' ')}. It describes symbolic lifestyle and self-care themes rather than medical facts or outcomes.",
        "limitation": "This synthesis is non-medical. It cannot diagnose or predict disease, illness, injury, prognosis, lifespan, death, accidents, fertility, treatment response or recovery outcomes, and it cannot recommend medication, tests, procedures, supplements or changes to professional care.",
        "components": {"natal": natal, "timing": timing, "events": events, "trajectory": trajectory},
    }
