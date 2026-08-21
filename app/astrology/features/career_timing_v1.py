from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1


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


def _house_lord(chart: dict[str, Any], house_no: int) -> str | None:
    houses = _safe_dict(chart.get("houses"))
    house = _safe_dict(houses.get(str(house_no)) or houses.get(house_no))
    lord = house.get("lord")
    return lord if isinstance(lord, str) and lord else None


def _career_lords(chart: dict[str, Any]) -> dict[str, float]:
    """Return career-relevant lords with stronger weight on core work houses."""
    weights = {
        10: 1.0,
        6: 0.8,
        11: 0.7,
        2: 0.6,
        9: 0.55,
        3: 0.45,
        7: 0.45,
        1: 0.4,
        12: 0.3,
    }
    result: dict[str, float] = {}
    for house_no, weight in weights.items():
        lord = _house_lord(chart, house_no)
        if lord:
            result[lord] = max(result.get(lord, 0.0), weight)
    return result


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
    """Normalize supported flat and nested Vimshottari structures."""
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
                normalized_md = dict(md_raw)
                normalized_md["major_lord"] = major
                _append_period(periods, normalized_md, reference_moment)

    return periods


def _period_score(
    period: dict[str, Any],
    career_lords: dict[str, float],
    natal_score: float,
) -> tuple[float, float, list[dict[str, Any]]]:
    """Score professional support and transition intensity separately."""
    support = 0.18 + natal_score * 0.30
    transition = 0.10
    evidence: list[dict[str, Any]] = []

    major = str(period.get("major_lord") or period.get("mahadasha") or period.get("lord") or "")
    sub = str(period.get("sub_lord") or period.get("antardasha") or "")

    for role, lord, base_weight in (("major", major, 0.30), ("sub", sub, 0.20)):
        lord_weight = career_lords.get(lord, 0.0)
        if lord_weight:
            increment = base_weight * lord_weight
            support += increment
            evidence.append({
                "rule": "career_house_lord_activation",
                "role": role,
                "planet": lord,
                "strength": round(increment, 3),
            })

        if lord in {"Sun", "Saturn", "Mercury", "Jupiter", "Mars"}:
            increment = base_weight * 0.18
            support += increment
            evidence.append({
                "rule": "career_significator_activation",
                "role": role,
                "planet": lord,
                "strength": round(increment, 3),
            })

        if lord in {"Rahu", "Ketu", "Mars", "Saturn"}:
            increment = base_weight * 0.42
            transition += increment
            evidence.append({
                "rule": "career_transition_activation",
                "role": role,
                "planet": lord,
                "strength": round(increment, 3),
            })

        if lord in career_lords and career_lords[lord] >= 0.7:
            transition += base_weight * 0.22

    return round(min(1.0, support), 3), round(min(1.0, transition), 3), evidence


def _best_period(
    periods: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    career_lords: dict[str, float],
    natal_score: float,
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        period_start = period["start_dt"]
        period_end = period["end_dt"]
        if period_end < start or period_start > end:
            continue
        support, transition, evidence = _period_score(period, career_lords, natal_score)
        candidates.append({
            "start": max(period_start, start).isoformat(),
            "end": min(period_end, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "career_support_score": support,
            "transition_score": transition,
            "evidence": evidence,
        })
    return max(candidates, key=lambda item: (item["career_support_score"], item["transition_score"]), default=None)


def analyze_career_timing_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 5,
    lookahead_years: int = 5,
) -> dict[str, Any]:
    """Compare symbolic career timing across past, present and future periods.

    Historical windows are deliberately non-assertive: a strong past period may be
    described as a period astrologically supportive of professional transition or
    advancement, but it is never treated as proof that a real-world event occurred.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_career_profession_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "career_timing",
            "model_version": "v1",
            "reason": "Career natal foundation is unavailable.",
        }

    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {
            "available": False,
            "event": "career_timing",
            "model_version": "v1",
            "reason": "No usable dasha periods are available for career timing analysis.",
            "natal": natal,
        }

    lords = _career_lords(chart)
    natal_score = float(natal.get("dominant_score") or 0.0)
    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), lords, natal_score)
    present = _best_period(periods, reference_moment, reference_moment, lords, natal_score)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, lords, natal_score)

    comparison = None
    if past and future:
        delta = round(float(future["career_support_score"]) - float(past["career_support_score"]), 3)
        comparison = {
            "future_minus_past": delta,
            "result": "future_stronger" if delta > 0.05 else "past_stronger" if delta < -0.05 else "similar_strength",
        }

    historical_validation = {
        "status": "unconfirmed",
        "rule": "Astrology may identify a past professional transition or advancement window, but must not claim that an event occurred unless the user confirms it.",
        "past_window_interpretation": (
            "This past period can be treated as a symbolic professional activation window for comparison with known history."
            if past
            else None
        ),
    }

    return {
        "available": bool(past or present or future),
        "event": "career_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future},
        "comparison": comparison,
        "historical_validation": historical_validation,
        "natal_career_theme": natal.get("dominant_theme"),
        "natal_career_score": natal_score,
        "answer": (
            "Career timing is compared across recent history, the current period and upcoming years. "
            "High-scoring periods indicate stronger symbolic professional activation, not guaranteed career events."
        ),
        "limitation": (
            "This is astrological timing analysis only. It does not establish that a past event happened and does not "
            "guarantee promotion, employment, job change, business success, income, recognition or any future outcome."
        ),
    }
