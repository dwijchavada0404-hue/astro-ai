from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.astrology.api import top_level_question_api_v1 as module


app = FastAPI()
app.include_router(module.router)
client = TestClient(app)


def _payload():
    return {
        "birth": {
            "date": "2000-04-04",
            "time": "14:04:00",
            "place": "Mumbai, India",
        },
        "question": "When will I be settled in life?",
        "reference_moment": "2026-08-21T12:00:00+05:30",
    }


def test_top_level_question_endpoint_routes_result(monkeypatch):
    monkeypatch.setattr(module, "build_chart", lambda birth: {"birth": {"date": "2000-04-04"}})
    monkeypatch.setattr(
        module,
        "route_top_level_question_v1",
        lambda chart, question, moment: {
            "available": True,
            "domain": "life_settlement",
            "route": "life_settlement_answer_v1",
            "answer": "bounded cross-domain answer",
        },
    )
    response = client.post("/api/v1/question", json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "life_settlement"
    assert body["route"] == "life_settlement_answer_v1"
    assert body["answer"] == "bounded cross-domain answer"
    assert "Known facts override" in body["disclaimer"]


def test_top_level_question_endpoint_surfaces_siblings_domain(monkeypatch):
    monkeypatch.setattr(module, "build_chart", lambda birth: {"birth": {"date": "2000-04-04"}})
    monkeypatch.setattr(
        module,
        "route_top_level_question_v1",
        lambda chart, question, moment: {
            "available": True,
            "domain": "siblings_communication",
            "route": "top_level_to_siblings_communication",
            "answer": "bounded sibling and communication answer",
            "limitation": "No specific-person loyalty or conflict prediction.",
        },
    )
    payload = _payload()
    payload["question"] = "What are my sibling and communication themes?"
    response = client.post("/api/v1/question", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "siblings_communication"
    assert body["route"] == "top_level_to_siblings_communication"
    assert body["answer"] == "bounded sibling and communication answer"
    assert body["result"]["limitation"]


def test_top_level_question_endpoint_requires_timezone():
    payload = _payload()
    payload["reference_moment"] = "2026-08-21T12:00:00"
    response = client.post("/api/v1/question", json=payload)
    assert response.status_code == 400
    assert "timezone" in response.json()["detail"].lower()


def test_top_level_question_endpoint_rejects_blank_question():
    payload = _payload()
    payload["question"] = "   "
    response = client.post("/api/v1/question", json=payload)
    assert response.status_code == 400
