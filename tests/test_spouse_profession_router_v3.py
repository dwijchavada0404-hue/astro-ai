from __future__ import annotations

from datetime import datetime

import pytest

import app.astrology.features.marriage_forecast_router_v3 as router_v3

from app.astrology.features.marriage_forecast_router_v3 import (
    route_marriage_question_v3,
)

from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)


# =========================================================
# REFERENCE TIME
# =========================================================

def _reference_moment() -> datetime:

    return datetime.fromisoformat(
        "2026-08-15T12:00:00+05:30"
    )


# =========================================================
# MINIMAL CHART
# =========================================================

def _chart() -> dict:

    # The profession evidence engine is monkeypatched in
    # these tests. The router still receives a valid chart
    # dictionary, keeping the integration boundary explicit.

    return {
        "houses": {},
        "planets": {},
    }


# =========================================================
# DETERMINISTIC PROFESSION ANALYSIS
# =========================================================

def _profession_analysis() -> dict:

    return {
        "available": True,

        "event": (
            "spouse_profession"
        ),

        "model_version": (
            "v2.1"
        ),

        "confidence": (
            0.84
        ),

        "summary": (
            "The spouse's career pattern is most consistent "
            "with client-facing, advisory or consulting work, "
            "international work, creative-commercial work and "
            "structured professional work."
        ),

        "career_style": [
            "people-facing, advisory or client-oriented",
            "knowledge-based with possible international exposure",
            "creative-commercial",
            "structured and responsibility-oriented",
        ],

        "strongest_clusters": [
            {
                "cluster": (
                    "client_advisory"
                ),
                "label": (
                    "client-facing, advisory or consulting work"
                ),
                "relative_strength": (
                    1.0
                ),
                "strength": (
                    "strong"
                ),
                "sources": [
                    "spouse_profession_lord",
                    "spouse_profession_lord_house",
                ],
                "supporting_families": [
                    "client_relationship",
                    "law_education_advisory",
                    "consulting_guidance",
                ],
            },
            {
                "cluster": (
                    "international_knowledge"
                ),
                "label": (
                    "international, knowledge-based or advisory work"
                ),
                "relative_strength": (
                    0.788
                ),
                "strength": (
                    "moderate_strong"
                ),
                "sources": [
                    "spouse_profession_lord_house",
                ],
                "supporting_families": [
                    "law_education_advisory",
                    "international_work",
                    "consulting_guidance",
                ],
            },
            {
                "cluster": (
                    "creative_commercial"
                ),
                "label": (
                    "creative-commercial or relationship-oriented work"
                ),
                "relative_strength": (
                    0.751
                ),
                "strength": (
                    "moderate_strong"
                ),
                "sources": [
                    "spouse_profession_lord",
                ],
                "supporting_families": [
                    "creative_commercial",
                    "client_relationship",
                    "design_lifestyle",
                ],
            },
            {
                "cluster": (
                    "structured_professional"
                ),
                "label": (
                    "structured corporate or responsibility-oriented work"
                ),
                "relative_strength": (
                    0.709
                ),
                "strength": (
                    "moderate_strong"
                ),
                "sources": [
                    "seventh_lord_professional_modifier",
                    "seventh_lord_house_modifier",
                ],
                "supporting_families": [
                    "structured_corporate",
                    "operations_compliance",
                    "management_visibility",
                    "corporate_responsibility",
                    "long_term_management",
                ],
            },
            {
                "cluster": (
                    "technical_operational"
                ),
                "label": (
                    "technical, engineering or operations work"
                ),
                "relative_strength": (
                    0.176
                ),
                "strength": (
                    "supporting"
                ),
                "sources": [
                    "seventh_lord_professional_modifier",
                ],
                "supporting_families": [
                    "operations_compliance",
                    "engineering_infrastructure",
                ],
            },
        ],

        "meta_clusters": [
            {
                "cluster": (
                    "client_advisory"
                ),
                "label": (
                    "client-facing, advisory or consulting work"
                ),
                "relative_strength": (
                    1.0
                ),
                "strength": (
                    "strong"
                ),
                "sources": [
                    "spouse_profession_lord",
                    "spouse_profession_lord_house",
                ],
                "supporting_families": [
                    "client_relationship",
                    "law_education_advisory",
                    "consulting_guidance",
                ],
            },
            {
                "cluster": (
                    "international_knowledge"
                ),
                "label": (
                    "international, knowledge-based or advisory work"
                ),
                "relative_strength": (
                    0.788
                ),
                "strength": (
                    "moderate_strong"
                ),
                "sources": [
                    "spouse_profession_lord_house",
                ],
                "supporting_families": [
                    "law_education_advisory",
                    "international_work",
                    "consulting_guidance",
                ],
            },
            {
                "cluster": (
                    "creative_commercial"
                ),
                "label": (
                    "creative-commercial or relationship-oriented work"
                ),
                "relative_strength": (
                    0.751
                ),
                "strength": (
                    "moderate_strong"
                ),
                "sources": [
                    "spouse_profession_lord",
                ],
                "supporting_families": [
                    "creative_commercial",
                    "client_relationship",
                    "design_lifestyle",
                ],
            },
            {
                "cluster": (
                    "structured_professional"
                ),
                "label": (
                    "structured corporate or responsibility-oriented work"
                ),
                "relative_strength": (
                    0.709
                ),
                "strength": (
                    "moderate_strong"
                ),
                "sources": [
                    "seventh_lord_professional_modifier",
                    "seventh_lord_house_modifier",
                ],
                "supporting_families": [
                    "structured_corporate",
                    "operations_compliance",
                    "management_visibility",
                    "corporate_responsibility",
                    "long_term_management",
                ],
            },
            {
                "cluster": (
                    "technical_operational"
                ),
                "label": (
                    "technical, engineering or operations work"
                ),
                "relative_strength": (
                    0.176
                ),
                "strength": (
                    "supporting"
                ),
                "sources": [
                    "seventh_lord_professional_modifier",
                ],
                "supporting_families": [
                    "operations_compliance",
                    "engineering_infrastructure",
                ],
            },
        ],

        "strongest_families": [
            {
                "family": (
                    "creative_commercial"
                ),
                "relative_strength": (
                    1.0
                ),
            },
            {
                "family": (
                    "client_relationship"
                ),
                "relative_strength": (
                    1.0
                ),
            },
            {
                "family": (
                    "law_education_advisory"
                ),
                "relative_strength": (
                    0.95
                ),
            },
            {
                "family": (
                    "international_work"
                ),
                "relative_strength": (
                    0.897
                ),
            },
            {
                "family": (
                    "consulting_guidance"
                ),
                "relative_strength": (
                    0.844
                ),
            },
            {
                "family": (
                    "design_lifestyle"
                ),
                "relative_strength": (
                    0.778
                ),
            },
        ],

        "ranked_families": [
            {
                "family": (
                    "creative_commercial"
                ),
                "label": (
                    "creative-commercial work"
                ),
                "relative_strength": (
                    1.0
                ),
                "sources": [
                    "spouse_profession_lord",
                ],
            },
            {
                "family": (
                    "client_relationship"
                ),
                "label": (
                    "client-facing or relationship-oriented work"
                ),
                "relative_strength": (
                    1.0
                ),
                "sources": [
                    "spouse_profession_lord",
                ],
            },
            {
                "family": (
                    "law_education_advisory"
                ),
                "label": (
                    "law, education or advisory professions"
                ),
                "relative_strength": (
                    0.95
                ),
                "sources": [
                    "spouse_profession_lord_house",
                ],
            },
            {
                "family": (
                    "international_work"
                ),
                "label": (
                    "international work"
                ),
                "relative_strength": (
                    0.897
                ),
                "sources": [
                    "spouse_profession_lord_house",
                ],
            },
            {
                "family": (
                    "consulting_guidance"
                ),
                "label": (
                    "consulting or guidance-oriented roles"
                ),
                "relative_strength": (
                    0.844
                ),
                "sources": [
                    "spouse_profession_lord_house",
                ],
            },
            {
                "family": (
                    "design_lifestyle"
                ),
                "label": (
                    "design or lifestyle-related sectors"
                ),
                "relative_strength": (
                    0.778
                ),
                "sources": [
                    "spouse_profession_lord",
                ],
            },
            {
                "family": (
                    "structured_corporate"
                ),
                "label": (
                    "structured corporate work"
                ),
                "relative_strength": (
                    0.402
                ),
                "sources": [
                    "seventh_lord_professional_modifier",
                ],
            },
            {
                "family": (
                    "management_visibility"
                ),
                "label": (
                    "management with professional visibility"
                ),
                "relative_strength": (
                    0.357
                ),
                "sources": [
                    "seventh_lord_house_modifier",
                ],
            },
            {
                "family": (
                    "corporate_responsibility"
                ),
                "label": (
                    "corporate responsibility"
                ),
                "relative_strength": (
                    0.337
                ),
                "sources": [
                    "seventh_lord_house_modifier",
                ],
            },
            {
                "family": (
                    "long_term_management"
                ),
                "label": (
                    "long-term management responsibility"
                ),
                "relative_strength": (
                    0.335
                ),
                "sources": [
                    "seventh_lord_professional_modifier",
                ],
            },
        ],

        "chart_context": {
            "seventh_house": {
                "sign": (
                    "Capricorn"
                ),
                "lord": (
                    "Saturn"
                ),
            },
        },

        "evidence": [],
    }


