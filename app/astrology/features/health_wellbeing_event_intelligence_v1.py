from __future__ import annotations

from datetime import datetime
from typing import Any

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


def _event(score: float, label: str, evidence: list[str]) -> dict[str, Any]:
    if score >= 0.72:
        level = "strong"
    elif score >= 0.56:
        level = "moderate"
    else:
        level = "developing"
    return {
        "score": _b(score),
        "activation": level,
        "label": label,
        "evidence": evidence,
        "status": "symbolic_theme_only",
    }


def analyze_health_wellbeing_event_intelligence_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Translate wellbeing timing into non-medical lifestyle-theme activations.

    These are reflective themes such as routine, pacing, rest and resilience. They are
    deliberately not illness, diagnosis, injury, treatment or recovery predictions.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_health_wellbeing_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "health_wellbeing_events",
            "model_version": "v1",
            "reason": "Health & Wellbeing natal foundation is unavailable.",
        }

    timing = analyze_health_wellbeing_timing_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    present = _d(_d(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    def blended(theme: str, timing_key: str, extra_theme: str | None = None) -> float:
        base = 0.58 * _f(themes.get(theme))
        present_component = 0.14 * _f(present.get(timing_key))
        future_component = 0.20 * _f(future.get(timing_key))
        extra = 0.08 * _f(themes.get(extra_theme)) if extra_theme else 0.0
        return _b(base + present_component + future_component + extra)

    events = {
        "energy_pacing_focus": _event(
            blended("vitality_energy", "vitality_support_score", "stress_balance"),
            "energy management and sustainable pacing",
            ["vitality_energy", "stress_balance", "vitality_timing"],
        ),
        "routine_reset_focus": _event(
            blended("routine_discipline", "routine_support_score", "preventive_self_care"),
            "routine consistency and daily maintenance",
            ["routine_discipline", "preventive_self_care", "routine_timing"],
        ),
        "resilience_development_focus": _event(
            blended("recovery_resilience", "recovery_support_score", "routine_discipline"),
            "resilience, adaptation and sustainable recovery habits",
            ["recovery_resilience", "routine_discipline", "recovery_timing"],
        ),
        "stress_balance_focus": _event(
            blended("stress_balance", "stress_balance_support_score", "rest_restoration"),
            "pressure management and emotional pacing",
            ["stress_balance", "rest_restoration", "stress_balance_timing"],
        ),
        "rest_restoration_focus": _event(
            blended("rest_restoration", "rest_support_score", "stress_balance"),
            "rest, restoration and retreat",
            ["rest_restoration", "stress_balance", "rest_timing"],
        ),
        "preventive_self_care_focus": _event(
            blended("preventive_self_care", "self_care_support_score", "routine_discipline"),
            "preventive self-care and moderation",
            ["preventive_self_care", "routine_discipline", "self_care_timing"],
        ),
    }

    strongest_key, strongest_event = max(events.items(), key=lambda item: item[1]["score"])
    return {
        "available": True,
        "event": "health_wellbeing_events",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_event": strongest_key,
        "strongest_event_score": strongest_event["score"],
        "strongest_future_event": strongest_key if future else None,
        "answer": (
            f"The strongest current Health & Wellbeing theme is {strongest_event['label']}. "
            "This is a reflective lifestyle emphasis, not a medical prediction."
        ),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known symptoms, diagnoses, medical history, treatment and clinician advice override astrology. "
                "Symbolic wellbeing themes must never be treated as evidence that illness, injury, diagnosis, treatment response or recovery occurred."
            ),
        },
        "limitation": (
            "Event scores describe symbolic emphasis on routines, pacing, rest, resilience and self-care. "
            "They cannot diagnose or predict disease, illness, injury, prognosis, lifespan, death, accidents, treatment response or recovery outcomes, "
            "and they cannot recommend medication, tests, procedures, supplements or changes to professional care."
        ),
        "components": {"natal": natal, "timing": timing},
    }
