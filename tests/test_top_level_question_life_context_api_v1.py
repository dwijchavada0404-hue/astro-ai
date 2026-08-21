from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.astrology.api import top_level_question_api_v1 as api_module


app = FastAPI()
app.include_router(api_module.router)
client = TestClient(app)


BIRTH = {
    "date": "2000-04-04",
    "time": "14:04:00",
    "place": "Mumbai, India",
}


def _payload():
    return {
        "birth": BIRTH,
        "question": "When will I be settled in life?",
        "reference_moment": "2026-08-21T12:00:00+05:30",
        "life_context": {
            "milestones": {
                "home_property": {
                    "state": "user_confirmed_achieved",
                    "achieved_date": "2026-03-01",
                    "note": "Already achieved",
                }
            }
        },
    }


def test_api_passes_normalized_life_context_to_router(monkeypatch):
    seen = {}
    monkeypatch.setattr(api_module, "build_chart", lambda birth: {"birth": {"date": "2000-04-04"}})

    def fake_route(chart, question, reference_moment, life_context=None):
        seen["life_context"] = life_context
        return {
            "available": True,
            "domain": "life_settlement",
            "route": "life_settlement_answer_v1",
            "answer": "Reality-aware answer.",
            "life_context": life_context,
            "reality_reconciliation": {"applied": True},
        }

    monkeypatch.setattr(api_module, "route_top_level_question_v1", fake_route)

    response = client.post("/api/v1/question", json=_payload())

    assert response.status_code == 200
    data = response.json()
    assert seen["life_context"]["milestones"]["home_property"]["state"] == "user_confirmed_achieved"
    assert seen["life_context"]["milestones"]["home_property"]["achieved_date"] == "2026-03-01"
    assert data["reality_reconciliation"]["applied"] is True
    assert data["life_context"]["milestones"]["home_property"]["state"] == "user_confirmed_achieved"


def test_existing_request_without_life_context_remains_valid(monkeypatch):
    monkeypatch.setattr(api_module, "build_chart", lambda birth: {"birth": {"date": "2000-04-04"}})
    seen = {}

    def fake_route(chart, question, reference_moment, life_context=None):
        seen["life_context"] = life_context
        return {
            "available": True,
            "domain": "career",
            "route": "top_level_to_career",
            "answer": "Existing answer.",
        }

    monkeypatch.setattr(api_module, "route_top_level_question_v1", fake_route)
    payload = _payload()
    payload.pop("life_context")

    response = client.post("/api/v1/question", json=payload)

    assert response.status_code == 200
    assert seen["life_context"] is None
    assert response.json()["answer"] == "Existing answer."


def test_pydantic_rejects_invalid_milestone_state():
    payload = _payload()
    payload["life_context"]["milestones"]["home_property"]["state"] = "definitely_done"

    response = client.post("/api/v1/question", json=payload)

    assert response.status_code == 422
