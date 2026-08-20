from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.career_direction_intelligence_v1 import analyze_career_direction_v1
from app.astrology.features.career_event_intelligence_v1 import analyze_career_event_intelligence_v1
from app.astrology.features.career_job_business_intelligence_v1 import analyze_job_vs_business_v1
from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1
from app.astrology.features.career_timing_v1 import analyze_career_timing_v1
from app.astrology.features.career_trajectory_v1 import analyze_career_trajectory_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _support_label(score: float) -> str:
    if score >= 0.72:
        return "strong"
    if score >= 0.52:
        return "moderate"
    return "limited"


def _future_event_highlight(events: dict[str, Any]) -> tuple[str | None, float]:
    candidates: list[tuple[str, float]] = []
    for event_name in ("promotion", "job_change", "new_job", "foreign_work"):
        event = _safe_dict(events.get(event_name))
        score = _safe_float(_safe_dict(event.get("future")).get("score"))
        candidates.append((event_name, score))
    if not candidates:
        return None, 0.0
    return max(candidates, key=lambda item: item[1])


def analyze_career_synthesis_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
    lookback_years: int = 3,
    lookahead_years: int = 5,
) -> dict[str, Any]:
    """Combine Career V1 layers into one bounded professional synthesis.

    The synthesis separates career potential, professional direction, preferred
    work structure, timing, event activation and longer-term trajectory. It does
    not convert symbolic astrology scores into guaranteed real-world outcomes.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    natal = analyze_career_profession_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "career_synthesis",
            "model_version": "v1",
            "reason": "Career natal foundation is unavailable.",
        }

    direction = analyze_career_direction_v1(chart)
    job_business = analyze_job_vs_business_v1(chart)
    timing = analyze_career_timing_v1(
        chart,
        reference_moment,
        lookback_years=lookback_years,
        lookahead_years=lookahead_years,
    )
    events = analyze_career_event_intelligence_v1(chart, reference_moment)
    trajectory = analyze_career_trajectory_v1(chart, reference_moment)

    natal_score = _safe_float(natal.get("dominant_score"))
    progression = _safe_float(trajectory.get("progression_score"))
    stability = _safe_float(trajectory.get("stability_score"))
    resilience = _safe_float(trajectory.get("resilience_score"))
    recovery = _safe_float(trajectory.get("recovery_score"))

    present_period = _safe_dict(_safe_dict(timing.get("present")).get("active_period"))
    future_period = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period"))
    present_support = _safe_float(present_period.get("career_support_score"))
    future_support = _safe_float(future_period.get("career_support_score"))
    timing_support = max(present_support, future_support)

    career_development_score = round(
        min(
            1.0,
            0.28 * natal_score
            + 0.25 * progression
            + 0.15 * stability
            + 0.13 * resilience
            + 0.10 * recovery
            + 0.09 * timing_support,
        ),
        3,
    )
    career_development_outlook = _support_label(career_development_score)

    component_availability = {
        "natal": bool(natal.get("available")),
        "direction": bool(direction.get("available")),
        "job_vs_business": bool(job_business.get("available")),
        "timing": bool(timing.get("available")),
        "events": bool(events.get("available")),
        "trajectory": bool(trajectory.get("available")),
    }
    available_count = sum(1 for available in component_availability.values() if available)
    confidence = round(min(0.95, 0.43 + 0.085 * available_count), 2)

    event_map = _safe_dict(events.get("events"))
    strongest_future_event, strongest_future_event_score = _future_event_highlight(event_map)
    challenge_event = _safe_dict(event_map.get("job_loss_challenge"))
    future_challenge_score = _safe_float(_safe_dict(challenge_event.get("future")).get("score"))

    primary_direction = direction.get("primary_direction") if direction.get("available") else None
    primary_direction_label = direction.get("primary_direction_label") if direction.get("available") else None
    secondary_direction = direction.get("secondary_direction") if direction.get("available") else None
    secondary_direction_label = direction.get("secondary_direction_label") if direction.get("available") else None
    primary_environment = direction.get("primary_environment") if direction.get("available") else None
    primary_environment_label = direction.get("primary_environment_label") if direction.get("available") else None
    orientation = job_business.get("orientation") if job_business.get("available") else None

    summary_parts = [
        f"Overall symbolic career-development support is {career_development_outlook}",
    ]
    if primary_direction_label:
        summary_parts.append(f"the strongest profession family is {primary_direction_label}")
    if orientation:
        summary_parts.append(f"the work-structure orientation is {str(orientation).replace('_', ' ')}")
    if trajectory.get("trajectory_pattern"):
        summary_parts.append(
            f"the broader trajectory is {str(trajectory.get('trajectory_pattern')).replace('_', ' ')}"
        )
    if trajectory.get("near_term_direction"):
        summary_parts.append(
            f"the near-term pattern is {str(trajectory.get('near_term_direction')).replace('_', ' ')}"
        )

    historical_validation = {
        "status": "unconfirmed",
        "reality_override": True,
        "rule": (
            "Past astrological career windows must remain unconfirmed unless the user supplies or confirms the real-world "
            "event. Known career history overrides predictive assumptions; astrology may only help interpret confirmed history."
        ),
    }

    return {
        "available": True,
        "event": "career_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "career_development_score": career_development_score,
        "career_development_outlook": career_development_outlook,
        "confidence": confidence,
        "component_availability": component_availability,
        "primary_direction": primary_direction,
        "primary_direction_label": primary_direction_label,
        "secondary_direction": secondary_direction,
        "secondary_direction_label": secondary_direction_label,
        "primary_environment": primary_environment,
        "primary_environment_label": primary_environment_label,
        "job_business_orientation": orientation,
        "trajectory_pattern": trajectory.get("trajectory_pattern"),
        "near_term_direction": trajectory.get("near_term_direction"),
        "progression_score": progression,
        "stability_score": stability,
        "resilience_score": resilience,
        "recovery_score": recovery,
        "current_career_support_score": present_support if timing.get("available") else None,
        "future_career_support_score": future_support if timing.get("available") else None,
        "strongest_past_period": _safe_dict(_safe_dict(timing.get("past")).get("strongest_period")) or None,
        "active_present_period": present_period or None,
        "strongest_future_period": future_period or None,
        "strongest_future_event": strongest_future_event,
        "strongest_future_event_score": round(strongest_future_event_score, 3),
        "future_challenge_score": round(future_challenge_score, 3),
        "historical_validation": historical_validation,
        "components": {
            "natal": natal,
            "direction": direction,
            "job_vs_business": job_business,
            "timing": timing,
            "events": events,
            "trajectory": trajectory,
        },
        "answer": ". ".join(summary_parts) + ".",
        "limitation": (
            "This synthesis describes symbolic astrological tendencies only. It does not guarantee employment, promotion, "
            "a new job, job change, continued employment, salary growth, business success, foreign work or recognition, "
            "and challenge signals must not be presented as predictions of termination or financial loss. It should not "
            "replace skills, experience, labour-market information or professional career advice."
        ),
    }