# =========================================================
# ROUTE HELPER
# =========================================================

def _route(
    monkeypatch: pytest.MonkeyPatch,
    question: str,
) -> tuple[
    dict,
    dict,
]:

    monkeypatch.setattr(
        router_v3,
        "analyze_spouse_profession_v2",
        lambda chart: (
            _profession_analysis()
        ),
    )

    analysis = (
        analyze_marriage_question_v3(
            question
        )
    )

    result = (
        route_marriage_question_v3(
            _chart(),
            analysis,
            _reference_moment(),
        )
    )

    return (
        analysis,
        result,
    )


# =========================================================
# GENERAL PROFESSION ROUTING
# =========================================================

def test_general_spouse_profession_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    analysis, result = (
        _route(
            monkeypatch,
            "What will my spouse do for work?",
        )
    )

    assert analysis[
        "primary_event"
    ] == "spouse_profession"

    assert result[
        "available"
    ] is True

    assert result[
        "route"
    ] == "natal_evidence"

    assert result[
        "event"
    ] == "spouse_profession"

    assert result[
        "evidence_engine"
    ] == "spouse_profession_reasoning_v2"

    assert result[
        "forecast_type"
    ] == "natal_pattern"

    assert result[
        "model_version"
    ] == "v2.1"

    assert result[
        "confidence"
    ] == 0.84

    assert result[
        "target_profession"
    ] is None

    assert result[
        "target_analysis"
    ] is None

    assert result[
        "answer"
    ] == result[
        "summary"
    ]


