from __future__ import annotations

from typing import Any

from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1
from app.astrology.features.finance_source_of_wealth_v1 import analyze_finance_source_of_wealth_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _safe_dict(chart.get("houses"))
    return _safe_dict(houses.get(str(number)) or houses.get(number))


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _lord_house(chart: dict[str, Any], house_number: int) -> tuple[str | None, int | None]:
    lord = _house(chart, house_number).get("lord")
    if not isinstance(lord, str) or not lord:
        return None, None
    return lord, _planet_house(chart, lord)


def analyze_finance_wealth_trajectory_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Describe the chart's symbolic wealth-building trajectory.

    The layer compares earning capacity with retention/accumulation, estimates
    stability versus volatility, and identifies whether the chart leans more
    toward early acceleration or slower/later consolidation. It does not predict
    guaranteed wealth or provide financial advice.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    natal = analyze_finance_wealth_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "finance_wealth_trajectory",
            "model_version": "v1",
            "reason": "Finance natal foundation is unavailable.",
        }

    source = analyze_finance_source_of_wealth_v1(chart)
    theme_scores = _safe_dict(natal.get("theme_scores"))

    earning_capacity = min(
        1.0,
        0.55 * float(theme_scores.get("income_savings") or 0.0)
        + 0.45 * float(theme_scores.get("gains_networks") or 0.0),
    )

    retention_score = 0.0
    retention_evidence: list[dict[str, Any]] = []
    for house_no, weight in ((2, 0.34), (4, 0.18), (9, 0.14), (11, 0.22)):
        lord, placed_house = _lord_house(chart, house_no)
        if lord is None:
            continue
        if placed_house in {2, 4, 9, 10, 11}:
            retention_score += weight
            retention_evidence.append({
                "rule": "retention_supportive_lord_placement",
                "house": house_no,
                "lord": lord,
                "lord_house": placed_house,
            })
        elif placed_house in {6, 8, 12}:
            retention_score += weight * 0.25
            retention_evidence.append({
                "rule": "retention_complex_lord_placement",
                "house": house_no,
                "lord": lord,
                "lord_house": placed_house,
            })

    saturn_house = _planet_house(chart, "Saturn")
    if saturn_house in {2, 4, 9, 10, 11}:
        retention_score += 0.12
        retention_evidence.append({"rule": "saturn_accumulation_support", "house": saturn_house})

    retention_score = round(min(1.0, retention_score), 3)
    earning_capacity = round(earning_capacity, 3)

    volatility_score = 0.0
    volatility_evidence: list[dict[str, Any]] = []
    speculative = float(theme_scores.get("speculation_creativity") or 0.0)
    shared = float(theme_scores.get("joint_assets_inheritance") or 0.0)
    if speculative >= 0.5:
        volatility_score += 0.35
        volatility_evidence.append({"rule": "strong_speculative_theme", "score": speculative})
    if shared >= 0.5:
        volatility_score += 0.18
        volatility_evidence.append({"rule": "shared_resource_dependency", "score": shared})

    for planet in ("Rahu", "Ketu", "Mars"):
        ph = _planet_house(chart, planet)
        if ph in {2, 5, 8, 11}:
            volatility_score += 0.12
            volatility_evidence.append({"rule": "volatile_planet_finance_house", "planet": planet, "house": ph})

    volatility_score = round(min(1.0, volatility_score), 3)
    stability_score = round(max(0.0, min(1.0, retention_score - 0.45 * volatility_score + 0.25)), 3)

    # Saturn-led accumulation and strong 9th-house support tend to describe
    # slower compounding/consolidation rather than very early acceleration.
    later_life_score = 0.0
    early_life_score = 0.0
    if saturn_house in {2, 9, 10, 11}:
        later_life_score += 0.42
    jupiter_house = _planet_house(chart, "Jupiter")
    if jupiter_house in {2, 5, 9, 11}:
        early_life_score += 0.22
        later_life_score += 0.18
    mercury_house = _planet_house(chart, "Mercury")
    if mercury_house in {2, 3, 5, 10, 11}:
        early_life_score += 0.28
    for house_no in (2, 9, 11):
        _, ph = _lord_house(chart, house_no)
        if ph in {9, 10, 11}:
            later_life_score += 0.12
        if ph in {2, 3, 5}:
            early_life_score += 0.10

    early_life_score = round(min(1.0, early_life_score), 3)
    later_life_score = round(min(1.0, later_life_score), 3)
    if later_life_score > early_life_score + 0.1:
        life_phase_pattern = "later_life_strengthening"
    elif early_life_score > later_life_score + 0.1:
        life_phase_pattern = "earlier_financial_acceleration"
    else:
        life_phase_pattern = "broadly_balanced_across_life"

    if stability_score >= 0.68 and volatility_score <= 0.35:
        accumulation_pattern = "gradual_stable_accumulation"
    elif volatility_score >= 0.55:
        accumulation_pattern = "volatile_or_cyclical_growth"
    elif earning_capacity >= 0.65 and retention_score < 0.45:
        accumulation_pattern = "strong_earning_weaker_retention"
    elif retention_score >= earning_capacity + 0.12:
        accumulation_pattern = "conservative_accumulation"
    else:
        accumulation_pattern = "mixed_accumulation_pattern"

    if retention_score >= earning_capacity + 0.12:
        earning_retention_balance = "retention_stronger_than_earning"
    elif earning_capacity >= retention_score + 0.12:
        earning_retention_balance = "earning_stronger_than_retention"
    else:
        earning_retention_balance = "earning_and_retention_balanced"

    return {
        "available": True,
        "event": "finance_wealth_trajectory",
        "model_version": "v1",
        "earning_capacity_score": earning_capacity,
        "retention_score": retention_score,
        "stability_score": stability_score,
        "volatility_score": volatility_score,
        "early_life_score": early_life_score,
        "later_life_score": later_life_score,
        "accumulation_pattern": accumulation_pattern,
        "life_phase_pattern": life_phase_pattern,
        "earning_retention_balance": earning_retention_balance,
        "primary_wealth_source": source.get("primary_source") if source.get("available") else None,
        "secondary_wealth_source": source.get("secondary_source") if source.get("available") else None,
        "evidence": {
            "retention": retention_evidence,
            "volatility": volatility_evidence,
        },
        "answer": (
            f"The chart shows a {accumulation_pattern.replace('_', ' ')} pattern, with "
            f"{earning_retention_balance.replace('_', ' ')} and a {life_phase_pattern.replace('_', ' ')} tendency."
        ),
        "limitation": (
            "This is symbolic astrological pattern analysis, not financial advice or a guarantee of wealth, "
            "returns, savings, asset growth or life-stage outcomes."
        ),
    }
