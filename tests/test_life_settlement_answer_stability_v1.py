from datetime import datetime, timezone

from app.astrology.features import life_settlement_answer_intelligence_v1 as module

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _question(intent: str, timing: bool = False):
    return {"available": True, "primary_intent": intent, "requires_timing_engine": timing}


def _synthesis():
    return {"available": True, "answer": "core synthesis", "historical_validation": {"status": "unconfirmed"}}


def test_overview_uses_stability_layer(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: _question("settlement_overview"))
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _synthesis())
    monkeypatch.setattr(module, "analyze_life_settlement_stability_v1", lambda c, m: {"available": True, "answer": "enhanced stability", "historical_validation": {"status": "unconfirmed"}})
    result = module.answer_life_settlement_question_v1({}, "When will life feel settled?", NOW)
    assert result["answer"] == "enhanced stability"
    assert result["stability"]["available"] is True


def test_multi_domain_stability_explains_core_vs_supporting(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: _question("multi_domain_stability"))
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _synthesis())
    monkeypatch.setattr(module, "analyze_life_settlement_stability_v1", lambda c, m: {"available": True, "answer": "enhanced stability"})
    result = module.answer_life_settlement_question_v1({}, "When will everything become stable?", NOW)
    text = result["answer"].lower()
    assert "supporting domains" in text
    assert "core settlement domains define" in text


def test_timing_question_does_not_require_stability_collection(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: _question("settlement_timing", timing=True))
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _synthesis())
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda c, m: {"available": False, "strongest_convergence_window": None})
    monkeypatch.setattr(module, "analyze_life_settlement_stability_v1", lambda c, m: (_ for _ in ()).throw(AssertionError("stability should not run")))
    result = module.answer_life_settlement_question_v1({}, "When will I settle?", NOW)
    assert result["stability"] is None
    assert "not infer" in result["answer"].lower()


def test_supporting_domains_cannot_be_described_as_substitutes(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: _question("settlement_overview"))
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda c, m: _synthesis())
    monkeypatch.setattr(module, "analyze_life_settlement_stability_v1", lambda c, m: {"available": True, "answer": "context"})
    result = module.answer_life_settlement_question_v1({}, "How settled is my life?", NOW)
    assert "cannot substitute for weak core settlement evidence" in result["limitation"].lower()
