from datetime import datetime, timezone

from app.astrology.features import top_level_question_router_v1 as module


NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _disable_non_travel(monkeypatch):
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


def test_foreign_travel_routes_to_travel_domain(monkeypatch):
    _disable_non_travel(monkeypatch)
    monkeypatch.setattr(module, "analyze_travel_journeys_question_v1", lambda q: {"available": True, "primary_intent": "international_travel"})
    monkeypatch.setattr(module, "route_travel_journeys_question_v1", lambda c, q, m: {"available": True, "event": "travel_journeys", "answer": "travel answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "When can I travel abroad?", NOW)
    assert result["domain"] == "travel_journeys"
    assert result["route"] == "top_level_to_travel_journeys"
    assert result["answer"] == "travel answer"


def test_location_settlement_precedence_beats_travel_overlap(monkeypatch):
    _disable_non_travel(monkeypatch)
    monkeypatch.setattr(module, "analyze_location_settlement_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_travel_journeys_question_v1", lambda q: {"available": True, "primary_intent": "international_travel"})
    monkeypatch.setattr(module, "route_location_settlement_question_v1", lambda c, q, m: {"available": True, "event": "location_settlement", "answer": "settlement answer"})
    result = module.route_top_level_question_v1({}, "When will I permanently settle abroad?", NOW)
    assert result["domain"] == "location_settlement"


def test_restricted_visa_question_routes_to_travel_safety_boundary(monkeypatch):
    _disable_non_travel(monkeypatch)
    monkeypatch.setattr(module, "analyze_travel_journeys_question_v1", lambda q: {"available": True, "primary_intent": "unknown", "restricted_outcome_requested": True})
    monkeypatch.setattr(module, "route_travel_journeys_question_v1", lambda c, q, m: {"available": True, "event": "travel_journeys", "route": "travel_journeys_safety_boundary_v1", "answer": "restricted travel answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "Will my visa be approved?", NOW)
    assert result["domain"] == "travel_journeys"
    assert result["result"]["route"] == "travel_journeys_safety_boundary_v1"


def test_real_classifier_hands_permanent_settlement_away_from_travel():
    understanding = module.analyze_travel_journeys_question_v1("When will I permanently settle abroad?")
    assert understanding["available"] is False
    assert understanding["handoff_to_location_settlement"] is True


def test_real_classifier_keeps_foreign_travel_in_travel_domain():
    understanding = module.analyze_travel_journeys_question_v1("When is my strongest period for foreign travel?")
    assert understanding["available"] is True
    assert understanding["primary_intent"] == "international_travel"
    assert understanding["handoff_to_location_settlement"] is False
