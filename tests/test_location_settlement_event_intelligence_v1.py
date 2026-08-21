from datetime import datetime, timezone

from app.astrology.features.location_settlement_event_intelligence_v1 import analyze_location_settlement_event_intelligence_v1


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


def test_event_categories_are_separate_and_bounded():
    result = analyze_location_settlement_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {"domestic_relocation", "foreign_travel_exposure", "long_distance_residence", "foreign_settlement", "return_or_re_rooting"}
    for event in result["events"].values():
        assert 0.0 <= event["future"]["score"] <= 1.0


def test_past_events_are_never_confirmed_by_astrology():
    result = analyze_location_settlement_event_intelligence_v1(_chart(), NOW)
    assert all(event["past"]["historical_status"] == "unconfirmed" for event in result["events"].values())
    assert "must not state" in result["historical_validation"]["rule"].lower()


def test_foreign_exposure_is_not_collapsed_into_settlement():
    result = analyze_location_settlement_event_intelligence_v1(_chart(), NOW)
    assert "foreign_travel_exposure" in result["events"]
    assert "foreign_settlement" in result["events"]
    assert result["events"]["foreign_travel_exposure"]["label"] != result["events"]["foreign_settlement"]["label"]


def test_immigration_and_location_guarantees_are_disallowed():
    result = analyze_location_settlement_event_intelligence_v1(_chart(), NOW)
    text = result["limitation"].lower()
    assert "visa approval" in text
    assert "citizenship" in text
    assert "particular country or city" in text
