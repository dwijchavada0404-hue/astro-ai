from datetime import datetime, timezone

import pytest

from app.services import unified_question_service_v1 as module

NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)
CHART = {"houses": {"1": {"lord": "Sun"}}, "planets": {"Sun": {"house": 1}}}


def test_service_normalizes_successful_router_output(monkeypatch):
    monkeypatch.setattr(
        module,
        "route_top_level_question_v1",
        lambda chart, question, moment, life_context=None: {
            "available": True,
            "domain": "career",
            "route": "top_level_to_career",
            "answer": "career answer",
            "limitation": "symbolic only",
        },
    )
    result = module.answer_unified_question_v1(CHART, "  How   is my career?  ", NOW)
    assert result["api_contract_version"] == "v1"
    assert result["status"] == "answered"
    assert result["question"] == "How is my career?"
    assert result["domain"] == "career"
    assert result["answer"] == "career answer"
    assert result["meta"]["deterministic_router"] is True
    assert result["meta"]["guaranteed_outcome"] is False


def test_job_change_timing_uses_event_window_not_engine_methodology(monkeypatch):
    monkeypatch.setattr(
        module,
        "route_top_level_question_v1",
        lambda chart, question, moment, life_context=None: {
            "available": True,
            "domain": "career",
            "route": "career_event_v1",
            "answer": "Career event themes are ranked from natal evidence and available dasha timing. Scores represent symbolic activation strength.",
            "result": {
                "primary_intent": "job_change",
                "event_result": {
                    "future": {
                        "event_specific_period": {
                            "start": "2027-02-12T00:00:00+05:30",
                            "end": "2027-10-19T00:00:00+05:30",
                        }
                    }
                },
            },
        },
    )
    result = module.answer_unified_question_v1(CHART, "Meri job change kab hogi", NOW)
    assert "Feb 2027 – Oct 2027" in result["answer"]
    assert "job change" in result["answer"].lower()
    assert "Career event themes are ranked" not in result["answer"]
    assert "symbolic activation strength" not in result["answer"]


def test_job_change_timing_respects_english_language(monkeypatch):
    monkeypatch.setattr(
        module,
        "route_top_level_question_v1",
        lambda chart, question, moment, life_context=None: {
            "available": True,
            "domain": "career",
            "route": "career_event_v1",
            "result": {"primary_intent": "job_change", "event_result": {"future": {"career_timing_period": {"start": "2028-01-01", "end": "2028-06-30"}}}},
        },
    )
    result = module.answer_unified_question_v1(CHART, "When will I change jobs?", NOW, answer_language="english")
    assert result["answer"].startswith("Your chart shows Jan 2028 – Jun 2028")


def test_unsupported_question_has_stable_envelope(monkeypatch):
    monkeypatch.setattr(
        module,
        "route_top_level_question_v1",
        lambda chart, question, moment, life_context=None: {
            "available": False,
            "event": "unknown",
            "route": "unsupported",
            "domain": None,
            "reason": "Unsupported question.",
        },
    )
    result = module.answer_unified_question_v1(CHART, "paint my desk", NOW)
    assert result["status"] == "unsupported"
    assert result["domain"] is None
    assert result["answer"] == "Unsupported question."
    assert result["route"] == "unsupported"


def test_life_context_is_forwarded_and_marked(monkeypatch):
    captured = {}

    def fake_router(chart, question, moment, life_context=None):
        captured["life_context"] = life_context
        return {"available": True, "domain": "life_settlement", "route": "life_settlement_answer_v1", "answer": "settlement answer"}

    monkeypatch.setattr(module, "route_top_level_question_v1", fake_router)
    context = {"career": {"status": "achieved"}}
    result = module.answer_unified_question_v1(CHART, "When will life settle?", NOW, life_context=context)
    assert captured["life_context"] == context
    assert result["meta"]["reality_override_enabled"] is True


def test_question_length_is_bounded():
    with pytest.raises(ValueError, match="1000"):
        module.answer_unified_question_v1(CHART, "x" * 1001, NOW)


def test_empty_question_is_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        module.answer_unified_question_v1(CHART, "   ", NOW)


def test_timezone_is_required():
    with pytest.raises(ValueError, match="timezone"):
        module.answer_unified_question_v1(CHART, "How is my career?", datetime(2026, 8, 24))


def test_chart_must_be_non_empty_dictionary():
    with pytest.raises(ValueError, match="must not be empty"):
        module.answer_unified_question_v1({}, "How is my career?", NOW)
    with pytest.raises(ValueError, match="dictionary"):
        module.answer_unified_question_v1([], "How is my career?", NOW)  # type: ignore[arg-type]


def test_life_context_type_is_validated():
    with pytest.raises(ValueError, match="life_context"):
        module.answer_unified_question_v1(CHART, "How is my career?", NOW, life_context=[])  # type: ignore[arg-type]


@pytest.mark.parametrize("raw", [
    "The longer-term Travel & Journeys trajectory is adaptive mobility, with a near-term direction of expansion.",
    "The combined Legal, Disputes & Conflict outlook is negotiation and resolution emphasis.",
])
def test_raw_engine_trajectory_and_synthesis_copy_use_natural_fallback(monkeypatch, raw):
    monkeypatch.setattr(
        module,
        "route_top_level_question_v1",
        lambda chart, question, moment, life_context=None: {
            "available": True,
            "domain": "career",
            "route": "top_level_to_career",
            "answer": raw,
            "result": {},
        },
    )
    result = module.answer_unified_question_v1(CHART, "How is my career?", NOW)
    assert result["answer"] != raw
    assert "clear indication" in result["answer"]
