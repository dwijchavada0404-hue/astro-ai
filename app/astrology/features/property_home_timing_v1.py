from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.property_home_reasoning_v1 import analyze_property_home_v1


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


def _house_lords(chart: dict[str, Any], house_numbers: tuple[int, ...]) -> set[str]:
    houses = _safe_dict(chart.get("houses"))
    result: set[str] = set()
    for number in house_numbers:
        house = _safe_dict(houses.get(str(number)) or houses.get(number))
        lord = house.get("lord")
        if isinstance(lord, str) and lord:
            result.add(lord)
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


def _period_lords(period: dict[str, Any]) -> tuple[str, str]:
    major = str(period.get("major_lord") or period.get("mahadasha") or period.get("lord") or "")
    sub = str(period.get("sub_lord") or period.get("antardasha") or "")
    return major, sub


def _period_scores(
    period: dict[str, Any],
    property_lords: set[str],
    mobility_lords: set[str],
    natal_home_score: float,
    natal_relocation_score: float,
) -> tuple[float, float]:
    major, sub = _period_lords(period)

    home_support = 0.22 + natal_home_score * 0.34
    relocation_activation = 0.16 + natal_relocation_score * 0.38

    for lord, property_weight, mobility_weight in ((major, 0.26, 0.22), (sub, 0.17, 0.15)):
        if lord in property_lords:
            home_support += property_weight
        if lord in mobility_lords:
            relocation_activation += mobility_weight
        if lord in {"Venus", "Moon", "Jupiter", "Mars", "Saturn"}:
            home_support += property_weight * 0.35
        if lord in {"Rahu", "Ketu", "Mars", "Saturn"}:
            relocation_activation += mobility_weight * 0.30

    return round(min(1.0, home_support), 3), round(min(1.0, relocation_activation), 3)


def _best_period(
    periods: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    property_lords: set[str],
    mobility_lords: set[str],
    natal_home_score: float,
    natal_relocation_score: float,
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps = period["start_dt"]
        pe = period["end_dt"]
        if pe < start or ps > end:
            continue
        home_score, relocation_score = _period_scores(
            period,
            property_lords,
            mobility_lords,
            natal_home_score,
            natal_relocation_score,
        )
        candidates.append({
            "start": max(ps, start).isoformat(),
            "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "home_property_support_score": home_score,
            "relocation_activation_score": relocation_score,
        })
    return max(candidates, key=lambda item: (item["home_property_support_score"], item["relocation_activation_score"]), default=None)


def analyze_property_home_timing_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 5,
    lookahead_years: int = 5,
) -> dict[str, Any]:
    """Compare past, present and future Property & Home support periods.

    Timing scores describe symbolic activation of home/property and relocation themes.
    Past windows remain historical hypotheses until the user confirms what actually happened.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_property_home_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "property_home_timing",
            "model_version": "v1",
            "reason": "Property & Home natal foundation is unavailable.",
        }

    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {
            "available": False,
            "event": "property_home_timing",
            "model_version": "v1",
            "reason": "No usable dasha periods are available for Property & Home timing analysis.",
            "natal": natal,
        }

    themes = _safe_dict(natal.get("theme_scores"))
    natal_home_score = max(
        float(themes.get("property_acquisition") or 0.0),
        float(themes.get("home_stability") or 0.0),
        float(themes.get("asset_accumulation") or 0.0),
    )
    natal_relocation_score = float(themes.get("relocation_change") or 0.0)

    property_lords = _house_lords(chart, (2, 4, 9, 11))
    mobility_lords = _house_lords(chart, (3, 4, 9, 12))

    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    past = _best_period(
        periods, past_start, reference_moment - timedelta(seconds=1), property_lords, mobility_lords,
        natal_home_score, natal_relocation_score,
    )
    present = _best_period(
        periods, reference_moment, reference_moment, property_lords, mobility_lords,
        natal_home_score, natal_relocation_score,
    )
    future = _best_period(
        periods, reference_moment + timedelta(seconds=1), future_end, property_lords, mobility_lords,
        natal_home_score, natal_relocation_score,
    )

    comparison = None
    if past and future:
        delta = round(float(future["home_property_support_score"]) - float(past["home_property_support_score"]), 3)
        comparison = {
            "future_minus_past": delta,
            "result": "future_stronger" if delta > 0.05 else "past_stronger" if delta < -0.05 else "similar_strength",
        }

    return {
        "available": bool(past or present or future),
        "event": "property_home_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {
            "available": past is not None,
            "strongest_period": past,
            "historical_status": "unconfirmed" if past else None,
        },
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future},
        "comparison": comparison,
        "natal_home_property_score": round(natal_home_score, 3),
        "natal_relocation_score": round(natal_relocation_score, 3),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "A past high-scoring Property & Home window must not be stated as a purchase, sale, inheritance, move "
                "or ownership event unless the user confirms the real-world milestone. Known facts override astrology."
            ),
        },
        "answer": (
            "Property & Home timing is compared across recent past, present and future dasha periods. "
            "Scores represent symbolic activation, not proof or probability of a property transaction or relocation."
        ),
        "limitation": (
            "This timing analysis does not predict or guarantee property purchase, ownership, sale, inheritance, "
            "financing approval, investment returns, relocation or residential stability."
        ),
    }
