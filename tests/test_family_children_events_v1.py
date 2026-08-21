from datetime import datetime, timezone

from app.astrology.features.family_children_events_v1 import analyze_family_children_events_v1


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


def test_events_are_separate_and_bounded():
    result = analyze_family_children_events_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert result["available"] is True
    assert set(result["event_scores"]) == {
        "parenting_nurturing",
        "family_growth_responsibility",
        "family_structure_change",
        "intergenerational_support",
        "family_stability",
    }
    assert all(0.0 <= score <= 1.0 for score in result["event_scores"].values())


def test_children_event_is_not_biological_prediction():
    result = analyze_family_children_events_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    text = (result["children_question_boundary"] + " " + result["limitation"]).lower()
    assert "parenting" in text
    assert "must not be converted" in text
    assert "pregnancy" in text
    assert "child-count" in text
    assert "does not predict or guarantee" in text


def test_historical_validation_preserves_reality_override():
    result = analyze_family_children_events_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert historical["reality_override"] is True
    assert "known family history overrides" in historical["rule"].lower()


def test_missing_foundation_is_unavailable():
    result = analyze_family_children_events_v1({}, datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert result["available"] is False
