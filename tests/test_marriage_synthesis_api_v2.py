from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


BIRTH = {
    "date": "2000-04-04",
    "time": "10:32:00",
    "place": "Mumbai, Maharashtra, India",
}


def test_marriage_synthesis_route_is_registered():
    paths = {getattr(route, "path", None) for route in main.app.routes}
    assert "/api/v1/marriage-synthesis-v2" in paths


def test_marriage_synthesis_endpoint_wires_chart_and_engine(monkeypatch):
    seen = {}

    def fake_build_chart(birth):
        seen["birth"] = birth
        return {"birth": {"place": birth.place}, "houses": {}, "planets": {}}

    def fake_synthesis(chart, reference_moment, *, include_timing=True):
        seen["chart"] = chart
        seen["reference_moment"] = reference_moment
        seen["include_timing"] = include_timing
        return {
            "available": True,
            "event": "marriage_synthesis",
            "model_version": "v2",
            "component_count": 13,
            "headline": "coherent marriage synthesis",
        }

    monkeypatch.setattr(main, "build_chart", fake_build_chart)
    monkeypatch.setattr(main, "synthesize_marriage_profile_v2", fake_synthesis)

    response = client.post(
        "/api/v1/marriage-synthesis-v2",
        json={
            "birth": BIRTH,
            "reference_moment": "2026-08-19T12:00:00+05:30",
            "include_timing": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["birth"]["place"] == BIRTH["place"]
    assert data["synthesis"]["event"] == "marriage_synthesis"
    assert data["synthesis"]["model_version"] == "v2"
    assert seen["include_timing"] is False
    assert seen["reference_moment"].utcoffset() is not None


def test_marriage_synthesis_endpoint_maps_value_error_to_400(monkeypatch):
    monkeypatch.setattr(main, "build_chart", lambda birth: {"birth": {}, "houses": {}, "planets": {}})

    def fail(*args, **kwargs):
        raise ValueError("reference_moment must include a timezone offset.")

    monkeypatch.setattr(main, "synthesize_marriage_profile_v2", fail)

    response = client.post(
        "/api/v1/marriage-synthesis-v2",
        json={
            "birth": BIRTH,
            "reference_moment": "2026-08-19T12:00:00",
            "include_timing": False,
        },
    )

    assert response.status_code == 400
    assert "timezone offset" in response.json()["detail"]
