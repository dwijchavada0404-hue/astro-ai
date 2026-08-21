from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.education_learning_reasoning_v1 import analyze_education_learning_v1
from app.astrology.features.property_home_timing_v1 import _collect_periods, _house_lords, _period_lords


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _period_scores(
    period: dict[str, Any],
    foundation_lords: set[str],
    higher_lords: set[str],
    skill_lords: set[str],
    research_lords: set[str],
    natal: dict[str, Any],
) -> tuple[float, float, float, float]:
    themes = natal.get("theme_scores") if isinstance(natal.get("theme_scores"), dict) else {}
    major, sub = _period_lords(period)

    study = 0.12 + float(themes.get("foundational_learning") or 0.0) * 0.34
    higher = 0.10 + float(themes.get("higher_education") or 0.0) * 0.36
    skill = 0.12 + max(
        float(themes.get("analytical_learning") or 0.0),
        float(themes.get("communication_learning") or 0.0),
    ) * 0.32
    research = 0.08 + float(themes.get("research_depth") or 0.0) * 0.36

    for lord, primary in ((major, 0.26), (sub, 0.17)):
        if lord in foundation_lords:
            study += primary
        if lord in higher_lords:
            higher += primary
        if lord in skill_lords:
            skill += primary
        if lord in research_lords:
            research += primary
        if lord in {"Mercury", "Jupiter"}:
            study += primary * 0.20
            higher += primary * 0.18
            skill += primary * 0.22
        if lord in {"Saturn", "Mars"}:
            research += primary * 0.16
            skill += primary * 0.10
        if lord in {"Venus", "Moon"}:
            skill += primary * 0.08

    return _bounded(study), _bounded(higher), _bounded(skill), _bounded(research)


def _best_period(
    periods: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    foundation_lords: set[str],
    higher_lords: set[str],
    skill_lords: set[str],
    research_lords: set[str],
    natal: dict[str, Any],
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps, pe = period["start_dt"], period["end_dt"]
        if pe < start or ps > end:
            continue
        study, higher, skill, research = _period_scores(
            period, foundation_lords, higher_lords, skill_lords, research_lords, natal
        )
        candidates.append({
            "start": max(ps, start).isoformat(),
            "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "study_support_score": study,
            "higher_education_support_score": higher,
            "skill_learning_support_score": skill,
            "research_support_score": research,
        })
    return max(
        candidates,
        key=lambda item: (
            max(item["study_support_score"], item["higher_education_support_score"], item["skill_learning_support_score"], item["research_support_score"]),
            item["higher_education_support_score"],
        ),
        default=None,
    )


def analyze_education_learning_timing_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 5,
    lookahead_years: int = 7,
) -> dict[str, Any]:
    """Compare past, present and future education/learning activation."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_education_learning_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "education_learning_timing", "model_version": "v1", "reason": "Education natal foundation is unavailable."}

    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {
            "available": False,
            "event": "education_learning_timing",
            "model_version": "v1",
            "reason": "No usable dasha periods are available for Education & Learning timing.",
            "natal": natal,
        }

    foundation_lords = _house_lords(chart, (4, 5, 9))
    higher_lords = _house_lords(chart, (5, 9))
    skill_lords = _house_lords(chart, (3, 5, 9))
    research_lords = _house_lords(chart, (5, 8, 9))
    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)

    args = (foundation_lords, higher_lords, skill_lords, research_lords, natal)
    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), *args)
    present = _best_period(periods, reference_moment, reference_moment, *args)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, *args)

    return {
        "available": bool(past or present or future),
        "event": "education_learning_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past, "historical_status": "unconfirmed" if past else None},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future},
        "natal": natal,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "A past high-scoring education period is not proof that admission, study, examination, graduation or qualification occurred. Known education history overrides astrology.",
        },
        "answer": "Education timing compares symbolic study, higher-education, skill-development and research activation across past, present and future dasha periods.",
        "limitation": (
            "Timing activation is not a probability or guarantee of admission, examination success, grades, scholarships, graduation, licences or employment. "
            "Educational decisions should use real eligibility, interests, finances and institution-specific requirements."
        ),
    }
