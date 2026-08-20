from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1
from app.astrology.features.finance_source_of_wealth_v1 import analyze_finance_source_of_wealth_v1
from app.astrology.features.finance_wealth_trajectory_v1 import analyze_finance_wealth_trajectory_v1
from app.astrology.features.finance_timing_v1 import analyze_finance_timing_v1
from app.astrology.features.finance_challenges_recovery_v1 import analyze_finance_challenges_recovery_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _support_label(score: float) -> str:
    if score >= 0.72:
        return "strong"
    if score >= 0.52:
        return "moderate"
    return "limited"


def analyze_finance_synthesis_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 3,
    lookahead_years: int = 5,
) -> dict[str, Any]:
    """Combine all Finance V1 layers into one coherent symbolic assessment.

    The synthesis deliberately separates potential, source, accumulation, timing,
    and pressure/recovery so a strong natal wealth signature is not confused with
    guaranteed outcomes or a permanently favourable financial period.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_finance_wealth_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "finance_synthesis",
            "model_version": "v1",
            "reason": "Finance natal foundation is unavailable.",
        }

    source = analyze_finance_source_of_wealth_v1(chart)
    trajectory = analyze_finance_wealth_trajectory_v1(chart)
    timing = analyze_finance_timing_v1(
        chart,
        reference_moment,
        lookback_years=lookback_years,
        lookahead_years=lookahead_years,
    )
    challenges = analyze_finance_challenges_recovery_v1(
        chart,
        reference_moment,
        lookback_years=lookback_years,
        lookahead_years=lookahead_years,
    )

    natal_score = float(natal.get("dominant_score") or 0.0)
    trajectory_data = _safe_dict(trajectory)
    source_data = _safe_dict(source)
    timing_data = _safe_dict(timing)
    challenge_data = _safe_dict(challenges)

    retention = float(trajectory_data.get("retention_score") or 0.0)
    earning = float(trajectory_data.get("earning_capacity_score") or 0.0)
    stability = float(trajectory_data.get("stability_score") or 0.0)
    volatility = float(trajectory_data.get("volatility_score") or 0.0)

    wealth_building_score = round(
        min(1.0, 0.38 * natal_score + 0.24 * earning + 0.24 * retention + 0.14 * stability),
        3,
    )
    wealth_building_outlook = _support_label(wealth_building_score)

    current = _safe_dict(timing_data.get("current"))
    past = _safe_dict(timing_data.get("past"))
    future = _safe_dict(timing_data.get("future"))
    current_score = current.get("score")
    future_window = future.get("strongest_window")
    past_window = past.get("strongest_window")

    current_outlook = (
        _support_label(float(current_score)) if isinstance(current_score, (int, float))
        else "timing unavailable"
    )

    primary_source = source_data.get("primary_source")
    secondary_source = source_data.get("secondary_source")
    accumulation_pattern = trajectory_data.get("accumulation_pattern")
    life_phase_pattern = trajectory_data.get("life_phase_pattern")
    balance = trajectory_data.get("earning_retention_balance")
    primary_challenge = challenge_data.get("primary_challenge")
    recovery_outlook = challenge_data.get("recovery_outlook")

    # A concise high-level conclusion, while retaining all component outputs for
    # richer UI/API responses and follow-up questions.
    summary_parts = [
        f"Overall wealth-building support is {wealth_building_outlook}",
    ]
    if primary_source:
        summary_parts.append(f"the leading symbolic wealth channel is {str(primary_source).replace('_', ' ')}")
    if accumulation_pattern:
        summary_parts.append(f"the accumulation pattern is {str(accumulation_pattern).replace('_', ' ')}")
    if primary_challenge:
        summary_parts.append(f"the main pressure theme is {str(primary_challenge).replace('_', ' ')}")
    summary_parts.append(f"the current timing backdrop is {current_outlook}")

    return {
        "available": True,
        "event": "finance_synthesis",
        "model_version": "v1",
        "wealth_building_score": wealth_building_score,
        "wealth_building_outlook": wealth_building_outlook,
        "primary_wealth_source": primary_source,
        "secondary_wealth_source": secondary_source,
        "accumulation_pattern": accumulation_pattern,
        "life_phase_pattern": life_phase_pattern,
        "earning_retention_balance": balance,
        "earning_capacity_score": earning,
        "retention_score": retention,
        "stability_score": stability,
        "volatility_score": volatility,
        "primary_financial_challenge": primary_challenge,
        "recovery_outlook": recovery_outlook,
        "current_timing_outlook": current_outlook,
        "strongest_past_window": past_window,
        "strongest_future_window": future_window,
        "components": {
            "natal": natal,
            "source_of_wealth": source,
            "trajectory": trajectory,
            "timing": timing,
            "challenges_recovery": challenges,
        },
        "answer": ". ".join(summary_parts) + ".",
        "limitation": (
            "This synthesis describes symbolic astrological tendencies only. It is not financial advice and does not "
            "guarantee wealth, income, savings, investment returns, inheritance, losses, recovery or any financial outcome."
        ),
    }
