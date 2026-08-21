from __future__ import annotations

from typing import Any

from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1


CAREER_DIRECTIONS: dict[str, str] = {
    "management_leadership": "management, leadership, administration and decision-making roles",
    "finance_commerce_analytics": "finance, commerce, audit, banking, accounting and analytical roles",
    "technology_engineering": "technology, engineering, systems, technical and problem-solving roles",
    "law_governance_compliance": "law, governance, regulation, compliance and public-administration roles",
    "consulting_communication": "consulting, advisory, communication, sales and client-facing roles",
    "creative_media_design": "creative, media, design, branding and expressive professions",
    "healthcare_service": "healthcare, healing, clinical support and service-oriented professions",
    "research_academia": "research, academia, teaching, knowledge and specialist-depth roles",
    "entrepreneurship_commercial": "entrepreneurship, independent practice, partnerships and commercial ventures",
}

ENVIRONMENTS: dict[str, str] = {
    "structured_organisation": "structured organisations and established institutions",
    "independent_practice": "independent practice, entrepreneurship or self-directed work",
    "foreign_mnc": "foreign-linked, multinational, cross-border or globally networked environments",
    "public_institutional": "government, regulated, public-sector or institution-heavy environments",
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


def analyze_career_direction_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Rank broad profession directions and work environments from natal patterns.

    This layer is intentionally comparative: it identifies families of work that
    receive more symbolic support in the supplied chart. It does not claim that a
    person must enter a particular profession or that any field guarantees success.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    foundation = analyze_career_profession_v1(chart)
    if not foundation.get("available"):
        return {
            "available": False,
            "event": "career_direction",
            "model_version": "v1",
            "reason": "Career natal foundation is unavailable.",
        }

    scores = {key: 0.0 for key in CAREER_DIRECTIONS}
    env_scores = {key: 0.0 for key in ENVIRONMENTS}
    evidence: list[dict[str, Any]] = []

    def add_house_links(direction: str, rules: tuple[tuple[int, float, set[int]], ...]) -> None:
        for house_no, weight, supported_houses in rules:
            lord, placed = _lord_house(chart, house_no)
            if lord and placed in supported_houses:
                scores[direction] += weight
                evidence.append({
                    "rule": "career_direction_house_link",
                    "direction": direction,
                    "house": house_no,
                    "lord": lord,
                    "lord_house": placed,
                })

    add_house_links("management_leadership", (
        (10, 0.30, {1, 5, 9, 10, 11}), (1, 0.16, {1, 9, 10, 11}),
        (9, 0.14, {1, 5, 9, 10, 11}), (11, 0.12, {9, 10, 11}),
    ))
    add_house_links("finance_commerce_analytics", (
        (2, 0.25, {2, 5, 6, 10, 11}), (5, 0.15, {2, 5, 6, 10, 11}),
        (6, 0.18, {2, 6, 10, 11}), (10, 0.18, {2, 6, 10, 11}), (11, 0.14, {2, 10, 11}),
    ))
    add_house_links("technology_engineering", (
        (3, 0.20, {3, 6, 10, 11}), (5, 0.18, {3, 5, 6, 10, 11}),
        (6, 0.16, {3, 6, 10, 11}), (10, 0.22, {3, 6, 10, 11}),
    ))
    add_house_links("law_governance_compliance", (
        (6, 0.18, {6, 9, 10, 11}), (9, 0.26, {6, 9, 10, 11}),
        (10, 0.22, {6, 9, 10, 11}), (7, 0.12, {6, 7, 9, 10}),
    ))
    add_house_links("consulting_communication", (
        (2, 0.14, {2, 3, 5, 7, 10, 11}), (3, 0.26, {2, 3, 5, 7, 10, 11}),
        (7, 0.20, {3, 7, 10, 11}), (10, 0.16, {3, 7, 10, 11}),
    ))
    add_house_links("creative_media_design", (
        (3, 0.16, {3, 5, 7, 10, 11}), (5, 0.32, {3, 5, 7, 10, 11}),
        (7, 0.12, {3, 5, 7, 10}), (10, 0.14, {3, 5, 7, 10, 11}),
    ))
    add_house_links("healthcare_service", (
        (6, 0.28, {6, 8, 10, 12}), (8, 0.18, {6, 8, 10, 12}),
        (10, 0.18, {6, 8, 10, 12}), (12, 0.14, {6, 8, 10, 12}),
    ))
    add_house_links("research_academia", (
        (5, 0.18, {5, 8, 9, 10, 12}), (8, 0.18, {5, 8, 9, 10, 12}),
        (9, 0.28, {5, 8, 9, 10, 12}), (10, 0.14, {5, 8, 9, 10, 12}),
    ))
    add_house_links("entrepreneurship_commercial", (
        (3, 0.20, {1, 3, 7, 10, 11}), (7, 0.30, {1, 3, 7, 10, 11}),
        (10, 0.16, {1, 3, 7, 10, 11}), (11, 0.16, {3, 7, 10, 11}),
    ))

    planet_directions: dict[str, tuple[str, ...]] = {
        "Sun": ("management_leadership", "law_governance_compliance"),
        "Mercury": ("finance_commerce_analytics", "technology_engineering", "consulting_communication"),
        "Mars": ("technology_engineering", "management_leadership", "entrepreneurship_commercial"),
        "Jupiter": ("law_governance_compliance", "research_academia", "management_leadership"),
        "Venus": ("creative_media_design", "consulting_communication"),
        "Saturn": ("technology_engineering", "law_governance_compliance", "finance_commerce_analytics"),
        "Moon": ("healthcare_service", "consulting_communication"),
        "Rahu": ("technology_engineering", "entrepreneurship_commercial"),
    }
    for planet, directions in planet_directions.items():
        ph = _planet_house(chart, planet)
        if ph in {1, 2, 3, 5, 6, 7, 9, 10, 11}:
            for direction in directions:
                scores[direction] += 0.07
                evidence.append({"rule": "career_direction_planet_support", "planet": planet, "house": ph, "direction": direction})

    # Work-environment intelligence. These are separate from profession families.
    service_score = float(_safe_dict(foundation.get("theme_scores")).get("service_employment") or 0.0)
    enterprise_score = float(_safe_dict(foundation.get("theme_scores")).get("independent_enterprise") or 0.0)
    env_scores["structured_organisation"] += 0.55 * service_score
    env_scores["independent_practice"] += 0.55 * enterprise_score

    for house_no, weight in ((9, 0.20), (12, 0.25), (11, 0.12)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {3, 7, 9, 10, 11, 12}:
            env_scores["foreign_mnc"] += weight
            evidence.append({"rule": "foreign_environment_house_link", "house": house_no, "lord": lord, "lord_house": ph})
    rahu_house = _planet_house(chart, "Rahu")
    if rahu_house in {3, 7, 9, 10, 11, 12}:
        env_scores["foreign_mnc"] += 0.18
        evidence.append({"rule": "rahu_foreign_environment_support", "house": rahu_house})

    for house_no, weight in ((6, 0.15), (9, 0.18), (10, 0.22)):
        lord, ph = _lord_house(chart, house_no)
        if lord and ph in {6, 9, 10, 11}:
            env_scores["public_institutional"] += weight
            evidence.append({"rule": "institutional_environment_link", "house": house_no, "lord": lord, "lord_house": ph})
    if _planet_house(chart, "Sun") in {1, 6, 9, 10, 11}:
        env_scores["public_institutional"] += 0.12

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    env_scores = {key: round(min(1.0, value), 3) for key, value in env_scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    ranked_env = sorted(env_scores.items(), key=lambda item: item[1], reverse=True)

    primary, primary_score = ranked[0]
    secondary, secondary_score = ranked[1]
    primary_env, primary_env_score = ranked_env[0]

    return {
        "available": True,
        "event": "career_direction",
        "model_version": "v1",
        "primary_direction": primary,
        "primary_direction_label": CAREER_DIRECTIONS[primary],
        "primary_score": primary_score,
        "secondary_direction": secondary,
        "secondary_direction_label": CAREER_DIRECTIONS[secondary],
        "secondary_score": secondary_score,
        "direction_scores": scores,
        "ranked_directions": [
            {"direction": key, "label": CAREER_DIRECTIONS[key], "score": score}
            for key, score in ranked
        ],
        "primary_environment": primary_env,
        "primary_environment_label": ENVIRONMENTS[primary_env],
        "primary_environment_score": primary_env_score,
        "environment_scores": env_scores,
        "ranked_environments": [
            {"environment": key, "label": ENVIRONMENTS[key], "score": score}
            for key, score in ranked_env
        ],
        "evidence": evidence,
        "answer": (
            f"The strongest profession family is {CAREER_DIRECTIONS[primary]}, followed by "
            f"{CAREER_DIRECTIONS[secondary]}. The strongest work-environment theme is {ENVIRONMENTS[primary_env]}."
        ),
        "limitation": (
            "This is symbolic astrological pattern analysis. It does not prescribe a profession or guarantee "
            "employment, suitability, income, recognition, business success or career outcomes in any field."
        ),
    }
