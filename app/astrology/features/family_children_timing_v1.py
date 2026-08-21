from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.family_children_reasoning_v1 import analyze_family_children_v1


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


def _family_lords(chart: dict[str, Any]) -> set[str]:
    houses = _safe_dict(chart.get("houses"))
    lords: set[str] = set()
    for number in (2, 4, 5, 9, 11):
        house = _safe_dict(houses.get(str(number)) or houses.get(number))
        lord = house.get("lord")
        if isinstance(lord, str) and lord:
            lords.add(lord)
    return lords


def _change_lords(chart: dict[str, Any]) -> set[str]:
    houses = _safe_dict(chart.get("houses"))
    lords: set[str] = set()
    for number in (4, 5, 8, 12):
        house = _safe_dict(houses.get(str(number)) or houses.get(number))
        lord = house.get("lord")
        if isinstance(lord, str) and lord:
            lords.add(lord)
    return lords


def _append_period(periods: list[dict[str, Any]], raw: dict[str, Any], reference_moment: datetime, major_lord: str | None = None) -> None:
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
    periods: list[dict[str, Any]] = []
    for key in ("dasha_periods", "vimshottari"):
        for item in _safe_list(chart.get(key)):
            if isinstance(item, dict):
                _append_period(periods, item, reference_moment)

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
                normalized = dict(md_raw)
                normalized["major_lord"] = major
                _append_period(periods, normalized, reference_moment)
    return periods


def _period_scores(period: dict[str, Any], family_lords: set[str], change_lords: set[str], natal_score: float) -> tuple[float, float]:
    support = 0.22 + 0.36 * natal_score
    change = 0.12
    major = str(period.get("major_lord") or period.get("mahadasha") or period.get("lord") or "")
    sub = str(period.get("sub_lord") or period.get("antardasha") or "")
    for lord, weight in ((major, 0.26), (sub, 0.17)):
        if lord in family_lords:
            support += weight
        if lord in {"Jupiter", "Moon", "Venus"}:
            support += weight * 0.50
        if lord in change_lords:
            change += weight * 0.70
        if lord in {"Saturn", "Rahu", "Ketu", "Mars"}:
            change += weight * 0.40
    return round(min(1.0, support), 3), round(min(1.0, change), 3)


def _best_period(periods: list[dict[str, Any]], start: datetime, end: datetime, family_lords: set[str], change_lords: set[str], natal_score: float) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps = period["start_dt"]
        pe = period["end_dt"]
        if pe < start or ps > end:
            continue
        support_score, change_score = _period_scores(period, family_lords, change_lords, natal_score)
        candidates.append({
            "start": max(ps, start).isoformat(),
            "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "family_support_score": support_score,
            "family_change_score": change_score,
        })
    return max(candidates, key=lambda item: (item["family_support_score"], item["family_change_score"]), default=None)


def analyze_family_children_timing_v1(chart: dict[str, Any], reference_moment: datetime, lookback_years: int = 5, lookahead_years: int = 5) -> dict[str, Any]:
    """Compare past, present and future symbolic Family & Children timing windows."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_family_children_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "family_children_timing", "model_version": "v1", "reason": "Family & Children natal foundation is unavailable."}

    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {
            "available": False,
            "event": "family_children_timing",
            "model_version": "v1",
            "reason": "No usable dasha periods are available for Family & Children timing analysis.",
            "natal": natal,
        }

    family_lords = _family_lords(chart)
    change_lords = _change_lords(chart)
    natal_score = float(natal.get("dominant_score") or 0.0)
    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), family_lords, change_lords, natal_score)
    present = _best_period(periods, reference_moment, reference_moment, family_lords, change_lords, natal_score)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, family_lords, change_lords, natal_score)

    return {
        "available": bool(past or present or future),
        "event": "family_children_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future},
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Past symbolic family windows may describe periods of family support, responsibility or change, but must not be "
                "presented as proof that conception, pregnancy, childbirth, adoption, parenthood or another family milestone occurred."
            ),
        },
        "answer": (
            "Family & Children timing is compared across recent past, present and upcoming years using symbolic support and change activation."
        ),
        "limitation": (
            "This is astrological timing analysis only. It is not fertility or medical advice and does not predict or guarantee "
            "conception, pregnancy, childbirth, adoption, number or sex of children, or any family outcome."
        ),
    }
