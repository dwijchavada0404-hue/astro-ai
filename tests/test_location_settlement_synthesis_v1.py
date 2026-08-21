from datetime import datetime, timezone

from app.astrology.features.location_settlement_synthesis_v1 import analyze_location_settlement_synthesis_v1


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


def test_synthesis_is_bounded_and_has_full_component_evidence():
    result = analyze_location_settlement_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["scores"]) == {"rooted_home_base", "relocation", "foreign_exposure", "long_distance_residence", "foreign_settlement"}
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0
    assert set(result["components"]) == {"natal", "timing", "events", "trajectory"}


def test_exposure_and_settlement_remain_distinct_at_top_level():
    result = analyze_location_settlement_synthesis_v1(_chart(), NOW)
    assert "foreign_exposure" in result["scores"]
    assert "foreign_settlement" in result["scores"]
    assert "evaluated separately" in result["answer"].lower()


def test_reality_override_survives_advanced_synthesis():
    result = analyze_location_settlement_synthesis_v1(_chart(), NOW)
    validation = result["historical_validation"]
    assert validation["reality_override"] is True
    assert validation["status"] == "unconfirmed"
    assert "must never manufacture" in validation["rule"].lower()


def test_immigration_boundary_survives_top_level_synthesis():
    result = analyze_location_settlement_synthesis_v1(_chart(), NOW)
    text = result["limitation"].lower()
    assert "does not guarantee" in text
    assert "visa approval" in text
    assert "citizenship" in text
    assert "specific country or city" in text
