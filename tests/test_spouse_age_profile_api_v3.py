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
        "birth": {"date": "2000-04-04", "time": "14:04:00", "place": "Mumbai, Maharashtra, India"},
        "question": question,
        "reference_moment": "2026-08-15T12:00:00+05:30",
    }


def test_spouse_age_profile_api(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post("/api/v1/marriage-question-v3", json=_payload("Will my spouse be older than me?"))
    assert response.status_code == 200
    body = response.json()
    assert body["understanding"]["primary_event"] == "spouse_age_profile"
    result = body["result"]
    assert result["event"] == "spouse_age_profile"
    assert result["evidence_engine"] == "spouse_age_profile_reasoning_v2"
    assert result["target"] == "older_spouse"
    assert result["answer"]
    assert result["limitation"]


def test_younger_spouse_api(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post("/api/v1/marriage-question-v3", json=_payload("Will my spouse be younger than me?"))
    assert response.status_code == 200
    assert response.json()["result"]["target"] == "younger_spouse"


def test_similar_age_spouse_api(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post("/api/v1/marriage-question-v3", json=_payload("Will my spouse be around my age?"))
    assert response.status_code == 200
    assert response.json()["result"]["target"] == "similar_age_spouse"
