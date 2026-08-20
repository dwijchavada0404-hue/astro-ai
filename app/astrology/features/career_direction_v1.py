from __future__ import annotations

from typing import Any

from app.astrology.features.career_reasoning_v1 import analyze_career_v1


DIRECTION_LABELS = {
    "finance_audit_risk": "finance, audit, risk, compliance and analytical control functions",
    "technology_data": "technology, software, data, systems and digital problem-solving",
    "management_leadership": "management, administration, leadership and organizational responsibility",
    "consulting_advisory": "consulting, advisory, strategy, professional services and client-facing problem-solving",
    "law_governance": "law, governance, regulation, policy and institutional control",
    "medicine_healing": "medicine, healthcare, healing, diagnostics and service-oriented care",
    "creative_media": "creative, design, media, communication and expressive professions",
    "research_academia": "research, education, academia, writing and knowledge-intensive work",
    "government_public_service": "government, public administration, civil service and institutional authority",
    "entrepreneurship_commerce": "entrepreneurship, commerce, sales, independent business and market-building",
    "foreign_mnc": "foreign-linked, multinational, cross-border or globally distributed work environments",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _house_lord(chart: dict[str, Any], house_no: int) -> str | None:
    houses = _safe_dict(chart.get("houses"))
    house = _safe_dict(houses.get(str(house_no)) or houses.get(house_no))
    lord = house.get("lord")
    return lord if isinstance(lord, str) and lord else None


def _lord_house(chart: dict[str, Any], house_no: int) -> tuple[str | None, int | None]:
    lord = _house_lord(chart, house_no)
    return lord, _planet_house(chart, lord) if lord else None


def analyze_career_direction_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Rank symbolic professional directions from natal career signatures."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    career = analyze_career_v1(chart)
    if not career.get("available"):
        return {
            "available": False,
            "event": "career_direction",
            "model_version": "v1",
            "reason": "Career natal foundation is unavailable.",
        }

    scores = {key: 0.0 for key in DIRECTION_LABELS}
    evidence: list[dict[str, Any]] = []

    # House-link rules. These are comparative heuristics, intentionally bounded.
    house_rules = [
        (2, {2, 6, 10, 11}, ("finance_audit_risk", "consulting_advisory"), 0.12),
        (3, {3, 5, 10, 11}, ("technology_data", "creative_media", "entrepreneurship_commerce"), 0.10),
        (5, {3, 5, 9, 10, 11}, ("research_academia", "creative_media", "technology_data"), 0.11),
        (6, {2, 6, 8, 10, 11}, ("finance_audit_risk", "law_governance", "medicine_healing"), 0.13),
        (7, {3, 7, 10, 11}, ("consulting_advisory", "entrepreneurship_commerce"), 0.12),
        (8, {6, 8, 10, 11}, ("finance_audit_risk", "law_governance", "research_academia", "medicine_healing"), 0.09),
        (9, {5, 9, 10, 11, 12}, ("research_academia", "law_governance", "foreign_mnc"), 0.11),
        (10, {2, 3, 6, 7, 9, 10, 11}, ("management_leadership", "consulting_advisory"), 0.16),
        (11, {2, 3, 7, 10, 11}, ("management_leadership", "entrepreneurship_commerce", "finance_audit_risk"), 0.12),
        (12, {7, 9, 10, 12}, ("foreign_mnc", "research_academia", "medicine_healing"), 0.10),
    ]
    for house_no, supportive_houses, directions, weight in house_rules:
        lord, placed_house = _lord_house(chart, house_no)
        if lord and placed_house in supportive_houses:
            for direction in directions:
                scores[direction] += weight
                evidence.append({
                    "direction": direction,
                    "rule": "house_lord_profession_link",
                    "house": house_no,
                    "lord": lord,
                    "lord_house": placed_house,
                })

    # Small natural-significator nudges.
    significators = {
        "Mercury": ("technology_data", "finance_audit_risk", "consulting_advisory", "entrepreneurship_commerce"),
        "Jupiter": ("research_academia", "consulting_advisory", "law_governance", "management_leadership"),
        "Saturn": ("finance_audit_risk", "law_governance", "government_public_service", "management_leadership"),
        "Sun": ("management_leadership", "government_public_service", "law_governance"),
        "Mars": ("technology_data", "entrepreneurship_commerce", "medicine_healing"),
        "Venus": ("creative_media", "consulting_advisory"),
        "Moon": ("medicine_healing", "creative_media", "government_public_service"),
        "Rahu": ("technology_data", "foreign_mnc", "entrepreneurship_commerce"),
    }
    for planet, directions in significators.items():
        house = _planet_house(chart, planet)
        if house in {1, 2, 3, 5, 6, 7, 9, 10, 11, 12}:
            for direction in directions:
                scores[direction] += 0.06
                evidence.append({
                    "direction": direction,
                    "rule": "career_significator_support",
                    "planet": planet,
                    "house": house,
                })

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary, primary_score = ranked[0]
    secondary, secondary_score = ranked[1]
    tertiary, tertiary_score = ranked[2]

    return {
        "available": True,
        "event": "career_direction",
        "model_version": "v1",
        "primary_direction": primary,
        "primary_direction_label": DIRECTION_LABELS[primary],
        "primary_score": primary_score,
        "secondary_direction": secondary,
        "secondary_direction_label": DIRECTION_LABELS[secondary],
        "secondary_score": secondary_score,
        "tertiary_direction": tertiary,
        "tertiary_direction_label": DIRECTION_LABELS[tertiary],
        "tertiary_score": tertiary_score,
        "direction_scores": scores,
        "ranked_directions": [
            {"direction": direction, "label": DIRECTION_LABELS[direction], "score": score}
            for direction, score in ranked
        ],
        "evidence": evidence,
        "answer": (
            f"The strongest symbolic professional direction is {DIRECTION_LABELS[primary]}, followed by "
            f"{DIRECTION_LABELS[secondary]} and {DIRECTION_LABELS[tertiary]}."
        ),
        "limitation": (
            "This is astrological pattern analysis only. It does not guarantee suitability, employment, promotion, "
            "income or success in any profession and should not replace education, skills, experience or career advice."
        ),
    }
