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


def test_married_life_quality_api(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post("/api/v1/marriage-question-v3", json=_payload("Will my marriage be harmonious?"))
    assert response.status_code == 200
    body = response.json()
    assert body["understanding"]["primary_event"] == "married_life_quality"
    result = body["result"]
    assert result["event"] == "married_life_quality"
    assert result["evidence_engine"] == "married_life_quality_reasoning_v2"
    assert result["target"] == "harmony"
    assert result["answer"]
    assert result["limitation"]


def test_stable_marriage_api(monkeypatch):
    monkeypatch.setattr(chart_service, "resolve_place", _resolve_place)
    response = client.post("/api/v1/marriage-question-v3", json=_payload("Will my marriage be stable?"))
    assert response.status_code == 200
    assert response.json()["result"]["target"] == "stability"
