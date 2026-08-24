from datetime import date, datetime, time, timezone

import pytest
from fastapi import HTTPException

from app.astrology.api import top_level_question_api_v1 as module
from app.models.chart import BirthInput


BIRTH = BirthInput(date=date(2000, 4, 4), time=time(14, 4), place="Mumbai")
NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def test_api_delegates_to_hardened_service_and_preserves_envelope(monkeypatch):
    monkeypatch.setattr(module, "build_chart", lambda birth: {"birth": {"place": birth.place}, "houses": {"1": {}}})
    seen = {}

    def fake_service(chart, question, reference_moment, life_context=None):
        seen.update(chart=chart, question=question, reference_moment=reference_moment, life_context=life_context)
        return {
            "api_contract_version": "v1",
            "status": "answered",
            "question": "How is my career?",
            "reference_moment": reference_moment.isoformat(),
            "domain": "career",
            "route": "top_level_to_career",
            "answer": "career answer",
            "limitation": "bounded",
            "result": {"available": True, "domain": "career", "route": "top_level_to_career", "answer": "career answer"},
            "meta": {"deterministic_router": True, "reality_override_enabled": False, "guaranteed_outcome": False},
        }

    monkeypatch.setattr(module, "answer_unified_question_v1", fake_service)
    payload = module.AstroAIQuestionV1Request(
        birth=BIRTH,
        question="How is my career?",
        reference_moment=NOW,
    )
    response = module.answer_astroai_question_v1(payload)

    assert response["api_contract_version"] == "v1"
    assert response["status"] == "answered"
    assert response["domain"] == "career"
    assert response["meta"]["deterministic_router"] is True
    assert response["birth"]["place"] == "Mumbai"
    assert seen["question"] == "How is my career?"
    assert seen["life_context"] is None


def test_api_merges_life_context_updates_before_service(monkeypatch):
    monkeypatch.setattr(module, "build_chart", lambda birth: {"birth": {}, "houses": {"1": {}}})
    captured = {}

    def fake_service(chart, question, reference_moment, life_context=None):
        captured["life_context"] = life_context
        return {
            "api_contract_version": "v1", "status": "answered", "question": question,
            "reference_moment": reference_moment.isoformat(), "domain": "career", "route": "top_level_to_career",
            "answer": "answer", "limitation": None,
            "result": {"available": True, "domain": "career", "route": "top_level_to_career", "answer": "answer", "life_context": life_context},
            "meta": {"deterministic_router": True, "reality_override_enabled": True, "guaranteed_outcome": False},
        }

    monkeypatch.setattr(module, "answer_unified_question_v1", fake_service)
    payload = module.AstroAIQuestionV1Request(
        birth=BIRTH,
        question="When will I settle in life?",
        reference_moment=NOW,
        life_context=module.LifeContextV1(milestones={"career": module.MilestoneContextV1(state="likely_pending")}),
        life_context_updates=module.LifeContextV1(
            milestones={"career": module.MilestoneContextV1(state="user_confirmed_achieved", achieved_date=date(2025, 6, 1))}
        ),
    )
    response = module.answer_astroai_question_v1(payload)

    assert captured["life_context"]["milestones"]["career"]["state"] == "user_confirmed_achieved"
    assert response["next_life_context"]["milestones"]["career"]["state"] == "user_confirmed_achieved"
    assert response["meta"]["reality_override_enabled"] is True


def test_service_validation_error_becomes_http_400(monkeypatch):
    monkeypatch.setattr(module, "build_chart", lambda birth: {"birth": {}, "houses": {"1": {}}})

    def fail(*args, **kwargs):
        raise ValueError("reference_moment must include a timezone offset.")

    monkeypatch.setattr(module, "answer_unified_question_v1", fail)
    payload = module.AstroAIQuestionV1Request(
        birth=BIRTH,
        question="How is my career?",
        reference_moment=datetime(2026, 8, 24),
    )
    with pytest.raises(HTTPException) as exc:
        module.answer_astroai_question_v1(payload)
    assert exc.value.status_code == 400
    assert "timezone" in str(exc.value.detail).lower()


def test_request_model_caps_question_length():
    with pytest.raises(Exception):
        module.AstroAIQuestionV1Request(
            birth=BIRTH,
            question="x" * 1001,
            reference_moment=NOW,
        )
