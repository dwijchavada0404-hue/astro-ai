from datetime import datetime, timezone

from app.astrology.features.family_children_synthesis_v1 import analyze_family_children_synthesis_v1


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


def test_synthesis_combines_all_family_layers():
    result = analyze_family_children_synthesis_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert result["available"] is True
    assert set(result["components"]) == {"natal", "direction", "timing", "events", "trajectory"}
    assert all(result["component_availability"].values())


def test_synthesis_scores_are_bounded():
    result = analyze_family_children_synthesis_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert 0.0 <= result["family_development_score"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["strongest_future_event_score"] <= 1.0
    assert 0.0 <= result["future_family_support_score"] <= 1.0
    assert 0.0 <= result["future_family_change_score"] <= 1.0


def test_synthesis_preserves_reality_override_and_children_boundary():
    result = analyze_family_children_synthesis_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert historical["reality_override"] is True
    assert "known family and children history overrides" in historical["rule"].lower()
    boundary = result["children_question_boundary"].lower()
    assert "cannot diagnose fertility" in boundary
    assert "pregnancy" in boundary
    assert "number or sex of children" in boundary


def test_synthesis_language_is_non_deterministic():
    result = analyze_family_children_synthesis_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "symbolic astrological synthesis" in text
    assert "does not predict or guarantee" in text


def test_missing_foundation_is_unavailable():
    result = analyze_family_children_synthesis_v1({}, datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert result["available"] is False
