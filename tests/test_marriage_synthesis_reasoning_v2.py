from datetime import datetime, timezone

import pytest

import app.astrology.features.marriage_synthesis_reasoning_v2 as synthesis_v2


def _chart():
    return {"houses": {"7": {"lord": "Venus"}}, "planets": {"Venus": {"house": 7}}}


def test_v2_orchestrates_existing_marriage_routes(monkeypatch):
    def fake_analyze(question):
        return {"original_question": question, "primary_event": "stub", "query_mode": "single_event"}

    counter = {"value": 0}

    def fake_route(chart, question_analysis, reference_moment):
        counter["value"] += 1
        return {
            "available": True,
            "event": f"event_{counter['value']}",
            "answer": f"statement {counter['value']}",
            "confidence": 0.7,
        }

    monkeypatch.setattr(synthesis_v2, "analyze_marriage_question_v3", fake_analyze)
    monkeypatch.setattr(synthesis_v2, "route_marriage_question_v3", fake_route)

    queries = (("spouse_traits", "traits?"), ("married_life_quality", "quality?"))
    result = synthesis_v2.synthesize_marriage_profile_v2(
        _chart(), datetime(2026, 8, 19, tzinfo=timezone.utc), include_timing=False, component_queries=queries
    )

    assert result["available"] is True
    assert result["model_version"] == "v2"
    assert result["orchestration"]["requested_component_count"] == 2
    assert result["orchestration"]["collected_component_count"] == 2
    assert len(result["orchestration"]["collection_errors"]) == 2


def test_v2_can_skip_expensive_timing_components(monkeypatch):
    called = []

    def fake_collect(chart, reference_moment, expected_event, question):
        called.append(expected_event)
        return {"available": True, "event": expected_event, "answer": expected_event, "confidence": 0.7}

    monkeypatch.setattr(synthesis_v2, "_collect_component", fake_collect)
    result = synthesis_v2.synthesize_marriage_profile_v2(
        _chart(),
        datetime(2026, 8, 19, tzinfo=timezone.utc),
        include_timing=False,
        component_queries=(
            ("marriage_timing", "timing"),
            ("spouse_meeting", "meeting"),
            ("spouse_traits", "traits"),
        ),
    )
    assert called == ["spouse_traits"]
    assert result["orchestration"]["requested_component_count"] == 1


def test_v2_isolates_component_failure(monkeypatch):
    def fake_collect(chart, reference_moment, expected_event, question):
        if expected_event == "relationship_challenges":
            raise RuntimeError("engine unavailable")
        return {"available": True, "event": expected_event, "answer": "usable", "confidence": 0.8}

    monkeypatch.setattr(synthesis_v2, "_collect_component", fake_collect)
    result = synthesis_v2.synthesize_marriage_profile_v2(
        _chart(),
        datetime(2026, 8, 19, tzinfo=timezone.utc),
        include_timing=False,
        component_queries=(("spouse_traits", "traits"), ("relationship_challenges", "challenges")),
    )
    assert result["available"] is True
    assert result["component_count"] == 1
    assert result["orchestration"]["collected_component_count"] == 1
    assert result["orchestration"]["collection_errors"][0]["event"] == "relationship_challenges"


def test_v2_requires_timezone_aware_reference_moment():
    with pytest.raises(ValueError):
        synthesis_v2.synthesize_marriage_profile_v2(_chart(), datetime(2026, 8, 19))


def test_v2_rejects_bad_chart():
    with pytest.raises(ValueError):
        synthesis_v2.synthesize_marriage_profile_v2([], datetime(2026, 8, 19, tzinfo=timezone.utc))
