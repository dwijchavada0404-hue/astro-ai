from __future__ import annotations

from typing import Any

from app.astrology.dignity import (
    evaluate_planetary_dignities,
)


# =========================================================
# PLANETARY PROFESSION FAMILIES
# =========================================================

PLANET_PROFESSION_FAMILIES = {
    "Sun": {
        "leadership_management": 0.9,
        "administration_public_role": 0.8,
        "authority_responsibility": 0.8,
    },
    "Moon": {
        "people_service": 0.8,
        "public_interaction": 0.7,
        "care_support": 0.7,
    },
    "Mars": {
        "technical_operations": 0.9,
        "engineering_execution": 0.85,
        "entrepreneurial_action": 0.7,
    },
    "Mercury": {
        "communication_commerce": 0.9,
        "analysis_consulting": 0.85,
        "technology_information": 0.75,
    },
    "Jupiter": {
        "advisory_consulting": 0.9,
        "finance_law_education": 0.85,
        "management_guidance": 0.75,
    },
    "Venus": {
        "creative_commercial": 0.9,
        "client_relationship": 0.9,
        "design_lifestyle": 0.7,
    },
    "Saturn": {
        "structured_corporate": 0.9,
        "operations_compliance": 0.85,
        "engineering_infrastructure": 0.7,
        "long_term_management": 0.75,
    },
    "Rahu": {
        "technology_digital": 0.8,
        "international_unconventional": 0.85,
        "large_networks": 0.7,
    },
    "Ketu": {
        "research_specialisation": 0.8,
        "technical_depth": 0.7,
        "independent_expertise": 0.65,
    },
}


HOUSE_PROFESSION_FAMILIES = {
    1: {
        "independent_leadership": 0.75,
    },
    2: {
        "finance_commerce": 0.85,
        "advisory_speech": 0.7,
    },
    3: {
        "communication_sales": 0.85,
        "media_entrepreneurship": 0.75,
    },
    4: {
        "property_infrastructure": 0.8,
        "education_domestic_sector": 0.65,
    },
    5: {
        "education_strategy": 0.75,
        "creative_advisory": 0.7,
    },
    6: {
        "service_operations": 0.8,
        "compliance_healthcare": 0.75,
    },
    7: {
        "business_client_facing": 0.9,
        "consulting_partnership": 0.85,
    },
    8: {
        "research_risk": 0.85,
        "insurance_specialised_finance": 0.8,
    },
    9: {
        "law_education_advisory": 0.9,
        "international_work": 0.85,
        "consulting_guidance": 0.8,
    },
    10: {
        "management_visibility": 0.9,
        "corporate_responsibility": 0.85,
    },
    11: {
        "large_organisations_networks": 0.85,
        "technology_commerce": 0.75,
    },
    12: {
        "international_institutional": 0.85,
        "research_behind_scenes": 0.7,
    },
}


# =========================================================
# FAMILY LABELS
# =========================================================

