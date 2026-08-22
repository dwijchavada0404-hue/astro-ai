from datetime import datetime, timezone

from app.astrology.features.parents_elders_event_intelligence_v1 import analyze_parents_elders_event_intelligence_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"4": {"lord": "Moon"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}}, "planets": {"Moon": {"house": 4}, "Jupiter": {"house": 9}, "Sun": {"house": 10}, "Saturn": {"house": 6}, "Mars": {"house": 3}, "Venus": {"house": 4}}, "dasha_periods": [{"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Jupiter"}, {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"}]}


def test_event_intelligence_exposes_distinct_parent_elder_themes():
    result = analyze_parents_elders_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {"guidance_mentorship", "emotional_support", "duty_responsibility", "authority_structure", "independence_boundaries", "family_continuity"}
    assert result["strongest_future_event"] is not None


def test_event_activation_scores_are_bounded():
    result = analyze_parents_elders_event_intelligence_v1(_chart(), NOW)
    for event in result["events"].values():
        for phase in ("past", "present", "future"):
            activation = event[phase]["activation"]
            if activation:
                assert 0.0 <= activation["activation_score"] <= 1.0


def test_historical_family_events_remain_unconfirmed():
    result = analyze_parents_elders_event_intelligence_v1(_chart(), NOW)
    assert all(event["past"]["historical_status"] == "unconfirmed" for event in result["events"].values())
    rule = result["historical_validation"]["rule"].lower()
    assert "not evidence" in rule
    assert "known family history overrides astrology" in rule


def test_health_death_intentions_and_outcomes_are_disallowed():
    text = analyze_parents_elders_event_intelligence_v1(_chart(), NOW)["limitation"].lower()
    assert "health" in text and "illness" in text
    assert "lifespan" in text and "death" in text
    assert "intentions or character" in text
    assert "reconciliation" in text and "caregiving" in text