# =========================================================
# INTERNATIONAL WORK
# =========================================================

def test_international_work_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Will my spouse work abroad?",
        )
    )

    target = result[
        "target_analysis"
    ]

    assert result[
        "target_profession"
    ] == "international_work"

    assert target[
        "target"
    ] == "international_work"

    assert target[
        "target_type"
    ] == "broad"

    assert target[
        "support_level"
    ] == "strongly_supported"

    assert target[
        "support_score"
    ] == pytest.approx(
        0.897,
        abs=0.001,
    )

    assert (
        "strongly supported"
        in result[
            "answer"
        ].lower()
    )


# =========================================================
# LAW
# =========================================================

def test_law_target_uses_specific_scoring(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Could my spouse be a lawyer?",
        )
    )

    target = result[
        "target_analysis"
    ]

    assert result[
        "target_profession"
    ] == "law"

    assert target[
        "target_type"
    ] == "specific"

    assert target[
        "strongest_cluster_score"
    ] == pytest.approx(
        1.0,
        abs=0.001,
    )

    assert target[
        "strongest_family_score"
    ] == pytest.approx(
        0.95,
        abs=0.001,
    )

    # Specific occupation:
    # 80% direct-family evidence
    # 20% broad-cluster confirmation.
    assert target[
        "support_score"
    ] == pytest.approx(
        0.96,
        abs=0.001,
    )

    assert target[
        "support_level"
    ] == "strongly_supported"


