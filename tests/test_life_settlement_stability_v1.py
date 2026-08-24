from datetime import datetime, timezone

import pytest

from app.astrology.features import life_settlement_stability_v1 as module

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _core(score=0.68, coverage=1.0, confidence=0.8):
    return {"available": True, "life_settlement_score": score, "coverage": coverage, "confidence": confidence, "components": {}}


def _timing(convergence=0.7):
    return {"available": True, "strongest_convergence_window": {"start": "2027-01-01T00:00:00+00:00", "end": "2028-01-01T00:00:00+00:00", "convergence_score": convergence}}


def _support(score=0.7):
    return {"available": True, "confidence": score, "scores": {"a": score, "b": score}}


def _patch_supporting(monkeypatch, score=0.7):
    for _name, _label, fn in module.SUPPORTING_DOMAINS:
        monkeypatch.setattr(module, fn.__name__, lambda chart, moment, s=score: _support(s))


def test_stability_scores_are_bounded(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _core())
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda c, m: _timing())
    _patch_supporting(monkeypatch)
    result = module.analyze_life_settlement_stability_v1({}, NOW)
    assert result["available"] is True
    for key in ("overall_stability_score", "core_settlement_score", "timing_convergence_score", "supporting_context_score", "confidence"):
        assert 0.0 <= result[key] <= 1.0


def test_supporting_domains_cannot_rescue_weak_core(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _core(score=0.30))
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda c, m: _timing(convergence=1.0))
    _patch_supporting(monkeypatch, score=1.0)
    result = module.analyze_life_settlement_stability_v1({}, NOW)
    assert result["outlook"] == "core_foundations_still_developing"
    assert result["overall_stability_score"] < 0.60


def test_core_domains_remain_definition_of_settlement(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _core())
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda c, m: _timing())
    _patch_supporting(monkeypatch)
    result = module.analyze_life_settlement_stability_v1({}, NOW)
    principle = result["design_principle"].lower()
    assert "career" in principle and "finance" in principle and "marriage" in principle
    assert "supporting stability context only" in principle
    assert "cannot substitute" in principle


def test_reality_override_preserves_confirmed_milestones(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _core())
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda c, m: _timing())
    _patch_supporting(monkeypatch)
    result = module.analyze_life_settlement_stability_v1({}, NOW)
    rule = result["historical_validation"]["rule"].lower()
    assert "real-world history override" in rule
    assert "must never mark an unconfirmed milestone as achieved" in rule
    assert "move an achieved milestone back to pending" in rule


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone offset"):
        module.analyze_life_settlement_stability_v1({}, datetime(2026, 8, 23))
