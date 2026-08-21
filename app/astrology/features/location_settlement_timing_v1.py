from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.location_settlement_reasoning_v1 import analyze_location_settlement_v1
from app.astrology.features.property_home_timing_v1 import _collect_periods, _house_lords, _period_lords


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _period_scores(
    period: dict[str, Any],
    mobility_lords: set[str],
    foreign_lords: set[str],
    residence_lords: set[str],
    natal: dict[str, Any],
) -> tuple[float, float, float]:
    themes = natal.get("theme_scores") if isinstance(natal.get("theme_scores"), dict) else {}
    major, sub = _period_lords(period)

    relocation = 0.14 + float(themes.get("domestic_relocation") or 0.0) * 0.36
    foreign_exposure = 0.12 + float(themes.get("foreign_exposure") or 0.0) * 0.36
    settlement = 0.10 + float(themes.get("foreign_settlement") or 0.0) * 0.38

    for lord, primary in ((major, 0.26), (sub, 0.17)):
        if lord in mobility_lords:
            relocation += primary
        if lord in foreign_lords:
            foreign_exposure += primary
        if lord in residence_lords:
            settlement += primary * 0.78
        if lord in {"Rahu", "Ketu", "Saturn", "Moon"}:
            relocation += primary * 0.24
        if lord in {"Rahu", "Jupiter", "Mercury", "Saturn"}:
            foreign_exposure += primary * 0.26
        # Planetary activation alone is deliberately insufficient for settlement.
        if lord in {"Rahu", "Saturn", "Jupiter"}:
            settlement += primary * 0.12

    return _bounded(relocation), _bounded(foreign_exposure), _bounded(settlement)


def _best_period(
    periods: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    mobility_lords: set[str],
    foreign_lords: set[str],
    residence_lords: set[str],
    natal: dict[str, Any],
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps, pe = period["start_dt"], period["end_dt"]
        if pe < start or ps > end:
            continue
        relocation, exposure, settlement = _period_scores(
            period, mobility_lords, foreign_lords, residence_lords, natal
        )
        candidates.append({
            "start": max(ps, start).isoformat(),
            "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "relocation_activation_score": relocation,
            "foreign_exposure_score": exposure,
            "foreign_settlement_support_score": settlement,
        })
    return max(
        candidates,
        key=lambda item: (
            item["foreign_settlement_support_score"],
            item["foreign_exposure_score"],
            item["relocation_activation_score"],
        ),
        default=None,
    )


def analyze_location_settlement_timing_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 5,
    lookahead_years: int = 7,
) -> dict[str, Any]:
    """Compare past, present and future location/foreign-settlement activation."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_location_settlement_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "location_settlement_timing", "model_version": "v1", "reason": "Location natal foundation is unavailable."}

    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {
            "available": False,
            "event": "location_settlement_timing",
            "model_version": "v1",
            "reason": "No usable dasha periods are available for Location & Foreign Settlement timing.",
            "natal": natal,
        }

    mobility_lords = _house_lords(chart, (3, 4, 7, 9, 12))
    foreign_lords = _house_lords(chart, (7, 9, 12))
    residence_lords = _house_lords(chart, (4, 9, 12))
    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), mobility_lords, foreign_lords, residence_lords, natal)
    present = _best_period(periods, reference_moment, reference_moment, mobility_lords, foreign_lords, residence_lords, natal)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, mobility_lords, foreign_lords, residence_lords, natal)

    return {
        "available": bool(past or present or future),
        "event": "location_settlement_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past, "historical_status": "unconfirmed" if past else None},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future},
        "natal": natal,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "A past high-scoring mobility or foreign period is not proof that travel, relocation or migration occurred. Known real-world location history overrides astrology.",
        },
        "answer": "Location timing compares symbolic relocation, foreign-exposure and longer-term settlement activation across past, present and future dasha periods.",
        "limitation": (
            "Timing activation is not a probability or guarantee of travel, relocation, visa approval, immigration status, permanent residence or citizenship. "
            "Foreign exposure can manifest through work, study, travel, clients, family or temporary residence without permanent settlement."
        ),
    }
