from datetime import datetime, timezone

import pytest

from app.astrology.features import life_settlement_synthesis_v1 as module


NOW = datetime(2026, 8, 21, 10, 14, tzinfo=timezone.utc)


def _domain(score_key, score, confidence=0.8, **extra):
    return {"available": True, score_key: score, "confidence": confidence, **extra}


def _location(score=0.57, confidence=0.8):
    return {
        "available": True,
        "scores": {
            "rooted_home_base": 0.52,
            "long_distance_residence": score,
            "foreign_settlement": 0.48,
        },
        "confidence": confidence,
    }


def test_requires_timezone():
    with pytest.raises(ValueError, match="timezone"):
        module.analyze_life_settlement_synthesis_v1({}, datetime(2026, 8, 21, 10, 14))


def test_cross_domain_synthesis_aggregates_without_guarantees(monkeypatch):
    monkeypatch.setattr(module, "analyze_career_synthesis_v1", lambda *_: _domain("career_development_score", 0.80))
    monkeypatch.setattr(module, "analyze_finance_synthesis_v1", lambda *_: _domain("wealth_building_score", 0.70))
    monkeypatch.setattr(module, "synthesize_marriage_profile_v2", lambda *_: _domain("overall_score", 0.65))
    monkeypatch.setattr(module, "analyze_property_home_synthesis_v1", lambda *_: _domain("property_home_development_score", 0.60))
    monkeypatch.setattr(module, "analyze_family_children_synthesis_v1", lambda *_: _domain("family_development_score", 0.55))
    monkeypatch.setattr(module, "analyze_location_settlement_synthesis_v1", lambda *_: _location())

    result = module.analyze_life_settlement_synthesis_v1({}, NOW)

    assert result["available"] is True
    assert result["coverage"] == 1.0
    assert result["strongest_domains"][0] == "career"
    assert "location_settlement" in result["available_domains"]
    assert 0.0 <= result["life_settlement_score"] <= 1.0
    assert result["historical_validation"]["reality_override"] is True
    limitation = result["limitation"].lower()
    assert "does not guarantee" in limitation
    assert "pregnancy" in limitation
    assert "foreign settlement" in limitation
    assert "settled" in limitation


def test_component_failure_is_isolated(monkeypatch):
    monkeypatch.setattr(module, "analyze_career_synthesis_v1", lambda *_: _domain("career_development_score", 0.75))
    monkeypatch.setattr(module, "analyze_finance_synthesis_v1", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(module, "synthesize_marriage_profile_v2", lambda *_: _domain("overall_score", 0.60))
    monkeypatch.setattr(module, "analyze_property_home_synthesis_v1", lambda *_: _domain("property_home_development_score", 0.58))
    monkeypatch.setattr(module, "analyze_family_children_synthesis_v1", lambda *_: _domain("family_development_score", 0.62))
    monkeypatch.setattr(module, "analyze_location_settlement_synthesis_v1", lambda *_: _location())

    result = module.analyze_life_settlement_synthesis_v1({}, NOW)

    assert result["available"] is True
    assert "finance" not in result["available_domains"]
    assert result["coverage"] == pytest.approx(5 / 6, abs=0.001)
    assert result["collection_errors"][0]["domain"] == "finance"


def test_no_domains_available_returns_unavailable(monkeypatch):
    unavailable = lambda *_: {"available": False, "reason": "missing"}
    monkeypatch.setattr(module, "analyze_career_synthesis_v1", unavailable)
    monkeypatch.setattr(module, "analyze_finance_synthesis_v1", unavailable)
    monkeypatch.setattr(module, "synthesize_marriage_profile_v2", unavailable)
    monkeypatch.setattr(module, "analyze_property_home_synthesis_v1", unavailable)
    monkeypatch.setattr(module, "analyze_family_children_synthesis_v1", unavailable)
    monkeypatch.setattr(module, "analyze_location_settlement_synthesis_v1", unavailable)

    result = module.analyze_life_settlement_synthesis_v1({}, NOW)
    assert result["available"] is False
    assert result["event"] == "life_settlement_synthesis"
