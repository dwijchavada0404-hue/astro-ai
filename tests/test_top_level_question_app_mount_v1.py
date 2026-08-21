from fastapi.testclient import TestClient

from app.astrology.api import top_level_question_api_v1 as api_module
from app.main import app


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


def test_top_level_question_is_mounted_on_main_app(monkeypatch):
    monkeypatch.setattr(api_module, "build_chart", lambda birth: {"birth": {"date": "2000-04-04"}})
    monkeypatch.setattr(
        api_module,
        "route_top_level_question_v1",
        lambda chart, question, moment: {
            "available": True,
            "domain": "life_settlement",
            "route": "life_settlement_answer_v1",
            "answer": "cross-domain settlement answer",
        },
    )

    response = client.post("/api/v1/question", json=_payload())

    assert response.status_code == 200
    assert response.json()["domain"] == "life_settlement"
    assert response.json()["route"] == "life_settlement_answer_v1"


def test_main_app_openapi_exposes_top_level_question_route():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/question" in response.json()["paths"]
