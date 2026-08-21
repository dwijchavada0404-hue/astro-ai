from datetime import datetime, timezone

import pytest

from app.astrology.features import life_settlement_timing_v1 as module


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _domain(period, score_key, score):
    return {
        "available": True,
        "strongest_future_period": {
            "start": period[0],
            "end": period[1],
            score_key: score,
        },
    }


def _synthesis():
    return {
        "available": True,
        "historical_validation": {"reality_override": True},
        "components": {
            "career": _domain(("2027-01-01T00:00:00+00:00", "2028-01-01T00:00:00+00:00"), "career_support_score", 0.80),
            "finance": _domain(("2027-06-01T00:00:00+00:00", "2028-06-01T00:00:00+00:00"), "finance_support_score", 0.76),
            "marriage": {"available": False},
            "property_home": _domain(("2027-09-01T00:00:00+00:00", "2028-03-01T00:00:00+00:00"), "home_property_support_score", 0.72),
            "family_children": {"available": False},
        },
    }


def test_identifies_multi_domain_overlap(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: _synthesis())
    result = module.analyze_life_settlement_timing_v1({}, NOW)
    assert result["available"] is True
    assert result["strongest_convergence_window"] is not None
    assert result["strongest_convergence_window"]["domain_count"] == 3
    assert set(result["strongest_convergence_window"]["domains"]) == {"career", "finance", "property_home"}
    assert result["timing_outlook"] == "cross_domain_convergence_identified"


def test_minimum_domain_threshold_can_remove_overlap(monkeypatch):
    synthesis = _synthesis()
    synthesis["components"]["property_home"] = {"available": False}
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: synthesis)
    result = module.analyze_life_settlement_timing_v1({}, NOW, minimum_domains=3)
    assert result["available"] is True
    assert result["strongest_convergence_window"] is None
    assert result["timing_outlook"] == "domain_windows_present_without_material_overlap"


def test_insufficient_date_bounded_evidence(monkeypatch):
    synthesis = _synthesis()
    synthesis["components"] = {name: {"available": True} for name in module.DOMAIN_ORDER}
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: synthesis)
    result = module.analyze_life_settlement_timing_v1({}, NOW)
    assert result["available"] is False
    assert result["timing_outlook"] == "timing_evidence_insufficient"


def test_timezone_is_required():
    with pytest.raises(ValueError, match="timezone"):
        module.analyze_life_settlement_timing_v1({}, datetime(2026, 8, 21))


def test_parameter_bounds():
    with pytest.raises(ValueError):
        module.analyze_life_settlement_timing_v1({}, NOW, lookahead_years=11)
    with pytest.raises(ValueError):
        module.analyze_life_settlement_timing_v1({}, NOW, minimum_domains=1)


def test_non_guarantee_language(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: _synthesis())
    result = module.analyze_life_settlement_timing_v1({}, NOW)
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "not a guaranteed settlement date" in text
    assert "does not manufacture a precise settlement age/date" in text
