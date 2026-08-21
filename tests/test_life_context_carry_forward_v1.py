from fastapi.testclient import TestClient
import pytest

from app.astrology.api import top_level_question_api_v1 as api_module
from app.astrology.features.life_context_v1 import merge_life_context_v1
from app.main import app


client = TestClient(app)


def test_merge_advances_sparse_milestone_state():
    current = {
        "milestones": {
            "career_stability": {"state": "likely_pending", "note": "still developing"},
            "home_property": {"state": "unknown"},
        }
    }
    updates = {
        "milestones": {
            "career_stability": {
                "state": "user_confirmed_achieved",
                "achieved_date": "2026-08-01",
            }
        }
    }
    merged = merge_life_context_v1(current, updates)
    assert merged["milestones"]["career_stability"]["state"] == "user_confirmed_achieved"
    assert merged["milestones"]["career_stability"]["achieved_date"] == "2026-08-01"
    assert merged["milestones"]["career_stability"]["note"] == "still developing"
    assert merged["milestones"]["home_property"]["state"] == "unknown"


def test_confirmed_achievement_cannot_be_downgraded():
    current = {
        "milestones": {
            "committed_relationship": {"state": "user_confirmed_achieved"}
        }
    }
    updates = {
        "milestones": {
            "committed_relationship": {"state": "likely_pending"}
        }
    }
    with pytest.raises(ValueError, match="cannot move backward"):
        merge_life_context_v1(current, updates)


def test_likely_pending_can_advance_to_confirmed():
    merged = merge_life_context_v1(
        {"milestones": {"financial_stability": {"state": "likely_pending"}}},
        {"milestones": {"financial_stability": {"state": "user_confirmed_achieved"}}},
    )
    assert merged["confirmed_achieved"] == ["financial_stability"]
    assert merged["likely_pending"] == []


def _payload():
    return {
        "birth": {
            "date": "2000-04-04",
            "time": "14:04:00",
            "place": "Mumbai, India",
        },
        "question": "When will I be settled in life?",
        "reference_moment": "2026-08-21T12:00:00+05:30",
        "life_context": {
            "milestones": {
                "career_stability": {"state": "likely_pending"},
                "home_property": {"state": "unknown"},
            }
        },
        "life_context_updates": {
            "milestones": {
                "career_stability": {
                    "state": "user_confirmed_achieved",
                    "achieved_date": "2026-08-01",
                }
            }
        },
    }


def test_api_returns_canonical_next_life_context(monkeypatch):
    monkeypatch.setattr(api_module, "build_chart", lambda birth: {"birth": {"date": "2000-04-04"}})

    seen = {}

    def fake_route(chart, question, moment, *, life_context=None):
        seen["context"] = life_context
        return {
            "available": True,
            "domain": "life_settlement",
            "route": "life_settlement_answer_v1",
            "answer": "bounded answer",
            "life_context": life_context,
        }

    monkeypatch.setattr(api_module, "route_top_level_question_v1", fake_route)
    response = client.post("/api/v1/question", json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["next_life_context"]["milestones"]["career_stability"]["state"] == "user_confirmed_achieved"
    assert body["next_life_context"]["milestones"]["home_property"]["state"] == "unknown"
    assert seen["context"]["confirmed_achieved"] == ["career_stability"]


def test_api_rejects_backward_context_update(monkeypatch):
    monkeypatch.setattr(api_module, "build_chart", lambda birth: {"birth": {"date": "2000-04-04"}})
    payload = _payload()
    payload["life_context"] = {
        "milestones": {
            "career_stability": {"state": "user_confirmed_achieved"}
        }
    }
    payload["life_context_updates"] = {
        "milestones": {
            "career_stability": {"state": "likely_pending"}
        }
    }
    response = client.post("/api/v1/question", json=payload)
    assert response.status_code == 400
    assert "cannot move backward" in response.json()["detail"]
