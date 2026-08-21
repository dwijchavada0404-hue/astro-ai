from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.friends_social_community_reasoning_v1 import analyze_friends_social_community_v1
from app.astrology.features.property_home_timing_v1 import _collect_periods, _house_lords, _period_lords


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _period_scores(
    period: dict[str, Any],
    friendship_lords: set[str],
    network_lords: set[str],
    community_lords: set[str],
    boundary_lords: set[str],
    natal: dict[str, Any],
) -> tuple[float, float, float, float]:
    themes = natal.get("theme_scores") if isinstance(natal.get("theme_scores"), dict) else {}
    major, sub = _period_lords(period)

    friendship = 0.12 + float(themes.get("close_friendship") or 0.0) * 0.34
    network = 0.12 + max(
        float(themes.get("social_breadth") or 0.0),
        float(themes.get("networking_collaboration") or 0.0),
        float(themes.get("communication_connection") or 0.0),
    ) * 0.34
    community = 0.10 + float(themes.get("community_belonging") or 0.0) * 0.36
    boundaries = 0.10 + float(themes.get("selective_boundaries") or 0.0) * 0.36

    for lord, primary in ((major, 0.26), (sub, 0.17)):
        if lord in friendship_lords:
            friendship += primary
        if lord in network_lords:
            network += primary
        if lord in community_lords:
            community += primary
        if lord in boundary_lords:
            boundaries += primary
        if lord in {"Venus", "Moon", "Mercury"}:
            friendship += primary * 0.14
        if lord in {"Mercury", "Rahu", "Jupiter"}:
            network += primary * 0.16
        if lord in {"Jupiter", "Venus", "Sun"}:
            community += primary * 0.14
        if lord in {"Saturn", "Ketu"}:
            boundaries += primary * 0.18

    return _bounded(friendship), _bounded(network), _bounded(community), _bounded(boundaries)


def _best_period(
    periods: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    friendship_lords: set[str],
    network_lords: set[str],
    community_lords: set[str],
    boundary_lords: set[str],
    natal: dict[str, Any],
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for period in periods:
        ps, pe = period["start_dt"], period["end_dt"]
        if pe < start or ps > end:
            continue
        friendship, network, community, boundaries = _period_scores(
            period, friendship_lords, network_lords, community_lords, boundary_lords, natal
        )
        candidates.append({
            "start": max(ps, start).isoformat(),
            "end": min(pe, end).isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "friendship_support_score": friendship,
            "networking_support_score": network,
            "community_support_score": community,
            "boundary_selectivity_score": boundaries,
        })
    return max(
        candidates,
        key=lambda item: max(
            item["friendship_support_score"],
            item["networking_support_score"],
            item["community_support_score"],
            item["boundary_selectivity_score"],
        ),
        default=None,
    )


def analyze_friends_social_community_timing_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 5,
    lookahead_years: int = 7,
) -> dict[str, Any]:
    """Compare symbolic social activation across past, present and future periods."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookback_years <= 10 or not 1 <= lookahead_years <= 10:
        raise ValueError("lookback_years and lookahead_years must be between 1 and 10.")

    natal = analyze_friends_social_community_v1(chart)
    if not natal.get("available"):
        return {"available": False, "event": "friends_social_community_timing", "model_version": "v1", "reason": "Friends & Community natal foundation is unavailable."}

    periods = _collect_periods(chart, reference_moment)
    if not periods:
        return {
            "available": False,
            "event": "friends_social_community_timing",
            "model_version": "v1",
            "reason": "No usable dasha periods are available for Friends, Social Networks & Community timing.",
            "natal": natal,
        }

    friendship_lords = _house_lords(chart, (5, 7, 11))
    network_lords = _house_lords(chart, (3, 7, 11))
    community_lords = _house_lords(chart, (9, 11))
    boundary_lords = _house_lords(chart, (6, 8, 12))
    args = (friendship_lords, network_lords, community_lords, boundary_lords, natal)

    past_start = reference_moment - timedelta(days=365 * lookback_years)
    future_end = reference_moment + timedelta(days=365 * lookahead_years)
    past = _best_period(periods, past_start, reference_moment - timedelta(seconds=1), *args)
    present = _best_period(periods, reference_moment, reference_moment, *args)
    future = _best_period(periods, reference_moment + timedelta(seconds=1), future_end, *args)

    return {
        "available": bool(past or present or future),
        "event": "friends_social_community_timing",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "past": {"available": past is not None, "strongest_period": past, "historical_status": "unconfirmed" if past else None},
        "present": {"available": present is not None, "active_period": present},
        "future": {"available": future is not None, "strongest_period": future},
        "natal": natal,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": "A past high-scoring social period is not proof that friendships formed, ended, strengthened, weakened, or that any betrayal, conflict, isolation or community milestone occurred. Known social history overrides astrology.",
        },
        "answer": "Social timing compares symbolic friendship, networking, community-belonging and boundary/selectivity activation across past, present and future dasha periods.",
        "limitation": (
            "Timing activation is not a probability or guarantee of friendship, popularity, networking success, community acceptance, loyalty, betrayal, conflict or isolation. "
            "It cannot identify whether a specific person is trustworthy or predict a particular social event."
        ),
    }
