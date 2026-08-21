from __future__ import annotations

from typing import Any

from app.astrology.features.career_direction_intelligence_v1 import analyze_career_direction_v1
from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1


ORIENTATION_LABELS = {
    "structured_employment": "structured employment, institutional responsibility and organisational career paths",
    "independent_business": "independent business, entrepreneurship, partnership or self-directed commercial work",
    "mixed_hybrid": "a mixed path combining organisational work with advisory, consulting, partnership or independent activity",
}


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


def _lord_house(chart: dict[str, Any], house_no: int) -> tuple[str | None, int | None]:
    lord = _house(chart, house_no).get("lord")
    if not isinstance(lord, str) or not lord:
        return None, None
    return lord, _planet_house(chart, lord)


def analyze_job_vs_business_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Compare structured-employment and independent-business natal support.

    The output is comparative and symbolic. It does not advise a user to resign,
    start a company, invest capital, or choose one livelihood over another.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    foundation = analyze_career_profession_v1(chart)
    if not foundation.get("available"):
        return {
            "available": False,
            "event": "career_job_vs_business",
            "model_version": "v1",
            "reason": "Career natal foundation is unavailable.",
        }

    direction = analyze_career_direction_v1(chart)
    scores = {
        "structured_employment": 0.0,
        "independent_business": 0.0,
    }
    evidence: list[dict[str, Any]] = []

    theme_scores = _safe_dict(foundation.get("theme_scores"))
    service = float(theme_scores.get("service_employment") or 0.0)
    enterprise = float(theme_scores.get("independent_enterprise") or 0.0)
    career_strength = float(theme_scores.get("career_strength") or 0.0)
    gains = float(theme_scores.get("gains_progression") or 0.0)

    scores["structured_employment"] += 0.42 * service + 0.14 * career_strength + 0.08 * gains
    scores["independent_business"] += 0.42 * enterprise + 0.12 * career_strength + 0.08 * gains
    evidence.extend([
        {"rule": "foundation_service_support", "score": round(service, 3)},
        {"rule": "foundation_enterprise_support", "score": round(enterprise, 3)},
    ])

    # House architecture: 6th favours employment/service; 3rd and 7th favour
    # initiative/commerce; 10th and 11th can support either depending on links.
    for house_no, weight, supported_houses in (
        (6, 0.18, {2, 6, 10, 11}),
        (10, 0.12, {2, 6, 10, 11}),
        (2, 0.08, {2, 6, 10, 11}),
    ):
        lord, placed = _lord_house(chart, house_no)
        if lord and placed in supported_houses:
            scores["structured_employment"] += weight
            evidence.append({
                "rule": "structured_house_link",
                "house": house_no,
                "lord": lord,
                "lord_house": placed,
            })

    for house_no, weight, supported_houses in (
        (3, 0.14, {1, 3, 7, 10, 11}),
        (7, 0.20, {1, 3, 7, 10, 11}),
        (10, 0.10, {1, 3, 7, 10, 11}),
        (11, 0.08, {3, 7, 10, 11}),
    ):
        lord, placed = _lord_house(chart, house_no)
        if lord and placed in supported_houses:
            scores["independent_business"] += weight
            evidence.append({
                "rule": "independent_house_link",
                "house": house_no,
                "lord": lord,
                "lord_house": placed,
            })

    # Direction layer contributes work-environment context, but is deliberately
    # subordinate to the natal foundation so the layers remain independently useful.
    env_scores = _safe_dict(direction.get("environment_scores")) if direction.get("available") else {}
    structured_env = float(env_scores.get("structured_organisation") or 0.0)
    independent_env = float(env_scores.get("independent_practice") or 0.0)
    scores["structured_employment"] += 0.18 * structured_env
    scores["independent_business"] += 0.18 * independent_env
    if structured_env:
        evidence.append({"rule": "direction_structured_environment_support", "score": round(structured_env, 3)})
    if independent_env:
        evidence.append({"rule": "direction_independent_environment_support", "score": round(independent_env, 3)})

    # Planetary significators are small nudges only, never one-planet = one-path rules.
    for planet, target, active_houses in (
        ("Saturn", "structured_employment", {2, 6, 10, 11}),
        ("Sun", "structured_employment", {1, 6, 9, 10, 11}),
        ("Mercury", "independent_business", {3, 7, 10, 11}),
        ("Mars", "independent_business", {1, 3, 7, 10, 11}),
        ("Rahu", "independent_business", {3, 7, 10, 11}),
    ):
        placed = _planet_house(chart, planet)
        if placed in active_houses:
            scores[target] += 0.05
            evidence.append({"rule": "orientation_planet_nudge", "planet": planet, "house": placed, "target": target})

    bounded = {key: round(min(1.0, max(0.0, value)), 3) for key, value in scores.items()}
    job_score = bounded["structured_employment"]
    business_score = bounded["independent_business"]
    delta = round(job_score - business_score, 3)

    if abs(delta) <= 0.12:
        orientation = "mixed_hybrid"
    elif delta > 0:
        orientation = "structured_employment"
    else:
        orientation = "independent_business"

    evidence_count = len(evidence)
    confidence = round(min(0.92, 0.48 + 0.025 * evidence_count + 0.15 * abs(delta)), 2)

    return {
        "available": True,
        "event": "career_job_vs_business",
        "model_version": "v1",
        "orientation": orientation,
        "orientation_label": ORIENTATION_LABELS[orientation],
        "job_score": job_score,
        "business_score": business_score,
        "score_delta": delta,
        "confidence": confidence,
        "evidence": evidence,
        "answer": (
            f"The chart shows a symbolic tilt toward {ORIENTATION_LABELS[orientation]}. "
            f"Structured-employment support scores {job_score:.2f} and independent-business support scores {business_score:.2f}."
        ),
        "limitation": (
            "This compares astrological career patterns only. It is not career, legal or financial advice and does not "
            "predict guaranteed success in employment or business. Real-world skills, experience, capital, risk tolerance, "
            "market conditions and personal goals should govern career decisions."
        ),
    }