# =========================================================
# CORPORATE
# =========================================================

def test_corporate_target_uses_broad_cluster(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Will my spouse have a corporate job?",
        )
    )

    target = result[
        "target_analysis"
    ]

    assert result[
        "target_profession"
    ] == "corporate_work"

    assert target[
        "target_type"
    ] == "broad"

    assert target[
        "support_score"
    ] == pytest.approx(
        0.709,
        abs=0.001,
    )

    assert target[
        "support_level"
    ] == "supported"


# =========================================================
# CONSULTING
# =========================================================

def test_consulting_target_reaches_router(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    analysis, result = (
        _route(
            monkeypatch,
            "Could my spouse be a consultant?",
        )
    )

    assert analysis[
        "primary_event"
    ] == "spouse_profession"

    assert result[
        "event"
    ] == "spouse_profession"

    assert result[
        "target_profession"
    ] == "consulting"

    target = result[
        "target_analysis"
    ]

    assert target[
        "target_type"
    ] == "specific"

    assert target[
        "strongest_cluster_score"
    ] == pytest.approx(
        1.0,
        abs=0.001,
    )

    assert target[
        "strongest_family_score"
    ] == pytest.approx(
        0.95,
        abs=0.001,
    )

    assert target[
        "support_score"
    ] == pytest.approx(
        0.96,
        abs=0.001,
    )

    assert target[
        "support_level"
    ] == "strongly_supported"


# =========================================================
# DESIGN / CREATIVE
# =========================================================

def test_designer_target_reaches_router(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    analysis, result = (
        _route(
            monkeypatch,
            "Could my spouse be a designer?",
        )
    )

    assert analysis[
        "primary_event"
    ] == "spouse_profession"

    assert result[
        "target_profession"
    ] == "creative_work"

    target = result[
        "target_analysis"
    ]

    assert target[
        "target_type"
    ] == "specific"

    assert target[
        "strongest_cluster_score"
    ] == pytest.approx(
        0.751,
        abs=0.001,
    )

    assert target[
        "strongest_family_score"
    ] == pytest.approx(
        1.0,
        abs=0.001,
    )

    assert target[
        "support_score"
    ] == pytest.approx(
        0.95,
        abs=0.001,
    )

    assert target[
        "support_level"
    ] == "strongly_supported"


# =========================================================
# BUSINESS
# =========================================================

def test_business_target_reaches_router(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    analysis, result = (
        _route(
            monkeypatch,
            "Could my spouse own a business?",
        )
    )

    assert analysis[
        "primary_event"
    ] == "spouse_profession"

    assert result[
        "target_profession"
    ] == "business"

    target = result[
        "target_analysis"
    ]

    assert target[
        "target_type"
    ] == "broad"

    assert target[
        "support_score"
    ] == pytest.approx(
        1.0,
        abs=0.001,
    )

    assert target[
        "support_level"
    ] == "strongly_supported"


# =========================================================
# FINANCE
# =========================================================

def test_finance_target_can_be_weak(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Will my spouse work in finance?",
        )
    )

    target = result[
        "target_analysis"
    ]

    assert result[
        "target_profession"
    ] == "finance"

    assert target[
        "target_type"
    ] == "specific"

    assert target[
        "support_level"
    ] == "weakly_supported"

    assert target[
        "support_score"
    ] == pytest.approx(
        0.0,
        abs=0.001,
    )


# =========================================================
# TECHNOLOGY
# =========================================================

def test_technology_cluster_only_support_is_discounted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Will my spouse work in technology?",
        )
    )

    target = result[
        "target_analysis"
    ]

    assert result[
        "target_profession"
    ] == "technology"

    assert target[
        "target_type"
    ] == "specific"

    assert target[
        "strongest_family_score"
    ] == pytest.approx(
        0.0,
        abs=0.001,
    )

    assert target[
        "strongest_cluster_score"
    ] == pytest.approx(
        0.176,
        abs=0.001,
    )

    # Cluster-only evidence for a specific occupation
    # receives the 70% discount.
    assert target[
        "support_score"
    ] == pytest.approx(
        0.123,
        abs=0.001,
    )

    assert target[
        "support_level"
    ] == "weakly_supported"


