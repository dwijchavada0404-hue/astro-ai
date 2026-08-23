from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.legal_disputes_conflict_reasoning_v1 import analyze_legal_disputes_conflict_v1


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


def _score_period(period: dict[str, Any], natal: dict[str, Any]) -> dict[str, Any]:
    themes = _d(natal.get("theme_scores"))
    lords = {str(period.get("major_lord") or ""), str(period.get("sub_lord") or "")}

    dispute = _b(0.48*float(themes.get("dispute_engagement") or 0) + 0.18*bool(lords & {"Mars", "Saturn"}) + 0.08*bool(lords & {"Rahu"}))
    negotiation = _b(0.48*float(themes.get("negotiation_mediation") or 0) + 0.18*bool(lords & {"Mercury", "Venus"}) + 0.10*bool(lords & {"Jupiter"}))
    complexity = _b(0.48*float(themes.get("complexity_endurance") or 0) + 0.18*bool(lords & {"Saturn", "Rahu", "Ketu"}) + 0.08*bool(lords & {"Mars"}))
    principles = _b(0.48*float(themes.get("principles_fairness") or 0) + 0.18*bool(lords & {"Jupiter", "Sun"}) + 0.08*bool(lords & {"Mercury"}))
    competition = _b(0.48*float(themes.get("competition_assertiveness") or 0) + 0.18*bool(lords & {"Mars", "Sun"}) + 0.08*bool(lords & {"Saturn"}))
    resolution = _b(0.48*float(themes.get("resolution_capacity") or 0) + 0.18*bool(lords & {"Jupiter", "Mercury"}) + 0.08*bool(lords & {"Venus"}))

    return {
        **period,
        "dispute_activation_score": dispute,
        "negotiation_support_score": negotiation,
        "complexity_endurance_score": complexity,
        "principles_fairness_score": principles,
        "competition_assertiveness_score": competition,
        "resolution_support_score": resolution,
        "overall_activation_score": _b((dispute + negotiation + complexity + principles + competition + resolution) / 6),
    }


def analyze_legal_disputes_conflict_timing_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Evaluate symbolic dispute/conflict-management timing without predicting legal outcomes."""
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_legal_disputes_conflict_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "legal_disputes_conflict_timing", "model_version": "v1", "reason": "Legal, Disputes & Conflict natal foundation is unavailable."}

    raw = chart.get("dasha_periods")
    if not isinstance(raw, list) or not raw:
        return {"available": False, "event": "legal_disputes_conflict_timing", "model_version": "v1", "reason": "Dasha periods are required for timing intelligence.", "natal": natal}

    scored: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        start, end = _iso(item.get("start")), _iso(item.get("end"))
        if start is None or end is None or start.tzinfo is None or end.tzinfo is None:
            continue
        scored.append(_score_period({**item, "start": start.isoformat(), "end": end.isoformat()}, natal))

    past = [p for p in scored if _iso(p["end"]) <= reference_moment]
    present = [p for p in scored if _iso(p["start"]) <= reference_moment < _iso(p["end"])]
    future = [p for p in scored if _iso(p["start"]) > reference_moment]
    strongest = lambda periods: max(periods, key=lambda p: p["overall_activation_score"]) if periods else None

    return {
        "available": True,
        "event": "legal_disputes_conflict_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"strongest_period": strongest(past), "historical_status": "unconfirmed"},
        "present": {"active_period": strongest(present)},
        "future": {"strongest_period": strongest(future)},
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "Known legal history and real outcomes override astrology. Past symbolic activation is not proof that a dispute, litigation, arrest, liability finding, judgment or settlement occurred.",
        },
        "limitation": "Timing scores describe symbolic conflict-management emphasis, not legal probability. They cannot predict guilt, liability, court verdicts, arrest, imprisonment, criminal outcomes, regulatory action, exact dispute outcomes or settlement amounts.",
        "natal": natal,
    }
