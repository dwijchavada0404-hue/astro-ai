from fastapi.testclient import TestClient

from app.main import app
from app.services import chart_service


client = TestClient(app)


def _resolve_place(place):
    return {
        "resolved_name": "Mumbai, Maharashtra, India",
        "latitude": 19.076,
        "longitude": 72.8777,
        "timezone": "Asia/Kolkata",
    }


def _payload(question):
    return {
        "birth": {
            "date": "2000-04-04",
            "time": "14:04:00",
            "place": "Mumbai, Maharashtra, India",
        },
        "question": question,
        "reference_moment": "2026-08-15T12:00:00+05:30",
    }


def test_spouse_wealth_api(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload("Will my spouse be wealthy?"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["understanding"]["primary_event"] == "spouse_wealth"
    assert body["result"]["event"] == "spouse_wealth"
    assert body["result"]["evidence_engine"] == "spouse_wealth_reasoning_v2"
    assert body["result"]["target"] == "wealthy"


def test_spouse_family_wealth_api(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload("Will my spouse come from a wealthy family?"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["understanding"]["primary_event"] == "spouse_wealth"
    assert body["result"]["target"] == "family_wealth"


def test_profession_question_remains_profession(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post(
        "/api/v1/marriage-question-v3",
        json=_payload("Will my spouse work in finance?"),
    )
    assert response.status_code == 200
    assert response.json()["understanding"]["primary_event"] == "spouse_profession"
