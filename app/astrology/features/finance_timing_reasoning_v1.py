from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1


FINANCE_HOUSES = {2, 5, 8, 9, 11}
SUPPORTIVE_HOUSES = {2, 5, 9, 10, 11}
CHALLENGING_HOUSES = {6, 8, 12}
FINANCE_SIGNIFICATORS = {"Jupiter", "Venus", "Mercury", "Saturn"}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _wealth_lords(chart: dict[str, Any]) -> set[str]:
    houses = _safe_dict(chart.get("houses"))
    lords: set[str] = set()
    for number in FINANCE_HOUSES:
        house = _safe_dict(houses.get(str(number)) or houses.get(number))
        lord = house.get("lord")
        if isinstance(lord, str) and lord:
            lords.add(lord)
    return lords


def _extract_dasha(chart: dict[str, Any], moment: datetime) -> tuple[str | None, str | None]:
    """Best-effort extraction from chart-supplied dasha periods.

    Supports a small set of common shapes used elsewhere in AstroAI fixtures.
    Missing dasha data is treated as neutral rather than an error.
    """
    periods = (
        _safe_list(chart.get("dasha_periods"))
        or _safe_list(chart.get("dashas"))
        or _safe_list(_safe_dict(chart.get("dasha")).get("periods"))
    )

    for period in periods:
        if not isinstance(period, dict):
            continue
        start_raw = period.get("start") or period.get("start_date")
        end_raw = period.get("end") or period.get("end_date")
        try:
            start = datetime.fromisoformat(str(start_raw))
            end = datetime.fromisoformat(str(end_raw))
        except (TypeError, ValueError):
            continue
        if start.tzinfo is None:
            start = start.replace(tzinfo=moment.tzinfo)
        if end.tzinfo is None:
            end = end.replace(tzinfo=moment.tzinfo)
        if start <= moment <= end:
            major = period.get("major") or period.get("mahadasha") or period.get("lord")
            sub = period.get("sub") or period.get("antardasha") or period.get("sub_lord")
            return (
                str(major) if isinstance(major, str) else None,
                str(sub) if isinstance(sub, str) else None,
            )
    return None, None


def _transit_score(chart: dict[str, Any], moment: datetime) -> tuple[float, list[dict[str, Any]]]:
    """Use chart-provided transit snapshots when available.

    Finance V1 intentionally avoids fabricating planetary positions. If a transit
    provider has populated snapshots keyed by ISO date/year, those placements are
    scored; otherwise this component contributes a neutral score of 0.5.
    """
    snapshots = _safe_dict(chart.get("transit_snapshots"))
    keys = (moment.date().isoformat(), str(moment.year))
    snapshot: dict[str, Any] = {}
    for key in keys:
        candidate = _safe_dict(snapshots.get(key))
        if candidate:
            snapshot = candidate
            break

    if not snapshot:
        return 0.5, [{"rule": "transit_data_unavailable", "score": 0.5}]

    score = 0.0
    evidence: list[dict[str, Any]] = []
    for planet in ("Jupiter", "Venus", "Mercury", "Saturn"):
        placement = _safe_dict(snapshot.get(planet))
        try:
            house = int(placement.get("house"))
        except (TypeError, ValueError):
            continue
        if house in SUPPORTIVE_HOUSES:
            score += 0.2
            evidence.append({"rule": "supportive_finance_transit", "planet": planet, "house": house})
        elif house in CHALLENGING_HOUSES:
            score += 0.07
            evidence.append({"rule": "complex_finance_transit", "planet": planet, "house": house})
    return round(min(1.0, score), 3), evidence


