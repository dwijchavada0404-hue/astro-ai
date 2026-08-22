from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.parents_elders_reasoning_v1 import analyze_parents_elders_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _bounded(value: float) -> float:
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


def _period_score(period: dict[str, Any], natal: dict[str, Any]) -> dict[str, Any]:
    themes = _safe_dict(natal.get("theme_scores"))
    major = str(period.get("major_lord") or "")
    sub = str(period.get("sub_lord") or "")
    lords = {major, sub}
    guidance = _bounded(0.44 * float(themes.get("guidance_mentorship") or 0) + 0.20 * bool(lords & {"Jupiter", "Sun"}) + 0.10 * bool(lords & {"Moon"}))
    support = _bounded(0.44 * float(themes.get("emotional_support") or 0) + 0.18 * bool(lords & {"Moon", "Venus"}) + 0.10 * bool(lords & {"Jupiter"}))
    duty = _bounded(0.42 * float(themes.get("duty_responsibility") or 0) + 0.22 * bool(lords & {"Saturn", "Sun"}) + 0.10 * bool(lords & {"Mars"}))
    authority = _bounded(0.42 * float(themes.get("authority_structure") or 0) + 0.20 * bool(lords & {"Sun", "Saturn"}) + 0.08 * bool(lords & {"Jupiter"}))
    boundaries = _bounded(0.44 * float(themes.get("independence_boundaries") or 0) + 0.20 * bool(lords & {"Saturn", "Mars"}) + 0.08 * bool(lords & {"Rahu", "Ketu"}))
    continuity = _bounded(0.46 * float(themes.get("family_continuity") or 0) + 0.16 * bool(lords & {"Moon", "Jupiter", "Venus"}) + 0.08 * bool(lords & {"Sun"}))
    return {**period, "guidance_support_score": guidance, "emotional_support_score": support, "duty_support_score": duty, "authority_support_score": authority, "boundary_support_score": boundaries, "continuity_support_score": continuity, "overall_activation_score": _bounded((guidance + support + duty + authority + boundaries + continuity) / 6)}


def analyze_parents_elders_timing_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Evaluate past/present/future family-role activation without predicting parent/elder events."""
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")
    natal = analyze_parents_elders_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "parents_elders_timing", "model_version": "v1", "reason": "Parents & Elders natal foundation is unavailable."}
    raw = chart.get("dasha_periods")
    if not isinstance(raw, list) or not raw:
        return {"available": False, "event": "parents_elders_timing", "model_version": "v1", "reason": "Dasha periods are required for timing intelligence.", "natal": natal}
    scored = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        start, end = _iso(item.get("start")), _iso(item.get("end"))
        if start is None or end is None or start.tzinfo is None or end.tzinfo is None:
            continue
        scored.append(_period_score({**item, "start": start.isoformat(), "end": end.isoformat()}, natal))
    past = [p for p in scored if _iso(p["end"]) <= reference_moment]
    present = [p for p in scored if _iso(p["start"]) <= reference_moment < _iso(p["end"])]
    future = [p for p in scored if _iso(p["start"]) > reference_moment]
    strongest = lambda periods: max(periods, key=lambda p: p["overall_activation_score"]) if periods else None
    return {"available": True, "event": "parents_elders_timing", "model_version": "v1", "reference_moment": reference_moment.isoformat(), "past": {"strongest_period": strongest(past), "historical_status": "unconfirmed"}, "present": {"active_period": strongest(present)}, "future": {"strongest_period": strongest(future)}, "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Past family-role activation is not evidence that closeness, conflict, caregiving, illness, loss or reconciliation occurred. Known family history overrides astrology."}, "limitation": "Timing scores are symbolic activation, not probabilities. They cannot predict a parent or elder's health, illness, lifespan, death, intentions, conflict, reconciliation or caregiving outcome.", "natal": natal}
