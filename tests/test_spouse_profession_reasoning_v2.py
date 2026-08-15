import json

import app.services.chart_service as chart_service

from app.models.chart import BirthInput
from app.services.chart_service import build_chart

from app.astrology.features.spouse_profession_reasoning_v2 import (
    analyze_spouse_profession_v2,
)


# =========================================================
# HELPERS
# =========================================================

def _mock_resolve_place(
    place: str,
):

    return {
        "query": place,
        "resolved_name": (
            "Mumbai, Mumbai Suburban District, "
            "Maharashtra, 400051, India"
        ),
        "latitude": 19.054999,
        "longitude": 72.8692035,
        "timezone": "Asia/Kolkata",
    }


def _build_reference_chart():

    chart_service.resolve_place = (
        _mock_resolve_place
    )

    with open(
        "test_request.json",
        "r",
        encoding="utf-8",
    ) as file:

        payload = json.load(
            file
        )

    return build_chart(
        BirthInput(
            **payload
        )
    )


def _analysis():

    return (
        analyze_spouse_profession_v2(
            _build_reference_chart()
        )
    )


# =========================================================
# BASIC OUTPUT
# =========================================================

def test_spouse_profession_v21_available():

    result = _analysis()

    assert (
        result[
            "available"
        ]
        is True
    )

    assert (
        result[
            "event"
        ]
        == "spouse_profession"
    )

    assert (
        result[
            "model_version"
        ]
        == "v2.1"
    )

    assert (
        result[
            "confidence"
        ]
        == 0.84
    )


# =========================================================
# PROFESSION HOUSE
# =========================================================

def test_spouse_profession_v21_house_context():

    result = _analysis()

    context = (
        result[
            "chart_context"
        ]
    )

    profession_house = (
        context[
            "spouse_profession_house"
        ]
    )

    assert (
        profession_house[
            "natal_house"
        ]
        == 4
    )

    assert (
        profession_house[
            "sign"
        ]
        == "Libra"
    )

    assert (
        profession_house[
            "lord"
        ]
        == "Venus"
    )

    assert (
        profession_house[
            "occupants"
        ]
        == []
    )


# =========================================================
# PROFESSION LORD
# =========================================================

def test_spouse_profession_v21_lord_context():

    result = _analysis()

    profession_lord = (
        result[
            "chart_context"
        ][
            "spouse_profession_lord"
        ]
    )

    assert (
        profession_lord[
            "planet"
        ]
        == "Venus"
    )

    assert (
        profession_lord[
            "house"
        ]
        == 9
    )

    assert (
        profession_lord[
            "sign"
        ]
        == "Pisces"
    )

    assert (
        profession_lord[
            "dignity"
        ]
        == "exalted"
    )


# =========================================================
# TOP META CLUSTER
# =========================================================

def test_spouse_profession_v21_top_cluster():

    result = _analysis()

    top = (
        result[
            "strongest_clusters"
        ][
            0
        ]
    )

    assert (
        top[
            "cluster"
        ]
        == "client_advisory"
    )

    assert (
        top[
            "strength"
        ]
        == "strong"
    )

    assert (
        top[
            "source_count"
        ]
        == 2
    )

    assert (
        top[
            "family_count"
        ]
        == 3
    )

    assert (
        top[
            "source_convergence_bonus"
        ]
        > 0
    )


# =========================================================
# INDEPENDENT CONVERGENCE
# =========================================================

def test_spouse_profession_v21_client_advisory_convergence():

    result = _analysis()

    top = (
        result[
            "strongest_clusters"
        ][
            0
        ]
    )

    assert set(
        top[
            "sources"
        ]
    ) == {
        "spouse_profession_lord",
        "spouse_profession_lord_house",
    }

    assert (
        "client_relationship"
        in top[
            "supporting_families"
        ]
    )

    assert (
        "law_education_advisory"
        in top[
            "supporting_families"
        ]
    )

    assert (
        "consulting_guidance"
        in top[
            "supporting_families"
        ]
    )


# =========================================================
# SINGLE-SOURCE BREADTH
# =========================================================

def test_spouse_profession_v21_distinguishes_breadth_from_convergence():

    result = _analysis()

    clusters = {
        item[
            "cluster"
        ]: item
        for item in result[
            "meta_clusters"
        ]
    }

    international = (
        clusters[
            "international_knowledge"
        ]
    )

    creative = (
        clusters[
            "creative_commercial"
        ]
    )

    assert (
        international[
            "source_count"
        ]
        == 1
    )

    assert (
        international[
            "source_convergence_bonus"
        ]
        == 0.0
    )

    assert (
        international[
            "family_breadth_bonus"
        ]
        > 0
    )

    assert (
        creative[
            "source_count"
        ]
        == 1
    )

    assert (
        creative[
            "source_convergence_bonus"
        ]
        == 0.0
    )


# =========================================================
# STRUCTURED PROFESSIONAL CLUSTER
# =========================================================

def test_spouse_profession_v21_structured_cluster():

    result = _analysis()

    clusters = {
        item[
            "cluster"
        ]: item
        for item in result[
            "meta_clusters"
        ]
    }

    structured = (
        clusters[
            "structured_professional"
        ]
    )

    assert (
        structured[
            "strength"
        ]
        == "moderate_strong"
    )

    assert (
        structured[
            "source_count"
        ]
        == 2
    )

    assert (
        structured[
            "source_convergence_bonus"
        ]
        > 0
    )


# =========================================================
# TECHNICAL THEMES REMAIN SECONDARY
# =========================================================

def test_spouse_profession_v21_technical_is_supporting():

    result = _analysis()

    clusters = {
        item[
            "cluster"
        ]: item
        for item in result[
            "meta_clusters"
        ]
    }

    technical = (
        clusters[
            "technical_operational"
        ]
    )

    assert (
        technical[
            "strength"
        ]
        == "supporting"
    )

    assert (
        technical[
            "relative_strength"
        ]
        < 0.5
    )


# =========================================================
# CAREER STYLE
# =========================================================

def test_spouse_profession_v21_career_style():

    result = _analysis()

    style = (
        result[
            "career_style"
        ]
    )

    assert (
        "people-facing, advisory or client-oriented"
        in style
    )

    assert (
        "knowledge-based with possible international exposure"
        in style
    )

    assert (
        "creative-commercial"
        in style
    )

    assert (
        "structured and responsibility-oriented"
        in style
    )


# =========================================================
# SUMMARY RESTRAINT
# =========================================================

def test_spouse_profession_v21_summary_is_not_exact_job_prediction():

    result = _analysis()

    summary = (
        result[
            "summary"
        ]
    )

    assert (
        "broad professional themes"
        in summary
    )

    assert (
        "one exact occupation"
        in summary
    )

    assert (
        "client-facing"
        in summary
    )

    assert (
        "international"
        in summary
    )


# =========================================================
# EVIDENCE PROVENANCE
# =========================================================

def test_spouse_profession_v21_evidence():

    result = _analysis()

    factors = [
        item[
            "factor"
        ]
        for item in result[
            "evidence"
        ]
    ]

    assert (
        "spouse_profession_lord"
        in factors
    )

    assert (
        "spouse_profession_lord_house"
        in factors
    )

    assert (
        "seventh_lord_professional_context"
        in factors
    )

    assert (
        "spouse_profession_lord_dignity"
        in factors
    )
