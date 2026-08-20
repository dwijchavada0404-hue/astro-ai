from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.career_event_timing import analyze_career_event_timing
from app.astrology.features.career_events import analyze_career_events
from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1
from app.astrology.features.career_timing_v1 import analyze_career_timing_v1


EVENT_MAP = {
    "promotion": "promotion_recognition",
    "job_change": "job_change",
    "new_job": "job_change",
    "job_loss_challenge": "career_pressure_challenge",
    "foreign_work": "foreign_international_opportunity",
}

EVENT_LABELS = {
    "promotion": "promotion, recognition or increased responsibility",
    "job_change": "job change or professional transition",
    "new_job": "new employment or entry into a different professional setup",
    "job_loss_challenge": "career pressure, disruption or employment challenge",
    "foreign_work": "foreign-linked, multinational, remote or international work opportunity",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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


def _natal_event_strength(natal_event: dict[str, Any]) -> float:
    scores = _safe_dict(natal_event.get("scores"))
    positive = _safe_float(scores.get("positive_score"))
    theme = _safe_float(scores.get("theme_score"))
    challenge = _safe_float(scores.get("challenge_score"))
    raw = positive + theme * 0.5 + challenge * 0.35
    return round(min(1.0, raw / 2.0), 3)


def _best_periods_by_time(
    periods: list[dict[str, Any]],
    reference_moment: datetime,
) -> dict[str, dict[str, Any] | None]:
    buckets: dict[str, list[dict[str, Any]]] = {"past": [], "present": [], "future": []}
    for period in periods:
        start = _parse_dt(period.get("start"), reference_moment.tzinfo)
        end = _parse_dt(period.get("end"), reference_moment.tzinfo)
        if not start or not end or end <= start:
            continue
        enriched = dict(period)
        enriched["normalized_score"] = round(min(1.0, _safe_float(period.get("score")) / 2.5), 3)
        if start <= reference_moment <= end:
            buckets["present"].append(enriched)
        elif end < reference_moment:
            buckets["past"].append(enriched)
        else:
            buckets["future"].append(enriched)

    def best(items: list[dict[str, Any]]) -> dict[str, Any] | None:
        return max(items, key=lambda item: (_safe_float(item.get("normalized_score")), str(item.get("start") or "")), default=None)

    return {key: best(items) for key, items in buckets.items()}


def _event_outlook(score: float, challenge_event: bool = False) -> str:
    if challenge_event:
        if score >= 0.75:
            return "elevated_challenge"
        if score >= 0.45:
            return "moderate_challenge"
        return "limited_challenge_signal"
    if score >= 0.75:
        return "strongly_active"
    if score >= 0.5:
        return "active"
    if score >= 0.25:
        return "mildly_active"
    return "weak_signal"


def analyze_career_event_intelligence_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Synthesize natal and dasha evidence for major career-event categories.

    The engine ranks symbolic event windows. A past high-scoring window is never
    treated as evidence that the corresponding real-world event actually happened.
    Future scores indicate astrological activation only, not event probabilities.
    """
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
            "event": "career_event_intelligence",
            "model_version": "v1",
            "reason": "Career natal foundation is unavailable.",
        }

    timing = analyze_career_timing_v1(chart, reference_moment)
    natal_events = analyze_career_events(chart)
    event_timing = analyze_career_event_timing(chart)

    natal_map = _safe_dict(natal_events.get("events"))
    timing_map = _safe_dict(event_timing.get("events")) if event_timing.get("available") else {}
    foundation_scores = _safe_dict(foundation.get("theme_scores"))

    results: dict[str, dict[str, Any]] = {}
    for output_event, legacy_event in EVENT_MAP.items():
        natal_event = _safe_dict(natal_map.get(legacy_event))
        natal_strength = _natal_event_strength(natal_event)
        periods = _safe_list(_safe_dict(timing_map.get(legacy_event)).get("periods"))
        windows = _best_periods_by_time(periods, reference_moment)

        # New-job intelligence is distinct from generic job-change intelligence:
        # it additionally requires employment/service symbolism from the natal foundation.
        employment_support = _safe_float(foundation_scores.get("service_employment")) if output_event == "new_job" else 0.0
        challenge_event = output_event == "job_loss_challenge"

        synthesized_windows: dict[str, dict[str, Any]] = {}
        for bucket in ("past", "present", "future"):
            selected = windows.get(bucket)
            generic_period = None
            if timing.get("available"):
                if bucket == "past":
                    generic_period = _safe_dict(_safe_dict(timing.get("past")).get("strongest_period"))
                elif bucket == "present":
                    generic_period = _safe_dict(_safe_dict(timing.get("present")).get("active_period"))
                else:
                    generic_period = _safe_dict(_safe_dict(timing.get("future")).get("strongest_period"))

            event_period_score = _safe_float(_safe_dict(selected).get("normalized_score"))
            generic_support = _safe_float(generic_period.get("career_support_score"))
            generic_transition = _safe_float(generic_period.get("transition_score"))

            if challenge_event:
                score = natal_strength * 0.45 + event_period_score * 0.35 + generic_transition * 0.20
            elif output_event in {"job_change", "new_job"}:
                score = natal_strength * 0.30 + event_period_score * 0.35 + generic_transition * 0.20 + generic_support * 0.15
            else:
                score = natal_strength * 0.35 + event_period_score * 0.40 + generic_support * 0.25

            if output_event == "new_job":
                score = score * 0.82 + employment_support * 0.18

            score = round(min(1.0, score), 3)
            synthesized_windows[bucket] = {
                "score": score,
                "outlook": _event_outlook(score, challenge_event=challenge_event),
                "event_specific_period": selected,
                "career_timing_period": generic_period or None,
                "historical_status": "unconfirmed" if bucket == "past" else None,
            }

        results[output_event] = {
            "label": EVENT_LABELS[output_event],
            "natal_strength": natal_strength,
            "natal_outlook": natal_event.get("outlook"),
            "natal_indicators": _safe_list(natal_event.get("indicators")),
            "employment_support": round(employment_support, 3) if output_event == "new_job" else None,
            "past": synthesized_windows["past"],
            "present": synthesized_windows["present"],
            "future": synthesized_windows["future"],
        }

    return {
        "available": True,
        "event": "career_event_intelligence",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": results,
        "timing_available": bool(timing.get("available")),
        "event_specific_timing_available": bool(event_timing.get("available")),
        "historical_validation": {
            "status": "unconfirmed",
            "rule": (
                "Past event windows describe astrological activation only. AstroAI must not state that a promotion, "
                "job change, new job, job loss or foreign-work event occurred unless the user confirms it."
            ),
        },
        "answer": (
            "Career event themes are ranked from natal evidence and available dasha timing. Scores represent symbolic "
            "activation strength, not the probability that a real-world career event will occur."
        ),
        "limitation": (
            "This astrology layer does not guarantee promotion, a new job, job change, foreign work or continued employment. "
            "A challenge signal must not be presented as a prediction of termination, unemployment or financial loss."
        ),
    }
