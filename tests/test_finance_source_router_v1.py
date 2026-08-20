from datetime import datetime, timezone

from app.astrology.features.finance_router_v1 import route_finance_question_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "4": {"lord": "Venus"},
            "5": {"lord": "Jupiter"},
            "7": {"lord": "Mercury"},
            "8": {"lord": "Venus"},
            "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
        },
        "planets": {
            "Mercury": {"house": 10},
            "Mars": {"house": 3},
            "Venus": {"house": 4},
            "Jupiter": {"house": 11},
            "Saturn": {"house": 10},
        },
        "dasha_periods": [
            {
                "start": "2025-01-01T00:00:00+00:00",
                "end": "2030-01-01T00:00:00+00:00",
                "major_lord": "Jupiter",
                "sub_lord": "Mercury",
            }
        ],
    }


def _now():
    return datetime(2026, 8, 20, tzinfo=timezone.utc)


def test_job_vs_business_routes_to_source_engine():
    result = route_finance_question_v1(_chart(), "Will I earn more from job or business?", _now())
    assert result["available"] is True
    assert result["route"] == "finance_source_of_wealth"
    assert {item["source"] for item in result["requested_sources"]} == {
        "salary_career",
        "business_entrepreneurship",
    }
    assert result["strongest_requested_source"] is not None


def test_property_major_source_routes_to_source_engine():
    result = route_finance_question_v1(_chart(), "Is property a major wealth source for me?", _now())
    assert result["available"] is True
    assert result["route"] == "finance_source_of_wealth"
    assert result["requested_sources"][0]["source"] == "property_assets"


def test_multiple_income_sources_routes_to_source_engine():
    result = route_finance_question_v1(_chart(), "Will I have multiple income sources?", _now())
    assert result["available"] is True
    assert result["route"] == "finance_source_of_wealth"
    assert result["requested_sources"][0]["source"] == "networks_multiple_income"


def test_simple_salary_question_remains_natal():
    result = route_finance_question_v1(_chart(), "How is my salary potential?", _now())
    assert result["available"] is True
    assert result["route"] == "finance_natal"


def test_explicit_year_keeps_period_priority_over_source_engine():
    result = route_finance_question_v1(_chart(), "Will business income be strong in 2027?", _now())
    assert result["route"] == "finance_period_v2"
