from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _parse_dt(value: Any, tzinfo) -> datetime | None:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return None
    else:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    return dt


def _wealth_lords(chart: dict[str, Any]) -> set[str]:
    houses = _safe_dict(chart.get("houses"))
    lords: set[str] = set()
    for number in (2, 5, 8, 9, 10, 11):
        h = _safe_dict(houses.get(str(number)) or houses.get(number))
        lord = h.get("lord")
        if isinstance(lord, str) and lord:
            lords.add(lord)
    return lords


def _period_score(period: dict[str, Any], wealth_lords: set[str], natal_score: float) -> float:
    score = 0.25 + natal_score * 0.35
    major = str(period.get("major_lord") or period.get("mahadasha") or period.get("lord") or "")
    sub = str(period.get("sub_lord") or period.get("antardasha") or "")
    for lord, weight in ((major, 0.28), (sub, 0.18)):
        if lord in wealth_lords:
            score += weight
        if lord in {"Jupiter", "Venus", "Mercury", "Saturn"}:
            score += weight * 0.55
    return round(min(1.0, score), 3)


def _append_period(
    periods: list[dict[str, Any]],
    raw: dict[str, Any],
    reference_moment: datetime,
    major_lord: str | None = None,
) -> None:
    start = _parse_dt(raw.get("start"), reference_moment.tzinfo)
    end = _parse_dt(raw.get("end"), reference_moment.tzinfo)
    if not start or not end or end <= start:
        return
    enriched = dict(raw)
    enriched["start_dt"] = start
    enriched["end_dt"] = end
    if major_lord and not enriched.get("major_lord") and not enriched.get("mahadasha"):
        enriched["major_lord"] = major_lord
    periods.append(enriched)


def _collect_periods(chart: dict[str, Any], reference_moment: datetime) -> list[dict[str, Any]]:
    """Normalize flat or nested Vimshottari structures into timing periods."""
    periods: list[dict[str, Any]] = []

    # Legacy/flat structures.
    for key in ("dasha_periods", "vimshottari"):
        for item in _safe_list(chart.get(key)):
            if isinstance(item, dict):
                _append_period(periods, item, reference_moment)

    # Production chart structure: dashas -> mahadashas -> antardashas.
    dashas = chart.get("dashas")
    if isinstance(dashas, list):
        for item in dashas:
            if isinstance(item, dict):
                _append_period(periods, item, reference_moment)
    elif isinstance(dashas, dict):
        for md_raw in _safe_list(dashas.get("mahadashas")):
            if not isinstance(md_raw, dict):
                continue
            major = md_raw.get("planet") if isinstance(md_raw.get("planet"), str) else None
            antardashas = _safe_list(md_raw.get("antardashas"))
            if antardashas:
                for ad_raw in antardashas:
                    if not isinstance(ad_raw, dict):
                        continue
                    normalized = dict(ad_raw)
                    normalized["antardasha"] = ad_raw.get("planet") or ad_raw.get("antardasha")
                    _append_period(periods, normalized, reference_moment, major_lord=major)
            else:
                normalized_md = dict(md_raw)
                normalized_md["major_lord"] = major
                _append_period(periods, normalized_md, reference_moment)

    return periods


def _best_period(
    periods: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    wealth_lords: set[str],
    natal_score: float,
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps = period["start_dt"]
        pe = period["end_dt"]
        if pe < start or ps > end:
            continue
        score = _period_score(period, wealth_lords, natal_score)
        candidates.append({
            "start": max(ps, start).isoformat(),
            "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "score": score,
        })
    return max(candidates, key=lambda item: item["score"], default=None)


def analyze_finance_timing_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 5,
    lookahead_years: int = 5,
) -> dict[str, Any]:
    """Compare past, present and future financial-support periods.

    V1 uses available dasha-period data plus natal finance strength. It does not
    treat a high score as a guarantee of income, profits, wealth or investment returns.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_finance_wealth_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "finance_timing",
            "model_version": "v1",
            "reason": "Finance natal foundation is unavailable.",
        }

    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {
            "available": False,
            "event": "finance_timing",
            "model_version": "v1",
            "reason": "No usable dasha periods are available for financial timing analysis.",
            "natal": natal,
        }

    wealth_lords = _wealth_lords(chart)
    natal_score = float(natal.get("dominant_score") or 0.0)
    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), wealth_lords, natal_score)
    present = _best_period(periods, reference_moment, reference_moment, wealth_lords, natal_score)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, wealth_lords, natal_score)

    comparison = None
    if past and future:
        delta = round(float(future["score"]) - float(past["score"]), 3)
        comparison = {
            "future_minus_past": delta,
            "result": "future_stronger" if delta > 0.05 else "past_stronger" if delta < -0.05 else "similar_strength",
        }

    return {
        "available": bool(past or present or future),
        "event": "finance_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future},
        "comparison": comparison,
        "natal_finance_theme": natal.get("dominant_theme"),
        "natal_finance_score": natal_score,
        "answer": (
            "Financial timing is being compared across the recent past, current period and upcoming years. "
            "These are symbolic support periods, not predictions of guaranteed profit or wealth."
        ),
        "limitation": (
            "This is astrological timing analysis only. It is not financial advice and does not guarantee income, "
            "returns, business success, inheritance or wealth creation."
        ),
    }
