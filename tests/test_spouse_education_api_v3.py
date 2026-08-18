from fastapi.testclient import TestClient
from app.main import app
from app.services import chart_service
client=TestClient(app)
def rp(place): return {"resolved_name":"Mumbai, Maharashtra, India","latitude":19.076,"longitude":72.8777,"timezone":"Asia/Kolkata"}
def payload(q): return {"birth":{"date":"2000-04-04","time":"14:04:00","place":"Mumbai, Maharashtra, India"},"question":q,"reference_moment":"2026-08-15T12:00:00+05:30"}
def test_api(monkeypatch):
    monkeypatch.setattr(chart_service,"resolve_place",rp)
    response=client.post("/api/v1/marriage-question-v3",json=payload("Will my spouse be highly educated?"))
    assert response.status_code==200
    body=response.json()
    assert body["understanding"]["primary_event"]=="spouse_education"
    assert body["result"]["event"]=="spouse_education"
    assert body["result"]["evidence_engine"]=="spouse_education_reasoning_v2"
def test_finance_degree(monkeypatch):
    monkeypatch.setattr(chart_service,"resolve_place",rp)
    body=client.post("/api/v1/marriage-question-v3",json=payload("Will my spouse have a finance degree?")).json()
    assert body["understanding"]["primary_event"]=="spouse_education"
    assert body["result"]["target"]=="finance_commerce"
