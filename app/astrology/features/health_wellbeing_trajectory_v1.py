from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.health_wellbeing_event_intelligence_v1 import analyze_health_wellbeing_event_intelligence_v1
from app.astrology.features.health_wellbeing_reasoning_v1 import analyze_health_wellbeing_v1
from app.astrology.features.health_wellbeing_timing_v1 import analyze_health_wellbeing_timing_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_health_wellbeing_trajectory_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Synthesize longer-term symbolic wellbeing patterns without making medical claims."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_health_wellbeing_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "health_wellbeing_trajectory",
            "model_version": "v1",
            "reason": "Health & Wellbeing natal foundation is unavailable.",
        }

    timing = analyze_health_wellbeing_timing_v1(chart, reference_moment)
    events = analyze_health_wellbeing_event_intelligence_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    present = _d(_d(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    energy = _b(
        0.54 * _f(themes.get("vitality_energy"))
        + 0.22 * _f(future.get("vitality_support_score"))
        + 0.14 * _f(themes.get("stress_balance"))
        + 0.10 * _f(themes.get("routine_discipline"))
    )
    routine = _b(
        0.54 * _f(themes.get("routine_discipline"))
        + 0.22 * _f(future.get("routine_support_score"))
        + 0.14 * _f(themes.get("preventive_self_care"))
        + 0.10 * _f(themes.get("recovery_resilience"))
    )
    resilience = _b(
        0.54 * _f(themes.get("recovery_resilience"))
        + 0.22 * _f(future.get("recovery_support_score"))
        + 0.14 * _f(themes.get("routine_discipline"))
        + 0.10 * _f(themes.get("rest_restoration"))
    )
    balance = _b(
        0.54 * _f(themes.get("stress_balance"))
        + 0.22 * _f(future.get("stress_balance_support_score"))
        + 0.14 * _f(themes.get("rest_restoration"))
        + 0.10 * _f(themes.get("preventive_self_care"))
    )
    rest = _b(
        0.54 * _f(themes.get("rest_restoration"))
        + 0.22 * _f(future.get("rest_support_score"))
        + 0.14 * _f(themes.get("stress_balance"))
        + 0.10 * _f(themes.get("recovery_resilience"))
    )
    self_care = _b(
        0.54 * _f(themes.get("preventive_self_care"))
        + 0.22 * _f(future.get("self_care_support_score"))
        + 0.14 * _f(themes.get("routine_discipline"))
        + 0.10 * _f(themes.get("stress_balance"))
    )
    adaptability = _b(
        0.18 * energy
        + 0.20 * routine
        + 0.20 * resilience
        + 0.16 * balance
        + 0.14 * rest
        + 0.12 * self_care
    )

    if routine >= 0.66 and self_care >= 0.60:
        pattern = "routine_and_preventive_self_care_emphasis"
    elif resilience >= 0.66 and balance >= 0.60:
        pattern = "resilience_and_stress_balance_emphasis"
    elif rest >= 0.66:
        pattern = "rest_and_restoration_emphasis"
    elif energy >= 0.66:
        pattern = "energy_management_emphasis"
    else:
        pattern = "balanced_wellbeing_development"

    present_overall = _f(present.get("overall_activation_score"))
    future_overall = _f(future.get("overall_activation_score"))
    if future_overall > present_overall + 0.08:
        direction = "wellbeing_routine_activation_strengthening"
    elif _f(future.get("routine_support_score")) >= 0.60:
        direction = "routine_consistency_emphasis"
    elif _f(future.get("rest_support_score")) >= 0.60:
        direction = "rest_and_restoration_emphasis"
    elif _f(future.get("stress_balance_support_score")) >= 0.60:
        direction = "stress_balance_emphasis"
    else:
        direction = "broadly_steady_wellbeing_pattern"

    return {
        "available": True,
        "event": "health_wellbeing_trajectory",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "energy_management_score": energy,
        "routine_consistency_score": routine,
        "resilience_habits_score": resilience,
        "stress_balance_score": balance,
        "rest_restoration_score": rest,
        "preventive_self_care_score": self_care,
        "adaptability_score": adaptability,
        "trajectory_pattern": pattern,
        "near_term_direction": direction,
        "timing_available": bool(timing.get("available")),
        "events_available": bool(events.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known symptoms, diagnoses, medical history, treatment and clinician advice override symbolic wellbeing trajectory assumptions. "
                "Astrology must not manufacture illness, injury, diagnosis, treatment response or recovery events."
            ),
        },
        "answer": (
            f"The longer-term Health & Wellbeing trajectory is {pattern.replace('_', ' ')}, "
            f"with a near-term direction of {direction.replace('_', ' ')}."
        ),
        "limitation": (
            "This trajectory describes symbolic lifestyle themes only. It cannot diagnose or predict disease, illness, injury, prognosis, lifespan, death, accidents, "
            "treatment response or recovery outcomes, and it cannot recommend medication, tests, procedures, supplements or changes to professional care."
        ),
        "components": {"natal": natal, "timing": timing, "events": events},
    }
