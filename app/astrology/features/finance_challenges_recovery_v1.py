from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.finance_timing_v1 import (
    _collect_periods,
    _period_score,
    _wealth_lords,
)
from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1
from app.astrology.features.finance_wealth_trajectory_v1 import analyze_finance_wealth_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _house_lord(chart: dict[str, Any], house_no: int) -> str | None:
    house = _safe_dict(_safe_dict(chart.get("houses")).get(str(house_no)) or _safe_dict(chart.get("houses")).get(house_no))
    lord = house.get("lord")
    return lord if isinstance(lord, str) and lord else None


def _lord_house(chart: dict[str, Any], house_no: int) -> tuple[str | None, int | None]:
    lord = _house_lord(chart, house_no)
    if not lord:
        return None, None
    return lord, _planet_house(chart, lord)


def _challenge_profile(chart: dict[str, Any], trajectory: dict[str, Any]) -> tuple[dict[str, float], list[dict[str, Any]]]:
    scores = {
        "expense_pressure": 0.0,
        "debt_obligation_pressure": 0.0,
        "income_instability": 0.0,
        "speculative_volatility": 0.0,
        "shared_resource_complexity": 0.0,
        "retention_leakage": 0.0,
    }
    evidence: list[dict[str, Any]] = []

    # 12th house = outflow/expense symbolism; 6th = obligations/debt/service pressure;
    # 8th = shared-resource shocks/transformations; 5th = speculation/risk appetite.
    for house_no, key, weight in (
        (12, "expense_pressure", 0.34),
        (6, "debt_obligation_pressure", 0.30),
        (8, "shared_resource_complexity", 0.30),
        (5, "speculative_volatility", 0.22),
    ):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {6, 8, 12}:
            scores[key] += weight
            evidence.append({"rule": "challenge_house_lord_complex_placement", "house": house_no, "lord": lord, "lord_house": ph, "challenge": key})
        elif lord and ph in {2, 5, 9, 10, 11}:
            scores[key] += weight * 0.25
            evidence.append({"rule": "challenge_house_lord_supported", "house": house_no, "lord": lord, "lord_house": ph, "challenge": key})

    for planet, house_set, key, weight in (
        ("Rahu", {2, 5, 8, 11}, "speculative_volatility", 0.18),
        ("Ketu", {2, 8, 12}, "retention_leakage", 0.16),
        ("Mars", {2, 5, 8, 12}, "income_instability", 0.14),
        ("Saturn", {6, 8, 12}, "debt_obligation_pressure", 0.14),
    ):
        ph = _planet_house(chart, planet)
        if ph in house_set:
            scores[key] += weight
            evidence.append({"rule": "challenge_planet_finance_pressure", "planet": planet, "house": ph, "challenge": key})

    volatility = float(trajectory.get("volatility_score") or 0.0)
    retention = float(trajectory.get("retention_score") or 0.0)
    earning = float(trajectory.get("earning_capacity_score") or 0.0)
    if volatility >= 0.5:
        scores["income_instability"] += 0.22
        scores["speculative_volatility"] += 0.18
        evidence.append({"rule": "trajectory_high_volatility", "score": volatility})
    if retention + 0.12 < earning:
        scores["retention_leakage"] += 0.34
        evidence.append({"rule": "earning_exceeds_retention", "earning": earning, "retention": retention})

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    return scores, evidence


