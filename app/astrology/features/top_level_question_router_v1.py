from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from app.astrology.features.career_question_intelligence_v1 import analyze_career_question_v1
from app.astrology.features.career_router_v1 import route_career_question_v1
from app.astrology.features.education_learning_question_intelligence_v1 import analyze_education_learning_question_v1
from app.astrology.features.education_learning_router_v1 import route_education_learning_question_v1
from app.astrology.features.family_children_question_intelligence_v1 import analyze_family_children_question_v1
from app.astrology.features.family_children_router_v1 import route_family_children_question_v1
from app.astrology.features.finance_question_intelligence_v1 import analyze_finance_question_v1
from app.astrology.features.finance_router_v1 import route_finance_question_v1
from app.astrology.features.friends_social_community_question_intelligence_v1 import analyze_friends_social_community_question_v1
from app.astrology.features.friends_social_community_router_v1 import route_friends_social_community_question_v1
from app.astrology.features.life_context_v1 import reconcile_answer_with_life_context_v1
from app.astrology.features.life_settlement_answer_intelligence_v1 import answer_life_settlement_question_v1
from app.astrology.features.life_settlement_question_intelligence_v1 import analyze_life_settlement_question_v1
from app.astrology.features.location_settlement_question_intelligence_v1 import analyze_location_settlement_question_v1
from app.astrology.features.location_settlement_router_v1 import route_location_settlement_question_v1
from app.astrology.features.marriage_forecast_router_v3 import route_marriage_question_v3
from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3
from app.astrology.features.parents_elders_question_intelligence_v1 import analyze_parents_elders_question_v1
from app.astrology.features.parents_elders_router_v1 import route_parents_elders_question_v1
from app.astrology.features.property_home_question_intelligence_v1 import analyze_property_home_question_v1
from app.astrology.features.property_home_router_v1 import route_property_home_question_v1
from app.astrology.features.purpose_personal_growth_question_intelligence_v1 import analyze_purpose_personal_growth_question_v1
from app.astrology.features.purpose_personal_growth_router_v1 import route_purpose_personal_growth_question_v1
from app.astrology.features.siblings_communication_question_intelligence_v1 import analyze_siblings_communication_question_v1
from app.astrology.features.siblings_communication_router_v1 import route_siblings_communication_question_v1


DOMAIN_ORDER = (
    "life_settlement",
    "marriage",
    "career",
    "finance",
    "property_home",
    "family_children",
    "location_settlement",
    "education_learning",
    "purpose_personal_growth",
    "friends_social_community",
    "siblings_communication",
    "parents_elders",
)


def _require_reference_moment(reference_moment: datetime) -> None:
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")


def _with_context(result: dict[str, Any], life_context: dict[str, Any] | None) -> dict[str, Any]:
    return reconcile_answer_with_life_context_v1(result, life_context) if life_context is not None else result


def route_top_level_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
    life_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Route a natural-language question across mature AstroAI domains."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")
    _require_reference_moment(reference_moment)

    settlement = analyze_life_settlement_question_v1(question)
    if settlement.get("available"):
        result = answer_life_settlement_question_v1(chart, question, reference_moment)
        routed = {
            "available": bool(result.get("available")),
            "event": "life_settlement",
            "route": "life_settlement_answer_v1",
            "domain": "life_settlement",
            "understanding": settlement,
            "result": result,
            "answer": result.get("answer") or result.get("reason"),
            "limitation": result.get("limitation"),
        }
        return _with_context(routed, life_context)

    classifiers: tuple[tuple[str, Callable[[str], dict[str, Any]]], ...] = (
        ("marriage", analyze_marriage_question_v3),
        ("career", analyze_career_question_v1),
        ("finance", analyze_finance_question_v1),
        ("property_home", analyze_property_home_question_v1),
        ("family_children", analyze_family_children_question_v1),
        ("location_settlement", analyze_location_settlement_question_v1),
        ("education_learning", analyze_education_learning_question_v1),
        ("purpose_personal_growth", analyze_purpose_personal_growth_question_v1),
        ("friends_social_community", analyze_friends_social_community_question_v1),
        ("siblings_communication", analyze_siblings_communication_question_v1),
        ("parents_elders", analyze_parents_elders_question_v1),
    )
    matches: list[tuple[str, dict[str, Any]]] = []
    for domain, classifier in classifiers:
        try:
            understanding = classifier(question)
        except Exception:
            continue
        if understanding.get("available"):
            matches.append((domain, understanding))

    if not matches:
        return _with_context(
            {
                "available": False,
                "event": "unknown",
                "route": "unsupported",
                "domain": None,
                "reason": "The question was not identified as a supported AstroAI domain question.",
            },
            life_context,
        )

    domain, understanding = min(matches, key=lambda item: DOMAIN_ORDER.index(item[0]))
    if domain == "marriage":
        result = route_marriage_question_v3(chart, understanding, reference_moment)
    elif domain == "career":
        result = route_career_question_v1(chart, question, reference_moment)
    elif domain == "finance":
        result = route_finance_question_v1(chart, question, reference_moment)
    elif domain == "property_home":
        result = route_property_home_question_v1(chart, question, reference_moment)
    elif domain == "family_children":
        result = route_family_children_question_v1(chart, question, reference_moment)
    elif domain == "location_settlement":
        result = route_location_settlement_question_v1(chart, question, reference_moment)
    elif domain == "education_learning":
        result = route_education_learning_question_v1(chart, question, reference_moment)
    elif domain == "purpose_personal_growth":
        result = route_purpose_personal_growth_question_v1(chart, question, reference_moment)
    elif domain == "friends_social_community":
        result = route_friends_social_community_question_v1(chart, question, reference_moment)
    elif domain == "siblings_communication":
        result = route_siblings_communication_question_v1(chart, question, reference_moment)
    else:
        result = route_parents_elders_question_v1(chart, question, reference_moment)

    routed = {
        "available": bool(result.get("available")),
        "event": result.get("event") or domain,
        "route": f"top_level_to_{domain}",
        "domain": domain,
        "understanding": understanding,
        "result": result,
        "answer": result.get("answer") or result.get("reason"),
        "limitation": result.get("limitation"),
    }
    return _with_context(routed, life_context)
