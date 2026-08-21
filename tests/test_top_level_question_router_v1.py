from datetime import datetime, timezone

from app.astrology.features import top_level_question_router_v1 as module


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_settlement_intent_has_cross_domain_precedence(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: {"available": True, "primary_intent": "settlement_timing"})
    monkeypatch.setattr(module, "answer_life_settlement_question_v1", lambda c, q, m: {"available": True, "answer": "cross-domain answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "When will career, money and marriage all become stable?", NOW)
    assert result["domain"] == "life_settlement"
    assert result["route"] == "life_settlement_answer_v1"
    assert result["answer"] == "cross-domain answer"


def test_finance_question_preserves_finance_router(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_marriage_question_v3", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_career_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_finance_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_property_home_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_family_children_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_location_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_education_learning_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "route_finance_question_v1", lambda c, q, m: {"available": True, "event": "finance_wealth", "answer": "finance answer"})
    result = module.route_top_level_question_v1({}, "How will my finances progress?", NOW)
    assert result["domain"] == "finance"
    assert result["route"] == "top_level_to_finance"


def test_education_question_routes_to_education_domain(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_marriage_question_v3", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_career_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_finance_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_property_home_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_family_children_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_location_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_education_learning_question_v1", lambda q: {"available": True, "primary_intent": "higher_study_transition"})
    monkeypatch.setattr(module, "route_education_learning_question_v1", lambda c, q, m: {"available": True, "event": "education_learning", "answer": "education answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "When is a strong period for higher studies?", NOW)
    assert result["domain"] == "education_learning"
    assert result["route"] == "top_level_to_education_learning"
    assert result["answer"] == "education answer"


def test_unsupported_question_stays_unsupported(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_marriage_question_v3", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_career_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_finance_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_property_home_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_family_children_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_location_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_education_learning_question_v1", lambda q: {"available": False})
    result = module.route_top_level_question_v1({}, "What colour should I paint my desk?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"


def test_timezone_required():
    try:
        module.route_top_level_question_v1({}, "When will I settle?", datetime(2026, 8, 21))
    except ValueError as exc:
        assert "timezone" in str(exc).lower()
    else:
        raise AssertionError("Expected timezone validation error")
