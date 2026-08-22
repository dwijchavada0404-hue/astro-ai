from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.property_home_timing_v1 import _collect_periods, _house_lords, _period_lords
from app.astrology.features.siblings_communication_reasoning_v1 import analyze_siblings_communication_v1


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _period_scores(period: dict[str, Any], sibling_lords: set[str], communication_lords: set[str], initiative_lords: set[str], collaboration_lords: set[str], natal: dict[str, Any]) -> tuple[float, float, float, float]:
    themes = natal.get("theme_scores") if isinstance(natal.get("theme_scores"), dict) else {}
    major, sub = _period_lords(period)
    sibling = 0.12 + float(themes.get("sibling_bond") or 0.0) * 0.34
    communication = 0.12 + max(float(themes.get("communication_expression") or 0.0), float(themes.get("learning_skills") or 0.0)) * 0.34
    initiative = 0.10 + max(float(themes.get("initiative_courage") or 0.0), float(themes.get("boundaries_competition") or 0.0)) * 0.34
    collaboration = 0.10 + float(themes.get("collaboration") or 0.0) * 0.36
    for lord, primary in ((major, 0.26), (sub, 0.17)):
        if lord in sibling_lords:
            sibling += primary
        if lord in communication_lords:
            communication += primary
        if lord in initiative_lords:
            initiative += primary
        if lord in collaboration_lords:
            collaboration += primary
        if lord in {"Mercury", "Moon", "Jupiter", "Venus"}:
            sibling += primary * 0.10
        if lord in {"Mercury", "Jupiter"}:
            communication += primary * 0.18
        if lord in {"Mars", "Sun", "Saturn"}:
            initiative += primary * 0.16
        if lord in {"Mercury", "Venus", "Jupiter"}:
            collaboration += primary * 0.14
    return _bounded(sibling), _bounded(communication), _bounded(initiative), _bounded(collaboration)


def _best_period(periods: list[dict[str, Any]], start: datetime, end: datetime, sibling_lords: set[str], communication_lords: set[str], initiative_lords: set[str], collaboration_lords: set[str], natal: dict[str, Any]) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps, pe = period["start_dt"], period["end_dt"]
        if pe < start or ps > end:
            continue
        sibling, communication, initiative, collaboration = _period_scores(period, sibling_lords, communication_lords, initiative_lords, collaboration_lords, natal)
        candidates.append({
            "start": max(ps, start).isoformat(), "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "sibling_relationship_support_score": sibling,
            "communication_learning_support_score": communication,
            "initiative_boundary_support_score": initiative,
            "collaboration_support_score": collaboration,
        })
    return max(candidates, key=lambda item: max(item["sibling_relationship_support_score"], item["communication_learning_support_score"], item["initiative_boundary_support_score"], item["collaboration_support_score"]), default=None)


def analyze_siblings_communication_timing_v1(chart: dict[str, Any], reference_moment: datetime, lookback_years: int = 5, lookahead_years: int = 7) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_siblings_communication_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "siblings_communication_timing", "model_version": "v1", "reason": "Siblings & Communication natal foundation is unavailable."}
    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {"available": False, "event": "siblings_communication_timing", "model_version": "v1", "reason": "No usable dasha periods are available for Siblings & Communication timing.", "natal": natal}

    sibling_lords = _house_lords(chart, (3, 11))
    communication_lords = _house_lords(chart, (2, 3, 5))
    initiative_lords = _house_lords(chart, (1, 3, 6))
    collaboration_lords = _house_lords(chart, (3, 7, 11))
    args = (sibling_lords, communication_lords, initiative_lords, collaboration_lords, natal)
    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)
    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), *args)
    present = _best_period(periods, reference_moment, reference_moment, *args)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, *args)
    return {
        "available": bool(past or present or future), "event": "siblings_communication_timing", "model_version": "v1", "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past, "historical_status": "unconfirmed" if past else None},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future}, "natal": natal,
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Past activation is not proof that a sibling event, conflict, reconciliation, communication milestone or collaboration event occurred. Known relationship and communication history overrides astrology."},
        "answer": "Siblings & Communication timing compares symbolic sibling/peer, communication/learning, initiative/boundary and collaboration activation across past, present and future dasha periods.",
        "limitation": "Timing activation is not a probability or guarantee of sibling closeness, conflict, estrangement, reconciliation, communication success, exam/learning outcomes or collaboration results. It cannot identify a specific person's intentions or loyalty.",
    }