FAMILY_LABELS = {
    "leadership_management": "leadership or management",
    "administration_public_role": (
        "administration or public-facing responsibility"
    ),
    "authority_responsibility": (
        "responsibility-oriented work"
    ),
    "people_service": (
        "people-oriented or service work"
    ),
    "public_interaction": (
        "public interaction"
    ),
    "care_support": (
        "care or support functions"
    ),
    "technical_operations": (
        "technical or operations work"
    ),
    "engineering_execution": (
        "engineering or execution-oriented work"
    ),
    "entrepreneurial_action": (
        "entrepreneurial activity"
    ),
    "communication_commerce": (
        "communication or commerce"
    ),
    "analysis_consulting": (
        "analytical or consulting work"
    ),
    "technology_information": (
        "technology or information-oriented work"
    ),
    "advisory_consulting": (
        "advisory or consulting work"
    ),
    "finance_law_education": (
        "finance, law or education-related work"
    ),
    "management_guidance": (
        "management or guidance-oriented work"
    ),
    "creative_commercial": (
        "creative-commercial work"
    ),
    "client_relationship": (
        "client-facing or relationship-oriented work"
    ),
    "design_lifestyle": (
        "design or lifestyle-related sectors"
    ),
    "structured_corporate": (
        "structured corporate work"
    ),
    "operations_compliance": (
        "operations or compliance"
    ),
    "engineering_infrastructure": (
        "engineering or infrastructure"
    ),
    "long_term_management": (
        "long-term management responsibility"
    ),
    "technology_digital": (
        "technology or digital work"
    ),
    "international_unconventional": (
        "international or unconventional sectors"
    ),
    "large_networks": (
        "large networks or organisations"
    ),
    "research_specialisation": (
        "research or specialised work"
    ),
    "technical_depth": (
        "technical depth"
    ),
    "independent_expertise": (
        "independent specialist expertise"
    ),
    "independent_leadership": (
        "independent or self-directed leadership"
    ),
    "finance_commerce": (
        "finance or commerce"
    ),
    "advisory_speech": (
        "advisory or communication-oriented work"
    ),
    "communication_sales": (
        "communication or sales"
    ),
    "media_entrepreneurship": (
        "media or entrepreneurial activity"
    ),
    "property_infrastructure": (
        "property or infrastructure-related work"
    ),
    "education_domestic_sector": (
        "education or domestic-sector work"
    ),
    "education_strategy": (
        "education or strategy-oriented work"
    ),
    "creative_advisory": (
        "creative or advisory work"
    ),
    "service_operations": (
        "service or operations"
    ),
    "compliance_healthcare": (
        "compliance or healthcare-related work"
    ),
    "business_client_facing": (
        "business or client-facing work"
    ),
    "consulting_partnership": (
        "consulting or partnership-based work"
    ),
    "research_risk": (
        "research or risk-oriented work"
    ),
    "insurance_specialised_finance": (
        "insurance or specialised finance"
    ),
    "law_education_advisory": (
        "law, education or advisory professions"
    ),
    "international_work": (
        "international work"
    ),
    "consulting_guidance": (
        "consulting or guidance-oriented roles"
    ),
    "management_visibility": (
        "management with professional visibility"
    ),
    "corporate_responsibility": (
        "corporate responsibility"
    ),
    "large_organisations_networks": (
        "large organisations or networks"
    ),
    "technology_commerce": (
        "technology or commerce"
    ),
    "international_institutional": (
        "international or institutional environments"
    ),
    "research_behind_scenes": (
        "research or behind-the-scenes work"
    ),
}


# =========================================================
# META CLUSTERS
# =========================================================

META_CLUSTER_LABELS = {
    "client_advisory": (
        "client-facing, advisory or consulting work"
    ),
    "international_knowledge": (
        "international, knowledge-based or advisory work"
    ),
    "creative_commercial": (
        "creative-commercial or relationship-oriented work"
    ),
    "structured_professional": (
        "structured corporate or responsibility-oriented work"
    ),
    "technical_operational": (
        "technical, engineering or operations work"
    ),
    "finance_risk": (
        "finance, risk, insurance or commercial work"
    ),
    "technology_networked": (
        "technology, digital or network-oriented work"
    ),
    "people_service": (
        "people-oriented, public-facing or service work"
    ),
    "independent_entrepreneurial": (
        "independent, entrepreneurial or self-directed work"
    ),
    "research_specialist": (
        "research, specialist or depth-oriented work"
    ),
    "property_infrastructure": (
        "property, infrastructure or institutional work"
    ),
}


# =========================================================
# FAMILY → META CLUSTER MAP
# =========================================================

