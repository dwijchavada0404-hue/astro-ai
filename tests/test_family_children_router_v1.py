from datetime import datetime, timezone

from app.astrology.features.family_children_router_v1 import route_family_children_question_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Venus"},
            "4": {"lord": "Moon"},
            "5": {"lord": "Jupiter"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Mars"},
            "11": {"lord": "Mercury"},
            "12": {"lord": "Sun"},
        },
        "planets": {
            "Venus": {"house": 4},
            "Moon": {"house": 5},
            "Jupiter": {"house": 9},
            "Saturn": {"house": 8},
            "Mars": {"house": 11},
            "Mercury": {"house": 2},
            "Sun": {"house": 12},
        },
        "dashas": {
            "mahadashas": [
                {
                    "planet": "Jupiter",
                    "start": "2022-01-01T00:00:00+00:00",
                    "end": "2028-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Saturn", "start": "2026-01-01T00:00:00+00:00", "end": "2028-12-31T23:59:59+00:00"}
                    ],
                },
                {
                    "planet": "Venus",
                    "start": "2029-01-01T00:00:00+00:00",
                    "end": "2033-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Jupiter", "start": "2029-01-01T00:00:00+00:00", "end": "2033-12-31T23:59:59+00:00"}
                    ],
                },
            ]
        },
    }


def _now():
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_when_will_i_have_children_routes_to_guarded_parenting_event():
    result = route_family_children_question_v1(_chart(), "When will I have children?", _now())
    assert result["available"] is True
    assert result["route"] == "family_children_event_v1"
    assert result["event_key"] == "parenting_nurturing"
    boundary = result["children_question_boundary"].lower()
    assert "must not be converted" in boundary
    assert "pregnancy" in boundary


def test_family_overview_routes_to_synthesis():
    result = route_family_children_question_v1(_chart(), "Tell me about my overall family future", _now())
    assert result["route"] == "family_children_synthesis_v1"
    assert result["synthesis"]["historical_validation"]["status"] == "unconfirmed"


def test_family_stability_routes_to_direction():
    result = route_family_children_question_v1(_chart(), "How is my family stability?", _now())
    assert result["route"] == "family_children_direction_v1"


def test_generic_family_timing_routes_to_timing_engine():
    result = route_family_children_question_v1(_chart(), "When is my strongest family period?", _now())
    assert result["route"] == "family_children_timing_v1"
    assert result["timing"]["available"] is True


def test_unrelated_question_is_declined():
    result = route_family_children_question_v1(_chart(), "When will I get promoted?", _now())
    assert result["available"] is False
    assert result["route"] == "unsupported"
