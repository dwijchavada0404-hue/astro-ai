from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.property_home_timing_v1 import _collect_periods, _house_lords, _period_lords
from app.astrology.features.purpose_personal_growth_reasoning_v1 import analyze_purpose_personal_growth_v1


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _period_scores(period: dict[str, Any], self_lords: set[str], contribution_lords: set[str], meaning_lords: set[str], inner_lords: set[str], natal: dict[str, Any]) -> tuple[float, float, float, float]:
    themes = natal.get("theme_scores") if isinstance(natal.get("theme_scores"), dict) else {}
    major, sub = _period_lords(period)
    self_growth = 0.12 + float(themes.get("self_development") or 0.0) * 0.34
    contribution = 0.10 + max(float(themes.get("service_contribution") or 0.0), float(themes.get("public_contribution") or 0.0)) * 0.34
    meaning = 0.12 + float(themes.get("knowledge_guidance") or 0.0) * 0.34
    inner = 0.10 + float(themes.get("inner_growth") or 0.0) * 0.36

    for lord, primary in ((major, 0.26), (sub, 0.17)):
        if lord in self_lords:
            self_growth += primary
        if lord in contribution_lords:
            contribution += primary
        if lord in meaning_lords:
            meaning += primary
        if lord in inner_lords:
            inner += primary
        if lord in {"Sun", "Moon"}:
            self_growth += primary * 0.16
        if lord in {"Sun", "Saturn", "Mars", "Jupiter"}:
            contribution += primary * 0.12
        if lord in {"Jupiter", "Mercury"}:
            meaning += primary * 0.18
        if lord in {"Ketu", "Moon", "Jupiter", "Saturn"}:
            inner += primary * 0.14

    return _bounded(self_growth), _bounded(contribution), _bounded(meaning), _bounded(inner)


def _best_period(periods: list[dict[str, Any]], start: datetime, end: datetime, self_lords: set[str], contribution_lords: set[str], meaning_lords: set[str], inner_lords: set[str], natal: dict[str, Any]) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps, pe = period["start_dt"], period["end_dt"]
        if pe < start or ps > end:
            continue
        self_growth, contribution, meaning, inner = _period_scores(period, self_lords, contribution_lords, meaning_lords, inner_lords, natal)
        candidates.append({
            "start": max(ps, start).isoformat(), "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "self_growth_support_score": self_growth,
            "contribution_support_score": contribution,
            "meaning_guidance_support_score": meaning,
            "inner_growth_support_score": inner,
        })
    return max(candidates, key=lambda item: max(item["self_growth_support_score"], item["contribution_support_score"], item["meaning_guidance_support_score"], item["inner_growth_support_score"]), default=None)


def analyze_purpose_personal_growth_timing_v1(chart: dict[str, Any], reference_moment: datetime, lookback_years: int = 5, lookahead_years: int = 7) -> dict[str, Any]:
    """Compare symbolic personal-growth and contribution activation across time."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_purpose_personal_growth_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "purpose_personal_growth_timing", "model_version": "v1", "reason": "Purpose natal foundation is unavailable."}
    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {"available": False, "event": "purpose_personal_growth_timing", "model_version": "v1", "reason": "No usable dasha periods are available for Purpose & Personal Growth timing.", "natal": natal}

    self_lords = _house_lords(chart, (1, 5))
    contribution_lords = _house_lords(chart, (6, 10, 11))
    meaning_lords = _house_lords(chart, (5, 9))
    inner_lords = _house_lords(chart, (9, 12))
    args = (self_lords, contribution_lords, meaning_lords, inner_lords, natal)
    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)
    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), *args)
    present = _best_period(periods, reference_moment, reference_moment, *args)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, *args)

    return {
        "available": bool(past or present or future), "event": "purpose_personal_growth_timing", "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past, "historical_status": "unconfirmed" if past else None},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future}, "natal": natal,
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "A past high-scoring growth period is not proof that a transformation, calling, spiritual development or contribution milestone occurred. Known lived experience overrides astrology."},
        "answer": "Purpose timing compares symbolic self-growth, contribution, meaning/guidance and inner-growth activation across past, present and future dasha periods.",
        "limitation": "Timing activation is not proof of destiny, a calling, spiritual attainment, moral development, career obligation or a guaranteed life event. Personal values and choices remain primary.",
    }
