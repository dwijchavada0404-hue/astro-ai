from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from app.astrology.features.education_learning_synthesis_v1 import analyze_education_learning_synthesis_v1
from app.astrology.features.friends_social_community_synthesis_v1 import analyze_friends_social_community_synthesis_v1
from app.astrology.features.life_settlement_synthesis_v1 import analyze_life_settlement_synthesis_v1
from app.astrology.features.life_settlement_timing_v1 import analyze_life_settlement_timing_v1
from app.astrology.features.parents_elders_synthesis_v1 import analyze_parents_elders_synthesis_v1
from app.astrology.features.purpose_personal_growth_synthesis_v1 import analyze_purpose_personal_growth_synthesis_v1
from app.astrology.features.siblings_communication_synthesis_v1 import analyze_siblings_communication_synthesis_v1
from app.astrology.features.travel_journeys_synthesis_v1 import analyze_travel_journeys_synthesis_v1


SUPPORTING_DOMAINS: tuple[tuple[str, str, Callable[..., dict[str, Any]]], ...] = (
    ("education_learning", "Education & Learning", analyze_education_learning_synthesis_v1),
    ("purpose_personal_growth", "Purpose & Personal Growth", analyze_purpose_personal_growth_synthesis_v1),
    ("friends_social_community", "Friends, Social & Community", analyze_friends_social_community_synthesis_v1),
    ("siblings_communication", "Siblings & Communication", analyze_siblings_communication_synthesis_v1),
    ("parents_elders", "Parents & Elders", analyze_parents_elders_synthesis_v1),
    ("travel_journeys", "Travel & Journeys", analyze_travel_journeys_synthesis_v1),
)


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _support_score(name: str, result: dict[str, Any]) -> float:
    candidates: dict[str, tuple[str, ...]] = {
        "education_learning": ("education_development_score", "learning_development_score", "confidence"),
        "purpose_personal_growth": ("purpose_growth_score", "personal_growth_score", "confidence"),
        "friends_social_community": ("social_support_score", "community_score", "confidence"),
        "siblings_communication": ("communication_development_score", "sibling_relationship_score", "confidence"),
        "parents_elders": ("adaptability_score", "support_continuity_score", "confidence"),
        "travel_journeys": ("travel_adaptability", "confidence"),
    }
    for key in candidates[name]:
        if result.get(key) is not None:
            return _bounded(_safe_float(result.get(key)))
    scores = result.get("scores") if isinstance(result.get("scores"), dict) else {}
    if scores:
        values = [_safe_float(value) for value in scores.values()]
        return _bounded(sum(values) / len(values)) if values else 0.0
    return 0.55 if result.get("available") else 0.0


def analyze_life_settlement_stability_v1(chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    """Add broad stability context without allowing supporting domains to define 'settled'."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    core = analyze_life_settlement_synthesis_v1(chart, reference_moment)
    if not core.get("available"):
        return {
            "available": False,
            "event": "life_settlement_stability",
            "model_version": "v1",
            "reason": "Core Life Settlement synthesis is unavailable.",
            "core_synthesis": core,
        }

    timing = analyze_life_settlement_timing_v1(chart, reference_moment)
    supporting_components: dict[str, dict[str, Any]] = {}
    supporting_scores: dict[str, float] = {}
    collection_errors: list[dict[str, str]] = []
    labels: dict[str, str] = {}

    for name, label, fn in SUPPORTING_DOMAINS:
        labels[name] = label
        try:
            result = fn(chart, reference_moment)
            if not isinstance(result, dict):
                raise TypeError("supporting synthesis did not return a dictionary")
        except Exception as exc:
            result = {"available": False, "reason": "Supporting synthesis could not be collected."}
            collection_errors.append({"domain": name, "error_type": type(exc).__name__, "message": str(exc)})
        supporting_components[name] = result
        if result.get("available"):
            supporting_scores[name] = _support_score(name, result)

    core_score = _bounded(_safe_float(core.get("life_settlement_score")))
    core_coverage = _bounded(_safe_float(core.get("coverage")))
    supporting_coverage = len(supporting_scores) / len(SUPPORTING_DOMAINS)
    supporting_mean = (
        sum(supporting_scores.values()) / len(supporting_scores)
        if supporting_scores
        else 0.0
    )
    convergence = 0.0
    strongest_window = timing.get("strongest_convergence_window") if isinstance(timing, dict) else None
    if isinstance(strongest_window, dict):
        convergence = _bounded(_safe_float(strongest_window.get("convergence_score")))

    overall_stability = _bounded(
        0.72 * core_score
        + 0.18 * convergence
        + 0.10 * supporting_mean
    )
    confidence = _bounded(
        0.38
        + 0.30 * core_coverage
        + 0.14 * supporting_coverage
        + 0.18 * _safe_float(core.get("confidence"))
    )

    if core_score < 0.45:
        outlook = "core_foundations_still_developing"
    elif overall_stability >= 0.72 and convergence >= 0.60:
        outlook = "broad_stability_with_cross_domain_convergence"
    elif overall_stability >= 0.58:
        outlook = "moderate_broad_stability"
    else:
        outlook = "mixed_stability_context"

    strongest_supporting = [
        name for name, _ in sorted(supporting_scores.items(), key=lambda item: item[1], reverse=True)[:2]
    ]
    support_text = ", ".join(labels[name] for name in strongest_supporting) if strongest_supporting else "no additional supporting domains"

    return {
        "available": True,
        "event": "life_settlement_stability",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "overall_stability_score": overall_stability,
        "core_settlement_score": core_score,
        "timing_convergence_score": convergence,
        "supporting_context_score": _bounded(supporting_mean),
        "confidence": confidence,
        "outlook": outlook,
        "core_domain_coverage": core_coverage,
        "supporting_domain_coverage": round(supporting_coverage, 3),
        "supporting_scores": supporting_scores,
        "strongest_supporting_domains": strongest_supporting,
        "core_synthesis": core,
        "timing": timing,
        "supporting_components": supporting_components,
        "collection_errors": collection_errors,
        "design_principle": (
            "Career, Finance, Marriage/Relationships, Property/Home, Family/Children and Location/Settlement define the core settlement construct. "
            "Education, Purpose, Social life, Siblings/Communication, Parents/Elders and Travel provide supporting stability context only and cannot substitute for missing core foundations."
        ),
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known achieved milestones and real-world history override astrological assumptions. Historical astrology may help interpret confirmed milestones, but must never mark an unconfirmed milestone as achieved or move an achieved milestone back to pending."
            ),
        },
        "answer": (
            f"Overall symbolic life stability is {outlook.replace('_', ' ')}. Core settlement remains the deciding layer; "
            f"the strongest additional context currently comes from {support_text}."
        ),
        "limitation": (
            "This is a symbolic cross-domain stability model, not a guarantee that life will 'fall into place'. Supporting domains cannot convert weak core settlement evidence into a settled outcome, and no score can override known real-world facts or user-confirmed milestones."
        ),
    }
