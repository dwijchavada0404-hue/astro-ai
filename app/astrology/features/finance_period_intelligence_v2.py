from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from app.astrology.features.finance_timing_v1 import (
    _collect_periods,
    _period_score,
    _wealth_lords,
)
from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1


_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2}|21\d{2})\b")
_RANGE_RE = re.compile(r"\b(19\d{2}|20\d{2}|21\d{2})\s*(?:to|through|till|until|[-–—])\s*(19\d{2}|20\d{2}|21\d{2})\b")


def extract_finance_period_request_v2(question: str) -> dict[str, Any]:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    q = re.sub(r"\s+", " ", question.strip().lower())
    range_match = _RANGE_RE.search(q)
    years = [int(value) for value in _YEAR_RE.findall(q)]

    if range_match:
        start_year, end_year = map(int, range_match.groups())
        if end_year < start_year:
            start_year, end_year = end_year, start_year
        return {
            "available": True,
            "request_type": "year_range",
            "start_year": start_year,
            "end_year": end_year,
            "years": list(range(start_year, end_year + 1)),
        }

    unique_years = list(dict.fromkeys(years))
    if len(unique_years) >= 2:
        return {
            "available": True,
            "request_type": "year_comparison",
            "years": unique_years,
        }
    if len(unique_years) == 1:
        return {
            "available": True,
            "request_type": "single_year",
            "year": unique_years[0],
            "years": unique_years,
        }
    return {"available": False, "request_type": "open_ended", "years": []}


def _year_bounds(year: int, tzinfo) -> tuple[datetime, datetime]:
    return datetime(year, 1, 1, tzinfo=tzinfo), datetime(year + 1, 1, 1, tzinfo=tzinfo)


def _score_year(
    year: int,
    periods: list[dict[str, Any]],
    wealth_lords: set[str],
    natal_score: float,
    tzinfo,
) -> dict[str, Any]:
    start, end = _year_bounds(year, tzinfo)
    weighted_total = 0.0
    covered_seconds = 0.0
    strongest: dict[str, Any] | None = None

    for period in periods:
        ps, pe = period["start_dt"], period["end_dt"]
        overlap_start, overlap_end = max(ps, start), min(pe, end)
        if overlap_end <= overlap_start:
            continue
        score = _period_score(period, wealth_lords, natal_score)
        seconds = (overlap_end - overlap_start).total_seconds()
        weighted_total += score * seconds
        covered_seconds += seconds
        candidate = {
            "start": overlap_start.isoformat(),
            "end": overlap_end.isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "score": score,
        }
        if strongest is None or score > strongest["score"]:
            strongest = candidate

    score = round(weighted_total / covered_seconds, 3) if covered_seconds else None
    return {
        "year": year,
        "available": score is not None,
        "score": score,
        "strongest_period": strongest,
        "interpretation": (
            "stronger_support" if score is not None and score >= 0.72
            else "moderate_support" if score is not None and score >= 0.52
            else "lighter_support" if score is not None
            else "insufficient_timing_data"
        ),
    }


def analyze_finance_period_v2(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    """Answer explicit Finance year/range/comparison requests without implying guaranteed returns."""
    request = extract_finance_period_request_v2(question)
    if not request["available"]:
        return {"available": False, "event": "finance_period", "model_version": "v2", "request": request}
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_finance_wealth_v1(chart)
    periods = _collect_periods(chart, reference_moment)
    if not natal.get("available") or not periods:
        return {
            "available": False,
            "event": "finance_period",
            "model_version": "v2",
            "request": request,
            "reason": "Natal finance reasoning or usable dasha timing data is unavailable.",
        }

    natal_score = float(natal.get("dominant_score") or 0.0)
    wealth_lords = _wealth_lords(chart)
    results = [_score_year(year, periods, wealth_lords, natal_score, reference_moment.tzinfo) for year in request["years"]]
    available = [item for item in results if item["available"]]
    strongest = max(available, key=lambda item: item["score"], default=None)
    weakest = min(available, key=lambda item: item["score"], default=None)

    comparison = None
    if len(available) >= 2 and strongest and weakest:
        delta = round(float(strongest["score"]) - float(weakest["score"]), 3)
        comparison = {
            "strongest_year": strongest["year"],
            "weakest_year": weakest["year"],
            "score_difference": delta,
            "material_difference": delta > 0.05,
        }

    return {
        "available": bool(available),
        "event": "finance_period",
        "model_version": "v2",
        "request": request,
        "year_results": results,
        "strongest_year": strongest,
        "comparison": comparison,
        "answer": "The requested financial periods were compared using natal finance strength and available dasha activation.",
        "limitation": "Astrological support scores are not financial advice and do not guarantee income, profits, returns, inheritance or wealth creation.",
    }
