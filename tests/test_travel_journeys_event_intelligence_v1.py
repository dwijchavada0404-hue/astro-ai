from datetime import datetime, timezone

from app.astrology.features.travel_journeys_event_intelligence_v1 import analyze_travel_journeys_event_intelligence_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "6": {"lord": "Saturn"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}, "12": {"lord": "Rahu"}},
        "planets": {"Mercury": {"house": 3}, "Moon": {"house": 9}, "Jupiter": {"house": 9}, "Rahu": {"house": 12}, "Saturn": {"house": 6}, "Sun": {"house": 10}, "Mars": {"house": 3}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Moon"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Rahu", "sub_lord": "Mercury"},
        ],
    }


def test_event_intelligence_exposes_distinct_travel_themes():
    result = analyze_travel_journeys_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {"short_journey_activity", "long_distance_travel", "international_exposure", "work_study_travel", "recurring_mobility", "travel_adaptability"}
    assert result["strongest_future_event"] is not None


def test_event_activation_scores_are_bounded():
    result = analyze_travel_journeys_event_intelligence_v1(_chart(), NOW)
    for event in result["events"].values():
        for phase in ("past", "present", "future"):
            activation = event[phase]["activation"]
            if activation:
                assert 0.0 <= activation["activation_score"] <= 1.0


def test_historical_trips_remain_unconfirmed():
    result = analyze_travel_journeys_event_intelligence_v1(_chart(), NOW)
    assert all(event["past"]["historical_status"] == "unconfirmed" for event in result["events"].values())
    rule = result["historical_validation"]["rule"].lower()
    assert "not evidence" in rule
    assert "known travel history overrides astrology" in rule


def test_relocation_destination_and_safety_claims_are_disallowed():
    text = analyze_travel_journeys_event_intelligence_v1(_chart(), NOW)["limitation"].lower()
    assert "not probabilities" in text
    assert "exact destination" in text
    assert "relocation" in text and "permanent settlement" in text
    assert "travel safety" in text and "accident" in text
