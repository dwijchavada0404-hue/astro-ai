from datetime import datetime, timezone

from app.astrology.features.location_settlement_trajectory_v1 import analyze_location_settlement_trajectory_v1


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "4": {"lord": "Moon"}, "7": {"lord": "Mars"}, "9": {"lord": "Jupiter"}, "12": {"lord": "Saturn"}},
        "planets": {"Mercury": {"house": 9}, "Moon": {"house": 12}, "Mars": {"house": 7}, "Jupiter": {"house": 12}, "Saturn": {"house": 4}, "Rahu": {"house": 9}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Rahu"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Jupiter"},
        ],
    }


def test_trajectory_scores_are_bounded_and_multidimensional():
    result = analyze_location_settlement_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    expected = {"home_base_stability", "mobility_trajectory", "international_trajectory", "foreign_settlement_trajectory", "location_change_pressure", "adaptability", "re_rooting_capacity"}
    assert set(result["scores"]) == expected
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_settlement_trajectory_does_not_equal_guaranteed_emigration():
    result = analyze_location_settlement_trajectory_v1(_chart(), NOW)
    text = result["limitation"].lower()
    assert "does not guarantee emigration" in text
    assert "temporary residence" in text
    assert "multiple home bases" in text


def test_reality_override_is_preserved():
    result = analyze_location_settlement_trajectory_v1(_chart(), NOW)
    validation = result["historical_validation"]
    assert validation["reality_override"] is True
    assert validation["status"] == "unconfirmed"
    assert "confirmed residence" in validation["rule"].lower()
