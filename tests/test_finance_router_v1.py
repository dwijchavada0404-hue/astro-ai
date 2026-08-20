from datetime import datetime, timezone

from app.astrology.features.finance_router_v1 import route_finance_question_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"}, "4": {"lord": "Sun"}, "5": {"lord": "Venus"},
            "6": {"lord": "Mercury"}, "8": {"lord": "Jupiter"}, "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"}, "11": {"lord": "Jupiter"}, "12": {"lord": "Mars"},
        },
        "planets": {
            "Mercury": {"house": 11}, "Venus": {"house": 5}, "Jupiter": {"house": 9},
            "Saturn": {"house": 2}, "Sun": {"house": 4}, "Mars": {"house": 3},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-12-31T23:59:59+00:00", "major_lord": "Saturn", "sub_lord": "Venus"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-12-31T23:59:59+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"},
        ],
    }


def _now():
    return datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc)


def test_timing_question_routes_to_finance_timing():
    result = route_finance_question_v1(_chart(), "When will my finances improve?", _now())
    assert result["available"] is True
    assert result["route"] == "finance_timing"
    assert result["timing"]["future"]["available"] is True


def test_natal_savings_question_routes_to_theme():
    result = route_finance_question_v1(_chart(), "How is my savings potential?", _now())
    assert result["available"] is True
    assert result["route"] == "finance_natal"
    assert result["theme"] == "income_savings"
    assert result["theme_score"] is not None


def test_inheritance_question_routes_to_shared_assets_theme():
    result = route_finance_question_v1(_chart(), "Is inheritance indicated?", _now())
    assert result["theme"] == "joint_assets_inheritance"


def test_unrelated_question_is_declined():
    result = route_finance_question_v1(_chart(), "When will I get married?", _now())
    assert result["available"] is False
    assert result["route"] == "unsupported"


def test_router_keeps_financial_safety_limitation():
    result = route_finance_question_v1(_chart(), "Should I invest in stocks?", _now())
    assert result["route"] == "finance_natal"
    assert "financial advice" in result["limitation"].lower()


def test_overall_financial_question_routes_to_synthesis():
    result = route_finance_question_v1(_chart(), "Give me an overall financial overview and wealth future", _now())
    assert result["available"] is True
    assert result["route"] == "finance_synthesis"
    assert result["synthesis"]["event"] == "finance_synthesis"
    assert "components" in result["synthesis"]
    assert "financial advice" in result["limitation"].lower()


def test_multi_dimensional_question_routes_to_synthesis():
    result = route_finance_question_v1(
        _chart(),
        "Will I become wealthy, when is my strongest period, and will I retain the money?",
        _now(),
    )
    assert result["route"] == "finance_synthesis"
    assert result["synthesis"]["wealth_building_outlook"] in {"strong", "moderate", "limited"}


def test_explicit_year_keeps_priority_over_synthesis():
    result = route_finance_question_v1(
        _chart(), "Give me my overall financial picture for 2027", _now()
    )
    assert result["route"] == "finance_period_v2"