def score_finance_moment_v1(chart: dict[str, Any], moment: datetime) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(moment, datetime):
        raise ValueError("moment must be a datetime.")
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("moment must include a timezone offset.")

    natal = analyze_finance_wealth_v1(chart)
    if not natal.get("available"):
        return {"available": False, "reason": natal.get("reason")}

    natal_score = round(float(natal.get("dominant_score") or 0.0), 3)
    wealth_lords = _wealth_lords(chart)

    major, sub = _extract_dasha(chart, moment)
    dasha_score = 0.5
    dasha_evidence: list[dict[str, Any]] = []
    activated = [planet for planet in (major, sub) if planet]
    if activated:
        dasha_score = 0.0
        for planet in activated:
            house = _planet_house(chart, planet)
            if planet in wealth_lords or planet in FINANCE_SIGNIFICATORS:
                dasha_score += 0.35
                dasha_evidence.append({"rule": "finance_relevant_dasha_lord", "planet": planet, "house": house})
            if house in SUPPORTIVE_HOUSES:
                dasha_score += 0.2
                dasha_evidence.append({"rule": "dasha_lord_supportive_house", "planet": planet, "house": house})
            elif house in CHALLENGING_HOUSES:
                dasha_score += 0.07
                dasha_evidence.append({"rule": "dasha_lord_complex_house", "planet": planet, "house": house})
        dasha_score = round(min(1.0, dasha_score), 3)
    else:
        dasha_evidence.append({"rule": "dasha_data_unavailable", "score": 0.5})

    transit_score, transit_evidence = _transit_score(chart, moment)
    total = round(natal_score * 0.4 + dasha_score * 0.35 + transit_score * 0.25, 3)

    return {
        "available": True,
        "date": moment.date().isoformat(),
        "score": total,
        "components": {
            "natal": natal_score,
            "dasha": dasha_score,
            "transit": transit_score,
        },
        "dominant_theme": natal.get("dominant_theme"),
        "dasha": {"major": major, "sub": sub},
        "evidence": dasha_evidence + transit_evidence,
    }


def _scan(chart: dict[str, Any], start: datetime, end: datetime, step_days: int) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    cursor = start
    while cursor <= end:
        scored = score_finance_moment_v1(chart, cursor)
        if scored.get("available"):
            points.append(scored)
        cursor += timedelta(days=step_days)
    return points


def _strongest(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not points:
        return None
    return max(points, key=lambda item: float(item.get("score") or 0.0))


def analyze_finance_timing_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 5,
    lookahead_years: int = 5,
    step_days: int = 30,
) -> dict[str, Any]:
    """Compare past, present and future finance-supportive periods.

    Scores symbolic support for earning/growth/opportunity. It does not predict
    guaranteed profits, investment returns, or advise any transaction.
    """
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")
    if not 7 <= step_days <= 90:
        raise ValueError("step_days must be between 7 and 90.")

    past_start = reference_moment - timedelta(days=365 * lookback_years)
    past_end = reference_moment - timedelta(days=1)
    future_start = reference_moment + timedelta(days=1)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    past_points = _scan(chart, past_start, past_end, step_days)
    present = score_finance_moment_v1(chart, reference_moment)
    future_points = _scan(chart, future_start, future_end, step_days)

    strongest_past = _strongest(past_points)
    strongest_future = _strongest(future_points)

    if not present.get("available"):
        return {
            "available": False,
            "event": "finance_timing",
            "model_version": "v1",
            "reason": present.get("reason"),
        }

    past_score = float(strongest_past.get("score") or 0.0) if strongest_past else 0.0
    future_score = float(strongest_future.get("score") or 0.0) if strongest_future else 0.0
    present_score = float(present.get("score") or 0.0)

    comparison = "similar_strength"
    if strongest_past and strongest_future:
        delta = round(future_score - past_score, 3)
        if delta > 0.08:
            comparison = "future_stronger"
        elif delta < -0.08:
            comparison = "past_stronger"
    elif strongest_future:
        comparison = "future_only"
    elif strongest_past:
        comparison = "past_only"

    return {
        "available": True,
        "event": "finance_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "lookback_years": lookback_years,
        "lookahead_years": lookahead_years,
        "past": {
            "available": strongest_past is not None,
            "strongest_point": strongest_past,
            "period_start": past_start.isoformat(),
            "period_end": past_end.isoformat(),
        },
        "present": present,
        "future": {
            "available": strongest_future is not None,
            "strongest_point": strongest_future,
            "period_start": future_start.isoformat(),
            "period_end": future_end.isoformat(),
        },
        "comparison": {
            "result": comparison,
            "future_minus_past": round(future_score - past_score, 3),
            "present_vs_future": round(future_score - present_score, 3),
        },
        "limitation": (
            "Finance timing is an astrological support indicator for earning, growth and opportunity. "
            "It is not financial advice, does not guarantee profits or income, and should not be used alone for investment decisions."
        ),
    }
