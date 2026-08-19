from datetime import datetime, timezone

import app.astrology.features.marriage_bidirectional_timing_reasoning_v1 as module


def _window(score: float, label: str):
    return {
        "primary_window": {
            "start": f"{label}-01T00:00:00+00:00",
            "end": f"{label}-28T00:00:00+00:00",
            "peak": {"score": score, "moment": f"{label}-15T00:00:00+00:00"},
        }
    }


def test_bidirectional_returns_past_and_future(monkeypatch):
    calls = []

    def fake_scan(chart, start, end, step_days=14):
        calls.append((start, end))
        if end < datetime(2026, 8, 19, tzinfo=timezone.utc):
            return {"events": {"marriage_timing": _window(0.78, "2023-08")}}
        return {"events": {"marriage_timing": _window(0.86, "2026-11")}}

    monkeypatch.setattr(module, "scan_marriage_forecast_v2", fake_scan)
    result = module.analyze_marriage_timing_bidirectional_v1(
        {}, datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
    )
    assert result["available"] is True
    assert result["past"]["strongest_score"] == 0.78
    assert result["future"]["strongest_score"] == 0.86
    assert result["comparison"]["result"] in {"future_stronger", "similar_strength"}
    assert len(calls) == 2


def test_married_user_future_wording_is_not_second_marriage(monkeypatch):
    def fake_scan(chart, start, end, step_days=14):
        return {"events": {"marriage_timing": _window(0.8, "2026-11")}}

    monkeypatch.setattr(module, "scan_marriage_forecast_v2", fake_scan)
    result = module.analyze_marriage_timing_bidirectional_v1(
        {},
        datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        relationship_status="married",
    )
    assert "relationship / commitment" in result["future"]["interpretation"]
    assert "remarriage" not in result["future"]["interpretation"]


def test_divorced_user_future_wording_supports_remarriage(monkeypatch):
    def fake_scan(chart, start, end, step_days=14):
        return {"events": {"marriage_timing": _window(0.8, "2027-02")}}

    monkeypatch.setattr(module, "scan_marriage_forecast_v2", fake_scan)
    result = module.analyze_marriage_timing_bidirectional_v1(
        {},
        datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        relationship_status="divorced",
    )
    assert "remarriage" in result["future"]["interpretation"]


def test_historical_window_is_not_presented_as_proof(monkeypatch):
    def fake_scan(chart, start, end, step_days=14):
        return {"events": {"marriage_timing": _window(0.91, "2023-08")}}

    monkeypatch.setattr(module, "scan_marriage_forecast_v2", fake_scan)
    result = module.analyze_marriage_timing_bidirectional_v1(
        {}, datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
    )
    assert "not guarantees" in result["limitation"].lower()
    assert "proof" in result["limitation"].lower()


def test_rejects_naive_reference_time():
    try:
        module.analyze_marriage_timing_bidirectional_v1({}, datetime(2026, 8, 19, 12, 0))
    except ValueError as exc:
        assert "timezone" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for naive datetime")
