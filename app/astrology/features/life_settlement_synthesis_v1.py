from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from app.astrology.features.career_synthesis_v1 import analyze_career_synthesis_v1
from app.astrology.features.family_children_synthesis_v1 import analyze_family_children_synthesis_v1
from app.astrology.features.finance_synthesis_v1 import analyze_finance_synthesis_v1
from app.astrology.features.marriage_synthesis_reasoning_v2 import synthesize_marriage_profile_v2
from app.astrology.features.property_home_synthesis_v1 import analyze_property_home_synthesis_v1


DOMAIN_ORDER = ("career", "finance", "marriage", "property_home", "family_children")
DOMAIN_LABELS = {
    "career": "Career & Profession",
    "finance": "Finance & Wealth",
    "marriage": "Marriage & Partnership",
    "property_home": "Property & Home",
    "family_children": "Family & Children",
}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_domain_score(domain: str, result: dict[str, Any]) -> float:
    keys = {
        "career": ("career_development_score",),
        "finance": ("wealth_building_score",),
        "property_home": ("property_home_development_score",),
        "family_children": ("family_development_score",),
        "marriage": ("overall_score", "synthesis_score", "confidence"),
    }[domain]
    for key in keys:
        if result.get(key) is not None:
            return _bounded(_safe_float(result.get(key)))
    return 0.0


def _extract_confidence(result: dict[str, Any]) -> float:
    value = result.get("confidence")
    if value is not None:
        return _bounded(_safe_float(value))
    orchestration = result.get("orchestration") if isinstance(result.get("orchestration"), dict) else {}
    requested = int(orchestration.get("requested_component_count") or 0)
    collected = int(orchestration.get("collected_component_count") or 0)
    if requested > 0:
        return _bounded(0.45 + 0.45 * collected / requested)
    return 0.55 if result.get("available") else 0.0


def _collect_domain(
    name: str,
    fn: Callable[..., dict[str, Any]],
    chart: dict[str, Any],
    reference_moment: datetime,
) -> tuple[dict[str, Any], dict[str, str] | None]:
    try:
        result = fn(chart, reference_moment)
        if not isinstance(result, dict):
            raise TypeError("domain synthesis did not return a dictionary")
        return result, None
    except Exception as exc:
        return {
            "available": False,
            "event": f"{name}_synthesis",
            "reason": "The domain synthesis could not be collected.",
        }, {
            "domain": name,
            "error_type": type(exc).__name__,
            "message": str(exc),
        }


def analyze_life_settlement_synthesis_v1(
    chart: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    """Orchestrate mature domain engines into one cross-domain life synthesis.

    This layer creates no new astrological evidence. It summarizes existing
    Career, Finance, Marriage, Property/Home and Family/Children engines,
    preserves each domain's limitations, and isolates component failures.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")

    engines: dict[str, Callable[..., dict[str, Any]]] = {
        "career": analyze_career_synthesis_v1,
        "finance": analyze_finance_synthesis_v1,
        "marriage": synthesize_marriage_profile_v2,
        "property_home": analyze_property_home_synthesis_v1,
        "family_children": analyze_family_children_synthesis_v1,
    }

    components: dict[str, dict[str, Any]] = {}
    collection_errors: list[dict[str, str]] = []
    domain_scores: dict[str, float] = {}
    domain_confidence: dict[str, float] = {}

    for domain in DOMAIN_ORDER:
        result, error = _collect_domain(domain, engines[domain], chart, reference_moment)
        components[domain] = result
        if error:
            collection_errors.append(error)
        if result.get("available"):
            domain_scores[domain] = _extract_domain_score(domain, result)
            domain_confidence[domain] = _extract_confidence(result)

    available_domains = [domain for domain in DOMAIN_ORDER if components[domain].get("available")]
    if not available_domains:
        return {
            "available": False,
            "event": "life_settlement_synthesis",
            "model_version": "v1",
            "reason": "No mature life-domain synthesis was available.",
            "components": components,
            "collection_errors": collection_errors,
        }

    weighted = [
        domain_scores[domain] * max(0.35, domain_confidence[domain])
        for domain in available_domains
    ]
    weights = [max(0.35, domain_confidence[domain]) for domain in available_domains]
    settlement_score = _bounded(sum(weighted) / sum(weights)) if weights else 0.0
    coverage = len(available_domains) / len(DOMAIN_ORDER)
    confidence = _bounded(
        0.34 + 0.30 * coverage + 0.26 * (sum(domain_confidence.values()) / len(available_domains))
    )

    if settlement_score >= 0.70:
        outlook = "broadly_supportive"
    elif settlement_score >= 0.50:
        outlook = "moderately_supportive_with_mixed_areas"
    else:
        outlook = "mixed_or_developmental"

    ranked = sorted(domain_scores.items(), key=lambda item: item[1], reverse=True)
    strongest_domains = [name for name, _ in ranked[:2]]
    development_domains = [name for name, score in ranked if score < 0.50]

    current_signals: dict[str, Any] = {}
    future_signals: dict[str, Any] = {}
    for domain in available_domains:
        result = components[domain]
        current_signals[domain] = (
            result.get("active_present_period")
            or result.get("current_timing_outlook")
            or result.get("near_term_direction")
        )
        future_signals[domain] = (
            result.get("strongest_future_period")
            or result.get("strongest_future_window")
            or result.get("strongest_future_event")
        )

    strongest_labels = [DOMAIN_LABELS[name] for name in strongest_domains]
    summary = (
        f"Cross-domain symbolic settlement is {outlook.replace('_', ' ')}. "
        f"The strongest current foundations are {', '.join(strongest_labels)}."
    )
    if development_domains:
        summary += (
            " Areas that may need more deliberate real-world development are "
            + ", ".join(DOMAIN_LABELS[name] for name in development_domains)
            + "."
        )

    return {
        "available": True,
        "event": "life_settlement_synthesis",
        "model_version": "v1",
        "reference_moment": reference_moment.isoformat(),
        "life_settlement_score": settlement_score,
        "life_settlement_outlook": outlook,
        "confidence": confidence,
        "coverage": round(coverage, 3),
        "available_domains": available_domains,
        "domain_scores": domain_scores,
        "domain_confidence": domain_confidence,
        "strongest_domains": strongest_domains,
        "development_domains": development_domains,
        "current_signals": current_signals,
        "future_signals": future_signals,
        "components": components,
        "collection_errors": collection_errors,
        "historical_validation": {
            "status": "unconfirmed",
            "reality_override": True,
            "rule": (
                "Known real-world career, financial, relationship, property and family history overrides astrological inference. "
                "Past symbolic windows may only be used to interpret milestones the user has confirmed."
            ),
        },
        "answer": summary,
        "limitation": (
            "This is a cross-domain symbolic astrology synthesis, not a deterministic life forecast. It does not guarantee "
            "career success, wealth, marriage, property ownership, fertility, pregnancy, childbirth, family outcomes or a "
            "specific age/date of being 'settled'. Domain-specific medical, financial, legal and relationship boundaries remain "
            "in force, and real-world facts and decisions take priority over astrological inference."
        ),
    }
