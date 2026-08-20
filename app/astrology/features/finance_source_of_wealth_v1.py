from __future__ import annotations

from typing import Any

from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1


SOURCE_LABELS = {
    "salary_career": "salary, career and profession-linked income",
    "business_entrepreneurship": "business, entrepreneurship and self-driven commercial activity",
    "investments_speculation": "investment, trading, speculation and creative-risk activity",
    "property_assets": "property, tangible assets and long-term asset accumulation",
    "inheritance_shared_wealth": "inheritance, spouse/partner resources and shared wealth",
    "networks_multiple_income": "networks, scaling, side income and multiple-income opportunities",
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


def analyze_finance_source_of_wealth_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Rank likely symbolic channels through which financial growth may manifest.

    This is descriptive astrological pattern analysis only. It does not recommend
    investments, businesses, jobs, leverage, property purchases or financial actions.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    natal = analyze_finance_wealth_v1(chart)
    if not natal.get("available"):
        return {
            "available": False,
            "event": "finance_source_of_wealth",
            "model_version": "v1",
            "reason": "Finance natal foundation is unavailable.",
        }

    scores = {key: 0.0 for key in SOURCE_LABELS}
    evidence: list[dict[str, Any]] = []

    # Career/salary: 2nd + 10th + 11th links and Saturn/Mercury support.
    for house_no, weight in ((2, 0.24), (10, 0.32), (11, 0.24)):
        lord = _house_lord(chart, house_no)
        if lord:
            ph = _planet_house(chart, lord)
            if ph in {2, 6, 10, 11}:
                scores["salary_career"] += weight
                evidence.append({"source": "salary_career", "rule": "career_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Business: strong 3rd/7th/10th/11th links, with Mercury/Mars emphasis.
    for house_no, weight in ((3, 0.18), (7, 0.26), (10, 0.24), (11, 0.22)):
        lord = _house_lord(chart, house_no)
        if lord:
            ph = _planet_house(chart, lord)
            if ph in {3, 7, 10, 11}:
                scores["business_entrepreneurship"] += weight
                evidence.append({"source": "business_entrepreneurship", "rule": "business_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Investments/speculation: 5th + 8th + 11th, plus Mercury/Venus/Jupiter support.
    for house_no, weight in ((5, 0.34), (8, 0.16), (11, 0.22)):
        lord = _house_lord(chart, house_no)
        if lord:
            ph = _planet_house(chart, lord)
            if ph in {2, 5, 8, 9, 11}:
                scores["investments_speculation"] += weight
                evidence.append({"source": "investments_speculation", "rule": "speculation_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Property/assets: 4th + 2nd + 11th, supported by Saturn/Venus/Mars.
    for house_no, weight in ((4, 0.36), (2, 0.18), (11, 0.18)):
        lord = _house_lord(chart, house_no)
        if lord:
            ph = _planet_house(chart, lord)
            if ph in {2, 4, 9, 10, 11}:
                scores["property_assets"] += weight
                evidence.append({"source": "property_assets", "rule": "property_house_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Inheritance/shared wealth: 8th + 7th + 2nd.
    for house_no, weight in ((8, 0.42), (7, 0.18), (2, 0.14)):
        lord = _house_lord(chart, house_no)
        if lord:
            ph = _planet_house(chart, lord)
            if ph in {2, 7, 8, 11}:
                scores["inheritance_shared_wealth"] += weight
                evidence.append({"source": "inheritance_shared_wealth", "rule": "shared_wealth_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Networks/multiple income: 11th + 3rd + 2nd, with Mercury/Jupiter support.
    for house_no, weight in ((11, 0.38), (3, 0.18), (2, 0.16)):
        lord = _house_lord(chart, house_no)
        if lord:
            ph = _planet_house(chart, lord)
            if ph in {2, 3, 10, 11}:
                scores["networks_multiple_income"] += weight
                evidence.append({"source": "networks_multiple_income", "rule": "network_income_link", "house": house_no, "lord": lord, "lord_house": ph})

    # Natural significator nudges. These are deliberately small and bounded.
    nudges = {
        "Mercury": ("business_entrepreneurship", "networks_multiple_income", "salary_career"),
        "Jupiter": ("investments_speculation", "networks_multiple_income", "inheritance_shared_wealth"),
        "Venus": ("property_assets", "investments_speculation", "inheritance_shared_wealth"),
        "Saturn": ("salary_career", "property_assets"),
        "Mars": ("business_entrepreneurship", "property_assets"),
    }
    for planet, sources in nudges.items():
        ph = _planet_house(chart, planet)
        if ph in {2, 4, 5, 7, 8, 9, 10, 11}:
            for source in sources:
                scores[source] += 0.07
                evidence.append({"source": source, "rule": "natural_significator_support", "planet": planet, "house": ph})

    scores = {key: round(min(1.0, value), 3) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary_source, primary_score = ranked[0]
    secondary_source, secondary_score = ranked[1]

    return {
        "available": True,
        "event": "finance_source_of_wealth",
        "model_version": "v1",
        "primary_source": primary_source,
        "primary_source_label": SOURCE_LABELS[primary_source],
        "primary_score": primary_score,
        "secondary_source": secondary_source,
        "secondary_source_label": SOURCE_LABELS[secondary_source],
        "secondary_score": secondary_score,
        "source_scores": scores,
        "ranked_sources": [
            {"source": source, "label": SOURCE_LABELS[source], "score": score}
            for source, score in ranked
        ],
        "evidence": evidence,
        "answer": (
            f"The strongest symbolic financial channel is {SOURCE_LABELS[primary_source]}, "
            f"followed by {SOURCE_LABELS[secondary_source]}. These are comparative chart themes, not guarantees."
        ),
        "limitation": (
            "This is astrological pattern analysis only. It is not financial advice and does not recommend any job, "
            "business, investment, property transaction, borrowing, leverage or asset allocation decision."
        ),
    }
