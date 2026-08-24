from datetime import datetime, timezone

from app.astrology.features import top_level_question_router_v1 as module


NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


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
    monkeypatch.setattr(module, "analyze_siblings_communication_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_parents_elders_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_travel_journeys_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_health_wellbeing_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_legal_disputes_conflict_question_v1", lambda q: {"available": False})


def test_legal_question_routes_to_legal_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_legal_disputes_conflict_question_v1", lambda q: {"available": True, "primary_intent": "negotiation_mediation"})
    monkeypatch.setattr(module, "route_legal_disputes_conflict_question_v1", lambda c, q, m: {"available": True, "event": "legal_disputes_conflict", "answer": "legal themes", "limitation": "not legal advice"})
    result = module.route_top_level_question_v1({}, "What are my negotiation and dispute-resolution themes?", NOW)
    assert result["domain"] == "legal_disputes_conflict"
    assert result["route"] == "top_level_to_legal_disputes_conflict"
    assert result["answer"] == "legal themes"


def test_legal_safety_boundary_is_preserved(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_legal_disputes_conflict_question_v1", lambda q: {"available": True, "primary_intent": "unknown", "prohibited_request_detected": True})
    monkeypatch.setattr(module, "route_legal_disputes_conflict_question_v1", lambda c, q, m: {"available": True, "event": "legal_disputes_conflict", "route": "legal_disputes_conflict_safety_boundary_v1", "answer": "verdict prediction blocked", "limitation": "not legal advice"})
    result = module.route_top_level_question_v1({}, "Will I definitely win my court case?", NOW)
    assert result["domain"] == "legal_disputes_conflict"
    assert result["result"]["route"] == "legal_disputes_conflict_safety_boundary_v1"


def test_marriage_precedence_beats_generic_conflict_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_marriage_question_v3", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_legal_disputes_conflict_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_marriage_question_v3", lambda c, u, m: {"available": True, "event": "marriage", "answer": "marriage answer"})
    result = module.route_top_level_question_v1({}, "How will conflict affect my marriage?", NOW)
    assert result["domain"] == "marriage"


def test_property_precedence_beats_dispute_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_property_home_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_legal_disputes_conflict_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_property_home_question_v1", lambda c, q, m: {"available": True, "event": "property_home", "answer": "property answer"})
    result = module.route_top_level_question_v1({}, "What are my property dispute and home ownership themes?", NOW)
    assert result["domain"] == "property_home"