FAMILY_META_MAP = {
    "client_relationship": {
        "client_advisory": 1.0,
        "creative_commercial": 0.35,
    },
    "business_client_facing": {
        "client_advisory": 1.0,
    },
    "consulting_partnership": {
        "client_advisory": 0.95,
    },
    "advisory_consulting": {
        "client_advisory": 1.0,
        "international_knowledge": 0.35,
    },
    "analysis_consulting": {
        "client_advisory": 0.85,
    },
    "consulting_guidance": {
        "client_advisory": 0.9,
        "international_knowledge": 0.55,
    },
    "advisory_speech": {
        "client_advisory": 0.75,
    },
    "law_education_advisory": {
        "client_advisory": 0.8,
        "international_knowledge": 0.75,
    },
    "finance_law_education": {
        "international_knowledge": 0.6,
        "finance_risk": 0.55,
        "client_advisory": 0.45,
    },
    "education_strategy": {
        "international_knowledge": 0.65,
    },
    "education_domestic_sector": {
        "international_knowledge": 0.45,
    },
    "international_work": {
        "international_knowledge": 1.0,
    },
    "international_institutional": {
        "international_knowledge": 0.9,
        "property_infrastructure": 0.25,
    },
    "international_unconventional": {
        "international_knowledge": 0.8,
        "technology_networked": 0.35,
    },
    "creative_commercial": {
        "creative_commercial": 1.0,
    },
    "design_lifestyle": {
        "creative_commercial": 0.8,
    },
    "creative_advisory": {
        "creative_commercial": 0.7,
        "client_advisory": 0.45,
    },
    "communication_commerce": {
        "creative_commercial": 0.4,
        "client_advisory": 0.45,
        "finance_risk": 0.25,
    },
    "communication_sales": {
        "client_advisory": 0.55,
        "people_service": 0.45,
    },
    "structured_corporate": {
        "structured_professional": 1.0,
    },
    "operations_compliance": {
        "structured_professional": 0.85,
        "technical_operational": 0.45,
    },
    "long_term_management": {
        "structured_professional": 0.8,
    },
    "management_visibility": {
        "structured_professional": 0.9,
    },
    "corporate_responsibility": {
        "structured_professional": 0.9,
    },
    "leadership_management": {
        "structured_professional": 0.75,
        "independent_entrepreneurial": 0.25,
    },
    "management_guidance": {
        "structured_professional": 0.65,
        "client_advisory": 0.3,
    },
    "authority_responsibility": {
        "structured_professional": 0.75,
    },
    "administration_public_role": {
        "structured_professional": 0.65,
        "people_service": 0.35,
    },
    "technical_operations": {
        "technical_operational": 1.0,
    },
    "engineering_execution": {
        "technical_operational": 0.95,
    },
    "engineering_infrastructure": {
        "technical_operational": 0.85,
        "property_infrastructure": 0.55,
    },
    "service_operations": {
        "technical_operational": 0.45,
        "people_service": 0.65,
    },
    "finance_commerce": {
        "finance_risk": 1.0,
    },
    "insurance_specialised_finance": {
        "finance_risk": 1.0,
        "research_specialist": 0.35,
    },
    "research_risk": {
        "finance_risk": 0.55,
        "research_specialist": 0.8,
    },
    "technology_digital": {
        "technology_networked": 1.0,
    },
    "technology_information": {
        "technology_networked": 0.9,
    },
    "technology_commerce": {
        "technology_networked": 0.85,
        "finance_risk": 0.3,
    },
    "large_networks": {
        "technology_networked": 0.65,
    },
    "large_organisations_networks": {
        "technology_networked": 0.65,
        "structured_professional": 0.4,
    },
    "people_service": {
        "people_service": 1.0,
    },
    "public_interaction": {
        "people_service": 0.9,
    },
    "care_support": {
        "people_service": 0.8,
    },
    "compliance_healthcare": {
        "people_service": 0.45,
        "structured_professional": 0.45,
    },
    "entrepreneurial_action": {
        "independent_entrepreneurial": 1.0,
    },
    "independent_leadership": {
        "independent_entrepreneurial": 0.95,
    },
    "media_entrepreneurship": {
        "independent_entrepreneurial": 0.75,
        "creative_commercial": 0.45,
    },
    "research_specialisation": {
        "research_specialist": 1.0,
    },
    "technical_depth": {
        "research_specialist": 0.85,
        "technical_operational": 0.4,
    },
    "independent_expertise": {
        "research_specialist": 0.7,
        "independent_entrepreneurial": 0.4,
    },
    "research_behind_scenes": {
        "research_specialist": 0.8,
    },
    "property_infrastructure": {
        "property_infrastructure": 1.0,
    },
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_dict(
    value: Any,
) -> dict[str, Any]:

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _get_house(
    chart: dict[str, Any],
    house_number: int,
) -> dict[str, Any]:

    return _safe_dict(
        _safe_dict(
            chart.get(
                "houses"
            )
        ).get(
            str(
                house_number
            )
        )
    )


def _get_planet(
    chart: dict[str, Any],
    planet: str | None,
) -> dict[str, Any]:

    if not planet:
        return {}

    return _safe_dict(
        _safe_dict(
            chart.get(
                "planets"
            )
        ).get(
            planet
        )
    )


def _planets_in_house(
    chart: dict[str, Any],
    house_number: int,
) -> list[str]:

    result = []

    planets = _safe_dict(
        chart.get(
            "planets"
        )
    )

    for (
        planet_name,
        raw_data,
    ) in planets.items():

        data = _safe_dict(
            raw_data
        )

        if (
            data.get(
                "house"
            )
            == house_number
        ):
            result.append(
                str(
                    planet_name
                )
            )

    return result


def _dignity_map(
    chart: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    return {
        str(
            item.get(
                "planet"
            )
        ): item
        for item in evaluate_planetary_dignities(
            chart
        )
        if isinstance(
            item,
            dict,
        )
        and item.get(
            "planet"
        )
    }


# =========================================================
# FAMILY SCORE HELPERS
# =========================================================

def _add_family_scores(
    score_map: dict[str, float],
    source_map: dict[str, list[str]],
    families: dict[str, float],
    source: str,
    factor_weight: float,
) -> None:

    for (
        family,
        base_weight,
    ) in families.items():

        contribution = (
            base_weight
            * factor_weight
        )

        score_map[
            family
        ] = (
            score_map.get(
                family,
                0.0,
            )
            + contribution
        )

        source_map.setdefault(
            family,
            []
        )

        if source not in source_map[
            family
        ]:

            source_map[
                family
            ].append(
                source
            )


def _build_ranked_families(
    score_map: dict[str, float],
    source_map: dict[str, list[str]],
) -> list[dict[str, Any]]:

    result = []

    for (
        family,
        score,
    ) in score_map.items():

        sources = (
            source_map.get(
                family,
                []
            )
        )

        confirmation_bonus = min(
            max(
                len(
                    sources
                )
                - 1,
                0,
            )
            * 0.08,
            0.24,
        )

        confirmed_score = (
            score
            + confirmation_bonus
        )

        result.append(
            {
                "family": family,
                "label": (
                    FAMILY_LABELS.get(
                        family,
                        family,
                    )
                ),
                "raw_score": round(
                    score,
                    3,
                ),
                "confirmation_bonus": round(
                    confirmation_bonus,
                    3,
                ),
                "confirmed_score": round(
                    confirmed_score,
                    3,
                ),
                "sources": (
                    sources
                ),
            }
        )

    result.sort(
        key=lambda item: (
            item[
                "confirmed_score"
            ]
        ),
        reverse=True,
    )

    top_score = (
        result[
            0
        ][
            "confirmed_score"
        ]
        if result
        else 1.0
    )

    for item in result:

        item[
            "relative_strength"
        ] = round(
            item[
                "confirmed_score"
            ]
            / top_score,
            3,
        )

    return result


# =========================================================
# META CLUSTER SYNTHESIS
# =========================================================

def _build_meta_clusters(
    ranked_families: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    cluster_scores: dict[
        str,
        float,
    ] = {}

    cluster_sources: dict[
        str,
        list[str],
    ] = {}

    cluster_families: dict[
        str,
        list[str],
    ] = {}

    for family_data in ranked_families:

        family = str(
            family_data.get(
                "family",
                "",
            )
        )

        if not family:
            continue

        family_score = _safe_float(
            family_data.get(
                "confirmed_score"
            )
        )

        family_sources = (
            family_data.get(
                "sources",
                [],
            )
        )

        if not isinstance(
            family_sources,
            list,
        ):
            family_sources = []

        cluster_weights = (
            FAMILY_META_MAP.get(
                family,
                {},
            )
        )

        for (
            cluster,
            cluster_weight,
        ) in cluster_weights.items():

            contribution = (
                family_score
                * cluster_weight
            )

            cluster_scores[
                cluster
            ] = (
                cluster_scores.get(
                    cluster,
                    0.0,
                )
                + contribution
            )

            cluster_sources.setdefault(
                cluster,
                [],
            )

            cluster_families.setdefault(
                cluster,
                [],
            )

            if family not in cluster_families[
                cluster
            ]:

                cluster_families[
                    cluster
                ].append(
                    family
                )

            for source in family_sources:

                source_name = str(
                    source
                )

                if (
                    source_name
                    and source_name
                    not in cluster_sources[
                        cluster
                    ]
                ):

                    cluster_sources[
                        cluster
                    ].append(
                        source_name
                    )

    results = []

    for (
        cluster,
        raw_score,
    ) in cluster_scores.items():

        sources = (
            cluster_sources.get(
                cluster,
                []
            )
        )

        families = (
            cluster_families.get(
                cluster,
                []
            )
        )

        source_bonus = min(
            max(
                len(
                    sources
                )
                - 1,
                0,
            )
            * 0.14,
            0.42,
        )

        family_bonus = min(
            max(
                len(
                    families
                )
                - 1,
                0,
            )
            * 0.05,
            0.20,
        )

        convergence_bonus = (
            source_bonus
            + family_bonus
        )

        confirmed_score = (
            raw_score
            + convergence_bonus
        )

        results.append(
            {
                "cluster": cluster,
                "label": (
                    META_CLUSTER_LABELS.get(
                        cluster,
                        cluster,
                    )
                ),
                "raw_score": round(
                    raw_score,
                    3,
                ),
                "source_convergence_bonus": round(
                    source_bonus,
                    3,
                ),
                "family_breadth_bonus": round(
                    family_bonus,
                    3,
                ),
                "convergence_bonus": round(
                    convergence_bonus,
                    3,
                ),
                "confirmed_score": round(
                    confirmed_score,
                    3,
                ),
                "source_count": len(
                    sources
                ),
                "family_count": len(
                    families
                ),
                "sources": sources,
                "supporting_families": (
                    families
                ),
            }
        )

    results.sort(
        key=lambda item: (
            item[
                "confirmed_score"
            ]
        ),
        reverse=True,
    )

    top_score = (
        results[
            0
        ][
            "confirmed_score"
        ]
        if results
        else 1.0
    )

    for item in results:

        relative_strength = (
            item[
                "confirmed_score"
            ]
            / top_score
        )

        item[
            "relative_strength"
        ] = round(
            relative_strength,
            3,
        )

        if relative_strength >= 0.82:

            strength_label = (
                "strong"
            )

        elif relative_strength >= 0.62:

            strength_label = (
                "moderate_strong"
            )

        elif relative_strength >= 0.42:

            strength_label = (
                "moderate"
            )

        else:

            strength_label = (
                "supporting"
            )

        item[
            "strength"
        ] = (
            strength_label
        )

    return results


# =========================================================
# CAREER STYLE
# =========================================================

def _build_career_style(
    meta_clusters: list[dict[str, Any]],
) -> list[str]:

    style = []

    relevant = {
        item.get(
            "cluster"
        )
        for item in meta_clusters
        if item.get(
            "strength"
        )
        in (
            "strong",
            "moderate_strong",
            "moderate",
        )
    }

    if "client_advisory" in relevant:

        style.append(
            "people-facing, advisory or client-oriented"
        )

    if "international_knowledge" in relevant:

        style.append(
            "knowledge-based with possible international exposure"
        )

    if "creative_commercial" in relevant:

        style.append(
            "creative-commercial"
        )

    if "structured_professional" in relevant:

        style.append(
            "structured and responsibility-oriented"
        )

    if "technical_operational" in relevant:

        style.append(
            "technical or operations-oriented"
        )

    if "finance_risk" in relevant:

        style.append(
            "commercial, financial or risk-oriented"
        )

    if "technology_networked" in relevant:

        style.append(
            "technology or network-oriented"
        )

    if "people_service" in relevant:

        style.append(
            "people-oriented or service-based"
        )

    if "independent_entrepreneurial" in relevant:

        style.append(
            "independent or entrepreneurial"
        )

    if "research_specialist" in relevant:

        style.append(
            "specialist or research-oriented"
        )

    if "property_infrastructure" in relevant:

        style.append(
            "property, infrastructure or institutional"
        )

    return style


# =========================================================
# SUMMARY
# =========================================================

def _build_summary(
    meta_clusters: list[dict[str, Any]],
    career_style: list[str],
) -> str:

    if not meta_clusters:

        return (
            "The currently modelled chart factors do not "
            "produce a sufficiently distinct spouse "
            "profession profile."
        )

    meaningful = [
        item
        for item in meta_clusters
        if item.get(
            "strength"
        )
        in (
            "strong",
            "moderate_strong",
            "moderate",
        )
    ]

    if not meaningful:

        meaningful = (
            meta_clusters[
                :3
            ]
        )

    top = (
        meaningful[
            :4
        ]
    )

    labels = [
        item[
            "label"
        ]
        for item in top
    ]

    if len(
        labels
    ) == 1:

        cluster_text = (
            labels[
                0
            ]
        )

    else:

        cluster_text = (
            ", ".join(
                labels[
                    :-1
                ]
            )
            + " and "
            + labels[
                -1
            ]
        )

    summary = (
        "The spouse's career pattern is most consistent "
        f"with {cluster_text}. "
        "These are broad professional themes rather than "
        "a prediction of one exact occupation."
    )

    if career_style:

        top_styles = (
            career_style[
                :4
            ]
        )

        if len(
            top_styles
        ) == 1:

            style_text = (
                top_styles[
                    0
                ]
            )

        else:

            style_text = (
                ", ".join(
                    top_styles[
                        :-1
                    ]
                )
                + " and "
                + top_styles[
                    -1
                ]
            )

        summary += (
            " Overall, the professional environment may be "
            f"{style_text}."
        )

    return summary


# =========================================================
# MAIN ENGINE
# =========================================================

def analyze_spouse_profession_v2(
    chart: dict[str, Any],
) -> dict[str, Any]:

    if not isinstance(
        chart,
        dict,
    ):
        raise ValueError(
            "chart must be a dictionary."
        )

    seventh_house = (
        _get_house(
            chart,
            7,
        )
    )

    if not seventh_house:

        return {
            "available": False,
            "reason": (
                "7th house data is unavailable."
            ),
        }

    profession_house_number = 4

    profession_house = (
        _get_house(
            chart,
            profession_house_number,
        )
    )

    if not profession_house:

        return {
            "available": False,
            "reason": (
                "The spouse profession house data "
                "is unavailable."
            ),
        }

    seventh_lord = (
        seventh_house.get(
            "lord"
        )
    )

    seventh_lord_data = (
        _get_planet(
            chart,
            seventh_lord,
        )
    )

    profession_lord = (
        profession_house.get(
            "lord"
        )
    )

    profession_lord_data = (
        _get_planet(
            chart,
            profession_lord,
        )
    )

    profession_occupants = (
        _planets_in_house(
            chart,
            profession_house_number,
        )
    )

    dignity_map = (
        _dignity_map(
            chart
        )
    )

    profession_lord_dignity = (
        _safe_dict(
            dignity_map.get(
                str(
                    profession_lord
                )
            )
        )
    )

    seventh_lord_dignity = (
        _safe_dict(
            dignity_map.get(
                str(
                    seventh_lord
                )
            )
        )
    )

    score_map: dict[
        str,
        float,
    ] = {}

    source_map: dict[
        str,
        list[str],
    ] = {}

    evidence = []

    # =====================================================
    # PRIMARY: SPOUSE PROFESSION LORD
    # =====================================================

    profession_lord_families = (
        PLANET_PROFESSION_FAMILIES.get(
            str(
                profession_lord
            ),
            {},
        )
    )

    _add_family_scores(
        score_map,
        source_map,
        profession_lord_families,
        "spouse_profession_lord",
        1.0,
    )

    evidence.append(
        {
            "factor": (
                "spouse_profession_lord"
            ),
            "tier": "primary",
            "strength": 1.0,
            "interpretation": (
                f"The spouse profession house is the natal "
                f"4th house, ruled by {profession_lord}. "
                "The profession lord provides the primary "
                "occupational family."
            ),
            "details": {
                "house": 4,
                "sign": (
                    profession_house.get(
                        "sign"
                    )
                ),
                "lord": (
                    profession_lord
                ),
            },
        }
    )

    # =====================================================
    # PRIMARY: PROFESSION LORD HOUSE
    # =====================================================

    profession_lord_house = (
        profession_lord_data.get(
            "house"
        )
    )

    if profession_lord_house:

        house_families = (
            HOUSE_PROFESSION_FAMILIES.get(
                int(
                    profession_lord_house
                ),
                {},
            )
        )

        _add_family_scores(
            score_map,
            source_map,
            house_families,
            "spouse_profession_lord_house",
            0.95,
        )

        evidence.append(
            {
                "factor": (
                    "spouse_profession_lord_house"
                ),
                "tier": "primary",
                "strength": 0.95,
                "interpretation": (
                    f"The spouse profession lord "
                    f"{profession_lord} is placed in the "
                    f"{profession_lord_house}th natal house, "
                    "which modifies the likely professional "
                    "environment."
                ),
                "details": {
                    "planet": (
                        profession_lord
                    ),
                    "house": (
                        profession_lord_house
                    ),
                    "sign": (
                        profession_lord_data.get(
                            "sign"
                        )
                    ),
                },
            }
        )

    # =====================================================
    # PRIMARY: OCCUPANTS
    # =====================================================

    for planet in profession_occupants:

        families = (
            PLANET_PROFESSION_FAMILIES.get(
                planet,
                {},
            )
        )

        source_name = (
            f"{planet.lower()}_in_"
            "spouse_profession_house"
        )

        _add_family_scores(
            score_map,
            source_map,
            families,
            source_name,
            0.85,
        )

        evidence.append(
            {
                "factor": (
                    "planet_in_spouse_profession_house"
                ),
                "tier": "primary",
                "strength": 0.85,
                "interpretation": (
                    f"{planet} occupies the spouse profession "
                    "house and directly modifies occupational "
                    "themes."
                ),
                "details": {
                    "planet": planet,
                    "house": 4,
                },
            }
        )

    # =====================================================
    # SECONDARY: 7TH LORD
    # =====================================================

    seventh_lord_families = (
        PLANET_PROFESSION_FAMILIES.get(
            str(
                seventh_lord
            ),
            {},
        )
    )

    _add_family_scores(
        score_map,
        source_map,
        seventh_lord_families,
        "seventh_lord_professional_modifier",
        0.45,
    )

    seventh_lord_house = (
        seventh_lord_data.get(
            "house"
        )
    )

    if seventh_lord_house:

        seventh_house_families = (
            HOUSE_PROFESSION_FAMILIES.get(
                int(
                    seventh_lord_house
                ),
                {},
            )
        )

        _add_family_scores(
            score_map,
            source_map,
            seventh_house_families,
            "seventh_lord_house_modifier",
            0.40,
        )

    evidence.append(
        {
            "factor": (
                "seventh_lord_professional_context"
            ),
            "tier": "secondary",
            "strength": 0.45,
            "interpretation": (
                f"The 7th lord {seventh_lord} provides "
                "secondary information about the spouse's "
                "professional style."
            ),
            "details": {
                "planet": (
                    seventh_lord
                ),
                "house": (
                    seventh_lord_house
                ),
                "sign": (
                    seventh_lord_data.get(
                        "sign"
                    )
                ),
            },
        }
    )

    # =====================================================
    # DIGNITY MODIFIER
    # =====================================================

    dignity_name = (
        profession_lord_dignity.get(
            "dignity"
        )
    )

    dignity_multiplier = 1.0

    if dignity_name == "exalted":

        dignity_multiplier = 1.12

    elif dignity_name == "own_sign":

        dignity_multiplier = 1.08

    elif dignity_name == "debilitated":

        dignity_multiplier = 0.88

    if dignity_multiplier != 1.0:

        for family in list(
            score_map.keys()
        ):

            sources = (
                source_map.get(
                    family,
                    []
                )
            )

            if (
                "spouse_profession_lord"
                in sources
                or
                "spouse_profession_lord_house"
                in sources
            ):

                score_map[
                    family
                ] *= (
                    dignity_multiplier
                )

    evidence.append(
        {
            "factor": (
                "spouse_profession_lord_dignity"
            ),
            "tier": "context",
            "strength": (
                0.65
                if dignity_name
                in (
                    "exalted",
                    "own_sign",
                )
                else 0.35
            ),
            "interpretation": (
                "Planetary dignity modifies confidence in "
                "the profession-lord evidence rather than "
                "creating a separate occupation."
            ),
            "details": {
                "planet": (
                    profession_lord
                ),
                "dignity": (
                    dignity_name
                ),
                "multiplier": (
                    dignity_multiplier
                ),
            },
        }
    )

    # =====================================================
    # FAMILY RANKING
    # =====================================================

    ranked_families = (
        _build_ranked_families(
            score_map,
            source_map,
        )
    )

    strongest_families = (
        ranked_families[
            :6
        ]
    )

    # =====================================================
    # META CLUSTER SYNTHESIS
    # =====================================================

    meta_clusters = (
        _build_meta_clusters(
            ranked_families
        )
    )

    strongest_clusters = (
        meta_clusters[
            :5
        ]
    )

    career_style = (
        _build_career_style(
            strongest_clusters
        )
    )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    primary_count = sum(
        1
        for item in evidence
        if item.get(
            "tier"
        )
        == "primary"
    )

    top_cluster_sources = (
        strongest_clusters[
            0
        ].get(
            "source_count",
            0,
        )
        if strongest_clusters
        else 0
    )

    top_cluster_families = (
        strongest_clusters[
            0
        ].get(
            "family_count",
            0,
        )
        if strongest_clusters
        else 0
    )

    confidence = round(
        _clamp(
            (
                0.52
                + min(
                    primary_count,
                    3,
                )
                * 0.06
                + min(
                    top_cluster_sources,
                    3,
                )
                * 0.045
                + min(
                    top_cluster_families,
                    4,
                )
                * 0.02
                + (
                    0.05
                    if dignity_name
                    in (
                        "exalted",
                        "own_sign",
                    )
                    else 0.0
                )
            ),
            0.50,
            0.86,
        ),
        3,
    )

    summary = (
        _build_summary(
            strongest_clusters,
            career_style,
        )
    )

    return {
        "available": True,

        "event": (
            "spouse_profession"
        ),

        "model_version": (
            "v2.1"
        ),

        "confidence": (
            confidence
        ),

        "summary": (
            summary
        ),

        "career_style": (
            career_style
        ),

        "strongest_clusters": (
            strongest_clusters
        ),

        "meta_clusters": (
            meta_clusters
        ),

        "strongest_families": (
            strongest_families
        ),

        "ranked_families": (
            ranked_families
        ),

        "chart_context": {
            "seventh_house": {
                "sign": (
                    seventh_house.get(
                        "sign"
                    )
                ),
                "lord": (
                    seventh_lord
                ),
            },

            "seventh_lord": {
                "planet": (
                    seventh_lord
                ),
                "house": (
                    seventh_lord_house
                ),
                "sign": (
                    seventh_lord_data.get(
                        "sign"
                    )
                ),
                "dignity": (
                    seventh_lord_dignity.get(
                        "dignity"
                    )
                ),
            },

            "spouse_profession_house": {
                "natal_house": (
                    profession_house_number
                ),
                "sign": (
                    profession_house.get(
                        "sign"
                    )
                ),
                "lord": (
                    profession_lord
                ),
                "occupants": (
                    profession_occupants
                ),
            },

            "spouse_profession_lord": {
                "planet": (
                    profession_lord
                ),
                "house": (
                    profession_lord_house
                ),
                "sign": (
                    profession_lord_data.get(
                        "sign"
                    )
                ),
                "dignity": (
                    dignity_name
                ),
            },
        },

        "evidence": (
            evidence
        ),
    }
