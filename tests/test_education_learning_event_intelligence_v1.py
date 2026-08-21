from datetime import datetime, timezone

from app.astrology.features.education_learning_event_intelligence_v1 import analyze_education_learning_event_intelligence_v1


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {
            "3": {"lord": "Mercury"}, "4": {"lord": "Moon"}, "5": {"lord": "Jupiter"},
            "8": {"lord": "Saturn"}, "9": {"lord": "Mars"},
        },
        "planets": {
            "Mercury": {"house": 5}, "Moon": {"house": 4}, "Jupiter": {"house": 9},
            "Saturn": {"house": 8}, "Mars": {"house": 3}, "Venus": {"house": 5},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Mars"},
        ],
    }


def test_event_categories_are_separate_and_bounded():
    result = analyze_education_learning_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {
        "admission_or_enrolment", "exam_or_assessment", "higher_study_transition",
        "skill_or_certification", "research_or_deep_study",
    }
    for event in result["events"].values():
        assert 0.0 <= event["future"]["score"] <= 1.0


def test_past_events_are_never_confirmed_by_astrology():
    result = analyze_education_learning_event_intelligence_v1(_chart(), NOW)
    assert all(event["past"]["historical_status"] == "unconfirmed" for event in result["events"].values())
    assert "must not state" in result["historical_validation"]["rule"].lower()


def test_exam_and_admission_activation_are_not_outcome_guarantees():
    result = analyze_education_learning_event_intelligence_v1(_chart(), NOW)
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "activation, not outcome probability" in text
    assert "does not predict or guarantee admission" in text
    assert "exam success" in text


def test_strongest_future_event_is_known_category():
    result = analyze_education_learning_event_intelligence_v1(_chart(), NOW)
    assert result["strongest_future_event"] in result["events"]