# =========================================================
# SOFTWARE ENGINEER
# =========================================================

def test_software_engineer_maps_to_technology(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Could my spouse be a software engineer?",
        )
    )

    assert result[
        "target_profession"
    ] == "technology"

    assert result[
        "target_analysis"
    ][
        "target_type"
    ] == "specific"


# =========================================================
# BANKER
# =========================================================

def test_banker_maps_to_finance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Could my spouse be a banker?",
        )
    )

    assert result[
        "target_profession"
    ] == "finance"

    assert result[
        "target_analysis"
    ][
        "target_type"
    ] == "specific"


# =========================================================
# ENTREPRENEUR
# =========================================================

def test_entrepreneur_maps_to_business(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "Could my spouse be an entrepreneur?",
        )
    )

    assert result[
        "target_profession"
    ] == "business"

    assert result[
        "target_analysis"
    ][
        "target_type"
    ] == "broad"


# =========================================================
# ROUTER METADATA
# =========================================================

def test_spouse_profession_router_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    analysis, result = (
        _route(
            monkeypatch,
            "Could my spouse be a consultant?",
        )
    )

    assert result[
        "event_label"
    ] == "Spouse Profession / Career Profile"

    assert result[
        "question_type"
    ] == "probability"

    assert result[
        "direction"
    ] == "neutral"

    assert result[
        "parser_confidence"
    ] == pytest.approx(
        0.82
    )

    assert result[
        "reference_moment"
    ] == (
        "2026-08-15T12:00:00+05:30"
    )

    assert analysis[
        "query_mode"
    ] == "single_event"


# =========================================================
# ANALYSIS PRESERVED
# =========================================================

def test_profession_analysis_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    _, result = (
        _route(
            monkeypatch,
            "What will my spouse do for work?",
        )
    )

    assert (
        result[
            "analysis"
        ][
            "model_version"
        ]
        == "v2.1"
    )

    assert result[
        "career_style"
    ]

    assert result[
        "strongest_clusters"
    ]

    assert result[
        "ranked_families"
    ]


# =========================================================
# EXISTING EVENT ROUTES NOT HIJACKED
# =========================================================

@pytest.mark.parametrize(
    (
        "question",
        "expected_event",
    ),
    [
        (
            "What kind of person will I marry?",
            "spouse_traits",
        ),
        (
            "When will I meet my future spouse?",
            "spouse_meeting",
        ),
        (
            "When will I get married?",
            "marriage_timing",
        ),
        (
            "Will I have a love marriage or arranged marriage?",
            "love_vs_arranged",
        ),
    ],
)
def test_profession_detection_does_not_hijack_other_events(
    question: str,
    expected_event: str,
) -> None:

    analysis = (
        analyze_marriage_question_v3(
            question
        )
    )

    assert analysis[
        "primary_event"
    ] == expected_event
