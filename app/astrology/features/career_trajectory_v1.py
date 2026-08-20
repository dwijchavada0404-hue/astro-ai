from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.career_event_intelligence_v1 import analyze_career_event_intelligence_v1
from app.astrology.features.career_job_business_intelligence_v1 import analyze_job_vs_business_v1
from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def analyze_career_trajectory_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Describe symbolic career progression, stability, mobility and challenge patterns."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    foundation = analyze_career_profession_v1(chart)
    if not foundation.get("available"):
        return {
            "available": False,
            "event": "career_trajectory",
            "model_version": "v1",
            "reason": "Career natal foundation is unavailable.",
        }

    events = analyze_career_event_intelligence_v1(chart, reference_moment)
    job_business = analyze_job_vs_business_v1(chart)
    themes = _safe_dict(foundation.get("theme_scores"))
    event_map = _safe_dict(events.get("events")) if events.get("available") else {}

    career_strength = _safe_float(themes.get("career_strength"))
    progression_theme = _safe_float(themes.get("gains_progression"))
    leadership = _safe_float(themes.get("leadership_authority"))
    service = _safe_float(themes.get("service_employment"))
    enterprise = _safe_float(themes.get("independent_enterprise"))
    skills = _safe_float(themes.get("skills_communication"))

    progression_score = round(min(1.0, 0.35 * career_strength + 0.35 * progression_theme + 0.18 * leadership + 0.12 * skills), 3)

    job_change = _safe_dict(event_map.get("job_change"))
    promotion = _safe_dict(event_map.get("promotion"))
    challenge = _safe_dict(event_map.get("job_loss_challenge"))

    present_change = _safe_float(_safe_dict(job_change.get("present")).get("score"))
    future_change = _safe_float(_safe_dict(job_change.get("future")).get("score"))
    present_promotion = _safe_float(_safe_dict(promotion.get("present")).get("score"))
    future_promotion = _safe_float(_safe_dict(promotion.get("future")).get("score"))
    present_challenge = _safe_float(_safe_dict(challenge.get("present")).get("score"))
    future_challenge = _safe_float(_safe_dict(challenge.get("future")).get("score"))

    mobility_score = round(min(1.0, 0.35 * max(present_change, future_change) + 0.25 * enterprise + 0.20 * skills + 0.20 * (1.0 - min(1.0, service))), 3)
    challenge_score = round(min(1.0, 0.55 * max(present_challenge, future_challenge) + 0.20 * max(present_change, future_change) + 0.15 * (1.0 - career_strength) + 0.10 * (1.0 - progression_theme)), 3)

    resilience_score = 0.0
    resilience_evidence: list[dict[str, Any]] = []
    for planet, houses, weight in (
        ("Saturn", {3, 6, 10, 11}, 0.24),
        ("Mars", {1, 3, 6, 10, 11}, 0.20),
        ("Jupiter", {1, 5, 9, 10, 11}, 0.18),
        ("Mercury", {2, 3, 5, 6, 10, 11}, 0.16),
    ):
        house = _planet_house(chart, planet)
        if house in houses:
            resilience_score += weight
            resilience_evidence.append({"rule": "career_resilience_planet_support", "planet": planet, "house": house})

    resilience_score += 0.12 * skills + 0.10 * progression_theme
    resilience_score = round(min(1.0, resilience_score), 3)

    stability_score = round(max(0.0, min(1.0, 0.40 * service + 0.25 * career_strength + 0.20 * progression_theme + 0.15 * resilience_score - 0.30 * mobility_score)), 3)
    recovery_score = round(min(1.0, 0.45 * resilience_score + 0.30 * progression_score + 0.15 * skills + 0.10 * max(future_promotion, future_change)), 3)

    if stability_score >= 0.65 and mobility_score <= 0.45:
        trajectory_pattern = "steady_structured_progression"
    elif progression_score >= 0.65 and mobility_score >= 0.55:
        trajectory_pattern = "growth_through_transitions"
    elif challenge_score >= 0.6 and recovery_score >= 0.6:
        trajectory_pattern = "cyclical_pressure_with_recovery"
    elif challenge_score >= 0.6:
        trajectory_pattern = "uneven_or_pressure_sensitive_path"
    elif enterprise >= service + 0.15:
        trajectory_pattern = "self_directed_or_independent_progression"
    else:
        trajectory_pattern = "mixed_adaptive_progression"

    if future_promotion > present_promotion + 0.08 and future_challenge <= present_challenge + 0.12:
        near_term_direction = "future_strengthening"
    elif future_challenge > present_challenge + 0.12:
        near_term_direction = "greater_future_pressure_or_restructuring"
    elif abs(future_promotion - present_promotion) <= 0.08 and abs(future_change - present_change) <= 0.08:
        near_term_direction = "broadly_similar_activation"
    else:
        near_term_direction = "mixed_transition_and_progression"

    return {
        "available": True,
        "event": "career_trajectory",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "trajectory_pattern": trajectory_pattern,
        "near_term_direction": near_term_direction,
        "progression_score": progression_score,
        "stability_score": stability_score,
        "mobility_score": mobility_score,
        "challenge_score": challenge_score,
        "resilience_score": resilience_score,
        "recovery_score": recovery_score,
        "job_business_orientation": job_business.get("orientation") if job_business.get("available") else None,
        "event_context": {
            "present_job_change_score": present_change,
            "future_job_change_score": future_change,
            "present_promotion_score": present_promotion,
            "future_promotion_score": future_promotion,
            "present_challenge_score": present_challenge,
            "future_challenge_score": future_challenge,
        },
        "evidence": {"resilience": resilience_evidence},
        "historical_rule": (
            "Historical career activation can be compared with confirmed career history, but predicted past changes, "
            "promotions or setbacks must remain unconfirmed unless supplied by the user."
        ),
        "answer": (
            f"The symbolic career trajectory is {trajectory_pattern.replace('_', ' ')}, with a near-term pattern of "
            f"{near_term_direction.replace('_', ' ')}."
        ),
        "limitation": (
            "This astrology layer describes career patterns, not guaranteed employment outcomes. Challenge or mobility "
            "scores do not predict termination, resignation, promotion, salary changes or business success."
        ),
    }
