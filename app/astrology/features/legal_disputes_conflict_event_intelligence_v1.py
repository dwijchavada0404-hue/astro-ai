from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.legal_disputes_conflict_reasoning_v1 import analyze_legal_disputes_conflict_v1
from app.astrology.features.legal_disputes_conflict_timing_v1 import analyze_legal_disputes_conflict_timing_v1


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _event(label: str, score: float, evidence: list[str]) -> dict[str, Any]:
    if score >= 0.72:
        level = "strong"
    elif score >= 0.56:
        level = "moderate"
    else:
        level = "light"
    return {
        "event": label,
        "activation_score": _b(score),
        "activation_level": level,
        "evidence": evidence,
        "historical_status": "unconfirmed",
    }


def analyze_legal_disputes_conflict_event_intelligence_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Translate legal/conflict timing into bounded symbolic event themes, not legal outcomes."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime) or reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must be a timezone-aware datetime.")

    natal = analyze_legal_disputes_conflict_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "legal_disputes_conflict_events",
            "model_version": "v1",
            "reason": "Legal, Disputes & Conflict natal foundation is unavailable.",
        }

    timing = analyze_legal_disputes_conflict_timing_v1(chart, reference_moment)
    themes = _d(natal.get("theme_scores"))
    present = _d(_d(timing.get("present")).get("active_period")) if timing.get("available") else {}
    future = _d(_d(timing.get("future")).get("strongest_period")) if timing.get("available") else {}

    def blended(theme_key: str, timing_key: str, supporting_key: str | None = None) -> float:
        value = 0.58 * _f(themes.get(theme_key)) + 0.30 * _f(future.get(timing_key))
        if supporting_key:
            value += 0.12 * _f(themes.get(supporting_key))
        else:
            value += 0.12 * _f(present.get(timing_key))
        return _b(value)

    events = {
        "dispute_engagement": _event(
            "dispute_engagement",
            blended("dispute_engagement", "dispute_activation_score", "competition_assertiveness"),
            ["6th-house/conflict axis", "dispute activation timing", "assertiveness context"],
        ),
        "negotiation_mediation": _event(
            "negotiation_mediation",
            blended("negotiation_mediation", "negotiation_support_score", "resolution_capacity"),
            ["7th-house negotiation axis", "Mercury/Venus/Jupiter support", "resolution capacity"],
        ),
        "complexity_endurance": _event(
            "complexity_endurance",
            blended("complexity_endurance", "complexity_endurance_score", "dispute_engagement"),
            ["8th-house complexity axis", "Saturn/Rahu/Ketu endurance context", "dispute-management load"],
        ),
        "principles_fairness": _event(
            "principles_fairness",
            blended("principles_fairness", "principles_fairness_score", "negotiation_mediation"),
            ["9th-house principles axis", "Jupiter/Sun fairness context", "negotiation support"],
        ),
        "competition_assertiveness": _event(
            "competition_assertiveness",
            blended("competition_assertiveness", "competition_assertiveness_score", "dispute_engagement"),
            ["6th-house competition axis", "Mars/Sun assertiveness context", "dispute engagement"],
        ),
        "resolution_capacity": _event(
            "resolution_capacity",
            blended("resolution_capacity", "resolution_support_score", "negotiation_mediation"),
            ["resolution-oriented natal signals", "Jupiter/Mercury/Venus support", "negotiation/mediation context"],
        ),
    }

    strongest = max(events.values(), key=lambda item: item["activation_score"])
    return {
        "available": True,
        "event": "legal_disputes_conflict_events",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "events": events,
        "strongest_future_event": strongest,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known legal history and actual outcomes override astrology. Symbolic activation must not be treated as proof that litigation, liability, arrest, judgment, settlement, regulatory action or another legal event occurred."
            ),
        },
        "answer": (
            f"The strongest symbolic Legal, Disputes & Conflict theme is {strongest['event'].replace('_', ' ')}, "
            "which describes conflict-management emphasis rather than a predicted legal outcome."
        ),
        "limitation": (
            "These event scores are not legal advice and cannot predict guilt, liability, court verdicts, arrest, imprisonment, criminal outcomes, regulatory action, exact dispute outcomes, settlement amounts or whether a case will be won or lost."
        ),
        "components": {"natal": natal, "timing": timing},
    }