def analyze_finance_challenges_recovery_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 3,
    lookahead_years: int = 5,
) -> dict[str, Any]:
    """Assess symbolic financial-pressure themes and recovery-support periods.

    The engine distinguishes natal vulnerability themes from timing. It does not
    claim bankruptcy, losses, debt events or recovery as certainties and does not
    provide financial advice.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if lookback_years < 0 or lookahead_years < 1:
        raise ValueError("lookback_years must be >= 0 and lookahead_years must be >= 1.")

    natal = analyze_finance_wealth_v1(chart)
    trajectory = analyze_finance_wealth_trajectory_v1(chart)
    if not natal.get("available") or not trajectory.get("available"):
        return {
            "available": False,
            "event": "finance_challenges_recovery",
            "model_version": "v1",
            "reason": "Finance natal or trajectory foundation is unavailable.",
        }

    challenge_scores, evidence = _challenge_profile(chart, trajectory)
    ranked = sorted(challenge_scores.items(), key=lambda item: item[1], reverse=True)
    primary_challenge, primary_score = ranked[0]

    natal_score = float(natal.get("dominant_score") or 0.0)
    wealth_lords = _wealth_lords(chart)
    periods = _collect_periods(chart, reference_moment)

    past_cutoff = reference_moment.replace(year=reference_moment.year - lookback_years) if lookback_years else reference_moment
    future_cutoff = reference_moment.replace(year=reference_moment.year + lookahead_years)

    past_points: list[dict[str, Any]] = []
    current_point: dict[str, Any] | None = None
    future_points: list[dict[str, Any]] = []

    for period in periods:
        score = _period_score(period, wealth_lords, natal_score)
        point = {
            "start": period["start_dt"].isoformat(),
            "end": period["end_dt"].isoformat(),
            "major_lord": period.get("major_lord") or period.get("mahadasha") or period.get("lord"),
            "sub_lord": period.get("sub_lord") or period.get("antardasha"),
            "support_score": score,
            "pressure_score": round(max(0.0, min(1.0, 1.0 - score)), 3),
        }
        if period["end_dt"] <= reference_moment and period["end_dt"] >= past_cutoff:
            past_points.append(point)
        elif period["start_dt"] <= reference_moment < period["end_dt"]:
            current_point = point
        elif reference_moment < period["start_dt"] <= future_cutoff:
            future_points.append(point)

    strongest_recovery = max(future_points, key=lambda item: item["support_score"], default=None)
    strongest_future_pressure = max(future_points, key=lambda item: item["pressure_score"], default=None)
    strongest_past_pressure = max(past_points, key=lambda item: item["pressure_score"], default=None)

    current_state = "timing_unavailable"
    if current_point:
        if current_point["support_score"] >= 0.72:
            current_state = "recovery_or_expansion_support"
        elif current_point["support_score"] >= 0.52:
            current_state = "mixed_or_stabilising"
        else:
            current_state = "higher_financial_pressure"

    recovery_outlook = "timing_unavailable"
    if strongest_recovery:
        if strongest_recovery["support_score"] >= 0.72:
            recovery_outlook = "strong_recovery_support_ahead"
        elif strongest_recovery["support_score"] >= 0.52:
            recovery_outlook = "moderate_recovery_support_ahead"
        else:
            recovery_outlook = "limited_recovery_support_in_scan"

    return {
        "available": True,
        "event": "finance_challenges_recovery",
        "model_version": "v1",
        "challenge_scores": challenge_scores,
        "ranked_challenges": [
            {"challenge": challenge, "score": score}
            for challenge, score in ranked
        ],
        "primary_challenge": primary_challenge,
        "primary_challenge_score": primary_score,
        "current_state": current_state,
        "current_period": current_point,
        "strongest_past_pressure": strongest_past_pressure,
        "strongest_future_pressure": strongest_future_pressure,
        "strongest_recovery_period": strongest_recovery,
        "recovery_outlook": recovery_outlook,
        "evidence": evidence,
        "answer": (
            f"The strongest natal financial-pressure theme is {primary_challenge.replace('_', ' ')}. "
            f"The timing scan currently reads as {current_state.replace('_', ' ')}, with "
            f"{recovery_outlook.replace('_', ' ')}."
        ),
        "limitation": (
            "This is symbolic astrological pattern analysis. It does not predict certain losses, debt, insolvency, "
            "recovery, returns or financial outcomes and is not financial advice."
        ),
    }
