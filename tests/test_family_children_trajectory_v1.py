from datetime import datetime, timezone

from app.astrology.features.family_children_trajectory_v1 import analyze_family_children_trajectory_v1


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


def test_trajectory_scores_are_bounded():
    result = analyze_family_children_trajectory_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert result["available"] is True
    for key in (
        "stability_score",
        "responsibility_growth_score",
        "change_pressure_score",
        "support_network_score",
        "resilience_score",
        "recovery_score",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_trajectory_exposes_pattern_and_near_term_direction():
    result = analyze_family_children_trajectory_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert result["trajectory_pattern"] in {
        "stable_consolidation",
        "growth_with_adjustment",
        "transition_and_restructuring",
        "mixed_family_development",
    }
    assert result["near_term_direction"] in {
        "supportive_consolidation",
        "change_and_adjustment",
        "balanced_support_and_change",
    }


def test_reality_override_blocks_specific_unconfirmed_events():
    result = analyze_family_children_trajectory_v1(_chart(), datetime(2026, 8, 21, tzinfo=timezone.utc))
    text = result["reality_override"]["rule"].lower()
    assert result["reality_override"]["known_facts_override"] is True
    assert "must not be translated" in text
    assert "pregnancy" in text
    assert "separation" in text
    assert "bereavement" in text


def test_missing_foundation_is_unavailable():
    result = analyze_family_children_trajectory_v1({}, datetime(2026, 8, 21, tzinfo=timezone.utc))
    assert result["available"] is False
