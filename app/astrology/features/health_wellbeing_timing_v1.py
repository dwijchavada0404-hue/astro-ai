from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.health_wellbeing_reasoning_v1 import analyze_health_wellbeing_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _iso(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _score(period: dict[str, Any], natal: dict[str, Any]) -> dict[str, Any]:
    t = _d(natal.get("theme_scores")); lords = {str(period.get("major_lord") or ""), str(period.get("sub_lord") or "")}
    vitality = _b(.48*float(t.get("vitality_energy") or 0) + .18*bool(lords & {"Sun", "Mars"}) + .08*bool(lords & {"Jupiter"}))
    routine = _b(.48*float(t.get("routine_discipline") or 0) + .18*bool(lords & {"Saturn", "Mercury"}) + .08*bool(lords & {"Mars"}))
    recovery = _b(.48*float(t.get("recovery_resilience") or 0) + .16*bool(lords & {"Jupiter", "Mars"}) + .10*bool(lords & {"Saturn"}))
    stress = _b(.48*float(t.get("stress_balance") or 0) + .16*bool(lords & {"Moon", "Mercury"}) + .10*bool(lords & {"Saturn"}))
    rest = _b(.48*float(t.get("rest_restoration") or 0) + .18*bool(lords & {"Moon", "Venus"}) + .08*bool(lords & {"Jupiter"}))
    selfcare = _b(.48*float(t.get("preventive_self_care") or 0) + .16*bool(lords & {"Jupiter", "Mercury"}) + .10*bool(lords & {"Saturn"}))
    return {**period, "vitality_support_score": vitality, "routine_support_score": routine, "recovery_support_score": recovery, "stress_balance_support_score": stress, "rest_support_score": rest, "self_care_support_score": selfcare, "overall_activation_score": _b((vitality+routine+recovery+stress+rest+selfcare)/6)}


def analyze_health_wellbeing_timing_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Evaluate symbolic wellbeing timing without medical prediction."""
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")
    natal = analyze_health_wellbeing_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "health_wellbeing_timing", "model_version": "v1", "reason": "Health & Wellbeing natal foundation is unavailable."}
    raw = chart.get("dasha_periods")
    if not isinstance(raw, list) or not raw:
        return {"available": False, "event": "health_wellbeing_timing", "model_version": "v1", "reason": "Dasha periods are required for timing intelligence.", "natal": natal}
    scored = []
    for item in raw:
        if not isinstance(item, dict): continue
        start, end = _iso(item.get("start")), _iso(item.get("end"))
        if start is None or end is None or start.tzinfo is None or end.tzinfo is None: continue
        scored.append(_score({**item, "start": start.isoformat(), "end": end.isoformat()}, natal))
    past = [p for p in scored if _iso(p["end"]) <= reference_moment]
    present = [p for p in scored if _iso(p["start"]) <= reference_moment < _iso(p["end"])]
    future = [p for p in scored if _iso(p["start"]) > reference_moment]
    strongest = lambda periods: max(periods, key=lambda p: p["overall_activation_score"]) if periods else None
    return {"available": True, "event": "health_wellbeing_timing", "model_version": "v1", "reference_moment": reference_moment.isoformat(), "past": {"strongest_period": strongest(past), "historical_status": "unconfirmed"}, "present": {"active_period": strongest(present)}, "future": {"strongest_period": strongest(future)}, "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known symptoms, diagnoses, medical history and clinician advice override astrology. Past symbolic wellbeing activation is not evidence that illness, injury, diagnosis or recovery occurred."}, "limitation": "Timing scores describe symbolic wellbeing emphasis, not medical risk or probability. They cannot predict disease, diagnosis, prognosis, lifespan, death, accidents, treatment response or recovery outcomes.", "natal": natal}
