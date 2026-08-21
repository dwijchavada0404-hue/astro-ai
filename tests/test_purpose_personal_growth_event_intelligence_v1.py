from datetime import datetime, timezone

from app.astrology.features.purpose_personal_growth_event_intelligence_v1 import analyze_purpose_personal_growth_event_intelligence_v1

NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"1": {"lord": "Sun"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"}, "9": {"lord": "Mercury"}, "10": {"lord": "Mars"}, "11": {"lord": "Venus"}, "12": {"lord": "Moon"}},
        "planets": {"Sun": {"house": 10}, "Jupiter": {"house": 9}, "Saturn": {"house": 6}, "Mercury": {"house": 5}, "Mars": {"house": 10}, "Venus": {"house": 11}, "Moon": {"house": 12}, "Ketu": {"house": 9}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
        ],
    }


def test_event_categories_are_separate_and_bounded():
    result = analyze_purpose_personal_growth_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {"identity_reorientation", "creative_expression_phase", "service_contribution_phase", "teaching_mentoring_guidance", "public_contribution_phase", "inner_growth_reflection"}
    for event in result["events"].values():
        assert 0.0 <= event["future"]["score"] <= 1.0


def test_past_growth_events_are_never_confirmed_by_astrology():
    result = analyze_purpose_personal_growth_event_intelligence_v1(_chart(), NOW)
    assert all(event["past"]["historical_status"] == "unconfirmed" for event in result["events"].values())
    assert "must not state" in result["historical_validation"]["rule"].lower()


def test_calling_and_spiritual_attainment_are_not_declared():
    result = analyze_purpose_personal_growth_event_intelligence_v1(_chart(), NOW)
    text = (result["historical_validation"]["rule"] + " " + result["limitation"]).lower()
    assert "found a calling" in text
    assert "spiritual attainment" in text
    assert "does not prove a calling" in text


def test_strongest_future_event_is_named():
    result = analyze_purpose_personal_growth_event_intelligence_v1(_chart(), NOW)
    assert result["strongest_future_event"] in result["events"]
    assert 0.0 <= result["strongest_future_event_score"] <= 1.0
