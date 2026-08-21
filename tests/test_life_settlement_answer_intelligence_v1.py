from datetime import datetime, timezone

from app.astrology.features import life_settlement_answer_intelligence_v1 as module


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)
CHART = {"birth": {"date": "2000-04-04"}}


def _synthesis():
    return {
        "available": True,
        "answer": "Cross-domain symbolic settlement is moderately supportive.",
        "historical_validation": {"reality_override": True},
    }


def _timing():
    window = {
        "start": "2028-04-01T00:00:00+00:00",
        "end": "2029-04-10T00:00:00+00:00",
        "domain_labels": ["Career & Profession", "Finance & Wealth", "Marriage & Partnership"],
        "domains": ["career", "finance", "marriage"],
        "domain_count": 3,
        "convergence_score": 0.81,
    }
    return {
        "available": True,
        "strongest_convergence_window": window,
        "ranked_convergence_windows": [window],
    }


def test_age_answer_is_derived_from_window(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: _synthesis())
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda chart, moment: _timing())
    result = module.answer_life_settlement_question_v1(CHART, "At what age will I settle in life?", NOW)
    assert result["available"] is True
    assert "age 27–29" in result["answer"]
    assert "not a guaranteed date" in result["answer"]


def test_target_age_inside_window(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: _synthesis())
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda chart, moment: _timing())
    result = module.answer_life_settlement_question_v1(CHART, "What will my life look like at 28?", NOW)
    assert "age 28" in result["answer"]
    assert "inside a symbolic cross-domain convergence window" in result["answer"]


def test_no_window_does_not_invent_age(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: _synthesis())
    monkeypatch.setattr(module, "analyze_life_settlement_timing_v1", lambda chart, moment: {"available": False, "ranked_convergence_windows": []})
    result = module.answer_life_settlement_question_v1(CHART, "What age will I be settled?", NOW)
    assert "do not provide enough overlapping" in result["answer"]
    assert "would not infer a settlement age or year" in result["answer"]


def test_overview_uses_cross_domain_synthesis(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_synthesis_v1", lambda chart, moment: _synthesis())
    result = module.answer_life_settlement_question_v1(CHART, "When will everything fall into place?", NOW)
    assert result["event"] == "life_settlement"
    assert result["reality_override"]["required"] is True


def test_unrelated_question_is_unsupported():
    result = module.answer_life_settlement_question_v1(CHART, "Tell me a joke", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"
