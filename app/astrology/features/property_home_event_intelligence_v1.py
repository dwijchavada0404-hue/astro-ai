from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.property_home_reasoning_v1 import analyze_property_home_v1
from app.astrology.features.property_home_timing_v1 import analyze_property_home_timing_v1


EVENT_LABELS = {
    "property_acquisition": "property acquisition or establishment of a home base",
    "property_sale_disposal": "property sale, disposal or release of a home-linked asset",
    "relocation": "residential relocation or change of home base",
    "inheritance_family_property": "inheritance or family-linked property transition",
    "renovation_construction": "renovation, construction or material improvement of a residence",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _house_lord(chart: dict[str, Any], number: int) -> str | None:
    houses = _safe_dict(chart.get("houses"))
    house = _safe_dict(houses.get(str(number)) or houses.get(number))
    lord = house.get("lord")
    return lord if isinstance(lord, str) and lord else None


def _planet_house(chart: dict[str, Any], planet: str | None) -> int | None:
    if not planet:
        return None
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _natal_event_scores(chart: dict[str, Any], foundation: dict[str, Any]) -> dict[str, float]:
    themes = _safe_dict(foundation.get("theme_scores"))
    acquisition = _safe_float(themes.get("property_acquisition"))
    accumulation = _safe_float(themes.get("asset_accumulation"))
    stability = _safe_float(themes.get("home_stability"))
    comfort = _safe_float(themes.get("home_comfort"))
    relocation = _safe_float(themes.get("relocation_change"))

    eighth_lord = _house_lord(chart, 8)
    eighth_house = _planet_house(chart, eighth_lord)
    inheritance_support = 0.0
    if eighth_lord:
        inheritance_support += 0.22
    if eighth_house in {2, 4, 8, 9, 11}:
        inheritance_support += 0.28

    mars_house = _planet_house(chart, "Mars")
    renovation_support = 0.16 if mars_house in {3, 4, 10, 11} else 0.04

    scores = {
        "property_acquisition": 0.52 * acquisition + 0.26 * accumulation + 0.14 * stability + 0.08 * comfort,
        "property_sale_disposal": 0.36 * relocation + 0.24 * accumulation + 0.20 * acquisition + 0.20 * (1.0 - stability),
        "relocation": 0.68 * relocation + 0.18 * (1.0 - stability) + 0.14 * acquisition,
        "inheritance_family_property": 0.38 * acquisition + 0.24 * accumulation + 0.38 * inheritance_support,
        "renovation_construction": 0.34 * acquisition + 0.28 * comfort + 0.18 * accumulation + 0.20 * renovation_support,
    }
    return {key: round(max(0.0, min(1.0, value)), 3) for key, value in scores.items()}


def _event_outlook(score: float) -> str:
    if score >= 0.75:
        return "strongly_active"
    if score >= 0.50:
        return "active"
    if score >= 0.25:
        return "mildly_active"
    return "weak_signal"


def _timing_component(event_name: str, period: dict[str, Any] | None) -> float:
    if not period:
        return 0.0
    home = _safe_float(period.get("home_property_support_score"))
    relocation = _safe_float(period.get("relocation_activation_score"))
    if event_name == "relocation":
        return relocation
    if event_name == "property_sale_disposal":
        return 0.55 * relocation + 0.45 * home
    return home


def analyze_property_home_event_intelligence_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Rank symbolic Property & Home event themes across past, present and future.

    Event scores describe activation only. They are not probabilities and must never be
    converted into factual claims about purchases, sales, inheritance or relocation.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    foundation = analyze_property_home_v1(chart)
    if not foundation.get("available"):
        return {
            "available": False,
            "event": "property_home_event_intelligence",
            "model_version": "v1",
            "reason": "Property & Home natal foundation is unavailable.",
        }

    timing = analyze_property_home_timing_v1(chart, reference_moment)
    natal_scores = _natal_event_scores(chart, foundation)

    period_map = {
        "past": _safe_dict(_safe_dict(timing.get("past")).get("strongest_period")) if timing.get("available") else {},
        "present": _safe_dict(_safe_dict(timing.get("present")).get("active_period")) if timing.get("available") else {},
        "future": _safe_dict(_safe_dict(timing.get("future")).get("strongest_period")) if timing.get("available") else {},
    }

    events: dict[str, Any] = {}
    for event_name, natal_score in natal_scores.items():
        windows: dict[str, Any] = {}
        for bucket in ("past", "present", "future"):
            period = period_map[bucket]
            timing_score = _timing_component(event_name, period)
            score = round(min(1.0, 0.58 * natal_score + 0.42 * timing_score), 3)
            windows[bucket] = {
                "score": score,
                "outlook": _event_outlook(score),
                "timing_period": period or None,
                "historical_status": "unconfirmed" if bucket == "past" else None,
            }
        events[event_name] = {
            "label": EVENT_LABELS[event_name],
            "natal_strength": natal_score,
            "past": windows["past"],
            "present": windows["present"],
            "future": windows["future"],
        }

    ranked_future = sorted(
        ((name, _safe_float(_safe_dict(data.get("future")).get("score"))) for name, data in events.items()),
        key=lambda item: item[1],
        reverse=True,
    )

    return {
        "available": True,
        "event": "property_home_event_intelligence",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_future_event": ranked_future[0][0] if ranked_future else None,
        "strongest_future_event_score": round(ranked_future[0][1], 3) if ranked_future else 0.0,
        "timing_available": bool(timing.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Past event windows are symbolic only. AstroAI must not state that a purchase, sale, inheritance, "
                "relocation, renovation or construction event occurred unless the user confirms it. Known facts override astrology."
            ),
        },
        "answer": (
            "Property & Home event themes are ranked from natal patterns and available dasha timing. "
            "Scores represent symbolic activation strength, not event probability or proof."
        ),
        "limitation": (
            "This event layer does not predict or guarantee property purchase, ownership, sale, inheritance, financing, "
            "relocation, construction, renovation, investment returns or any real-estate outcome."
        ),
    }
