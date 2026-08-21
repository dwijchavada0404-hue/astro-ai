from datetime import datetime, timezone

from app.astrology.features import top_level_question_router_v1 as module


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _disable_all(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_marriage_question_v3", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_career_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_finance_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_property_home_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_family_children_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_location_settlement_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_education_learning_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_purpose_personal_growth_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_friends_social_community_question_v1", lambda q: {"available": False})


def test_settlement_intent_has_cross_domain_precedence(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: {"available": True, "primary_intent": "settlement_timing"})
    monkeypatch.setattr(module, "answer_life_settlement_question_v1", lambda c, q, m: {"available": True, "answer": "cross-domain answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "When will career, money and marriage all become stable?", NOW)
    assert result["domain"] == "life_settlement"
    assert result["route"] == "life_settlement_answer_v1"
    assert result["answer"] == "cross-domain answer"


def test_finance_question_preserves_finance_router(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_finance_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_finance_question_v1", lambda c, q, m: {"available": True, "event": "finance_wealth", "answer": "finance answer"})
    result = module.route_top_level_question_v1({}, "How will my finances progress?", NOW)
    assert result["domain"] == "finance"
    assert result["route"] == "top_level_to_finance"


def test_education_question_routes_to_education_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_education_learning_question_v1", lambda q: {"available": True, "primary_intent": "higher_study_transition"})
    monkeypatch.setattr(module, "route_education_learning_question_v1", lambda c, q, m: {"available": True, "event": "education_learning", "answer": "education answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "When is a strong period for higher studies?", NOW)
    assert result["domain"] == "education_learning"
    assert result["route"] == "top_level_to_education_learning"
    assert result["answer"] == "education answer"


def test_purpose_question_routes_to_purpose_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_purpose_personal_growth_question_v1", lambda q: {"available": True, "primary_intent": "purpose_overview"})
    monkeypatch.setattr(module, "route_purpose_personal_growth_question_v1", lambda c, q, m: {"available": True, "event": "purpose_personal_growth", "answer": "purpose answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "What themes relate to my life purpose and growth?", NOW)
    assert result["domain"] == "purpose_personal_growth"
    assert result["route"] == "top_level_to_purpose_personal_growth"
    assert result["answer"] == "purpose answer"


def test_social_question_routes_to_social_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_friends_social_community_question_v1", lambda q: {"available": True, "primary_intent": "social_overview"})
    monkeypatch.setattr(module, "route_friends_social_community_question_v1", lambda c, q, m: {"available": True, "event": "friends_social_community", "answer": "social answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "How do friendship and community themes look for me?", NOW)
    assert result["domain"] == "friends_social_community"
    assert result["route"] == "top_level_to_friends_social_community"
    assert result["answer"] == "social answer"


def test_existing_domain_precedence_beats_purpose_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_career_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_purpose_personal_growth_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_career_question_v1", lambda c, q, m: {"available": True, "event": "career", "answer": "career answer"})
    result = module.route_top_level_question_v1({}, "What career direction gives me meaningful contribution?", NOW)
    assert result["domain"] == "career"
    assert result["route"] == "top_level_to_career"


def test_existing_domain_precedence_beats_social_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_marriage_question_v3", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_friends_social_community_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_marriage_question_v3", lambda c, u, m: {"available": True, "event": "marriage", "answer": "marriage answer"})
    result = module.route_top_level_question_v1({}, "Will friendship be important in my marriage?", NOW)
    assert result["domain"] == "marriage"
    assert result["route"] == "top_level_to_marriage"


def test_unsupported_question_stays_unsupported(monkeypatch):
    _disable_all(monkeypatch)
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
