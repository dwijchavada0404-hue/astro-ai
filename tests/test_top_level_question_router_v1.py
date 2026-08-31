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
    monkeypatch.setattr(module, "analyze_siblings_communication_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_parents_elders_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_travel_journeys_question_v1", lambda q: {"available": False})
    monkeypatch.setattr(module, "analyze_health_wellbeing_question_v1", lambda q: {"available": False})


def test_settlement_intent_has_cross_domain_precedence(monkeypatch):
    monkeypatch.setattr(module, "analyze_life_settlement_question_v1", lambda q: {"available": True, "primary_intent": "settlement_timing"})
    monkeypatch.setattr(module, "answer_life_settlement_question_v1", lambda c, q, m: {"available": True, "answer": "cross-domain answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "When will career, money and marriage all become stable?", NOW)
    assert result["domain"] == "life_settlement"
    assert result["route"] == "life_settlement_answer_v1"


def test_finance_question_preserves_finance_router(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_finance_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_finance_question_v1", lambda c, q, m: {"available": True, "event": "finance_wealth", "answer": "finance answer"})
    result = module.route_top_level_question_v1({}, "How will my finances progress?", NOW)
    assert result["domain"] == "finance"


def test_education_question_routes_to_education_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_education_learning_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_education_learning_question_v1", lambda c, q, m: {"available": True, "event": "education_learning", "answer": "education answer"})
    result = module.route_top_level_question_v1({}, "When is a strong period for higher studies?", NOW)
    assert result["domain"] == "education_learning"


def test_purpose_question_routes_to_purpose_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_purpose_personal_growth_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_purpose_personal_growth_question_v1", lambda c, q, m: {"available": True, "event": "purpose_personal_growth", "answer": "purpose answer"})
    result = module.route_top_level_question_v1({}, "What themes relate to my life purpose and growth?", NOW)
    assert result["domain"] == "purpose_personal_growth"


def test_social_question_routes_to_social_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_friends_social_community_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_friends_social_community_question_v1", lambda c, q, m: {"available": True, "event": "friends_social_community", "answer": "social answer"})
    result = module.route_top_level_question_v1({}, "How do friendship and community themes look for me?", NOW)
    assert result["domain"] == "friends_social_community"


def test_siblings_question_routes_to_siblings_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_siblings_communication_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_siblings_communication_question_v1", lambda c, q, m: {"available": True, "event": "siblings_communication", "answer": "siblings answer"})
    result = module.route_top_level_question_v1({}, "What are my sibling relationship themes?", NOW)
    assert result["domain"] == "siblings_communication"


def test_parents_elders_question_routes_to_parents_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_parents_elders_question_v1", lambda q: {"available": True, "primary_intent": "parents_elders_overview"})
    monkeypatch.setattr(module, "route_parents_elders_question_v1", lambda c, q, m: {"available": True, "event": "parents_elders", "answer": "parents answer", "limitation": "bounded"})
    result = module.route_top_level_question_v1({}, "What are my themes with parents and elders?", NOW)
    assert result["domain"] == "parents_elders"
    assert result["route"] == "top_level_to_parents_elders"
    assert result["answer"] == "parents answer"


def test_travel_question_routes_to_travel_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_travel_journeys_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_travel_journeys_question_v1", lambda c, q, m: {"available": True, "event": "travel_journeys", "answer": "travel answer"})
    result = module.route_top_level_question_v1({}, "When is foreign travel likely for me?", NOW)
    assert result["domain"] == "travel_journeys"


def test_health_question_routes_to_health_domain(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_health_wellbeing_question_v1", lambda q: {"available": True, "primary_intent": "health_wellbeing_overview"})
    monkeypatch.setattr(module, "route_health_wellbeing_question_v1", lambda c, q, m: {"available": True, "event": "health_wellbeing", "answer": "wellbeing answer", "limitation": "non-medical"})
    result = module.route_top_level_question_v1({}, "What are my health and wellbeing themes?", NOW)
    assert result["domain"] == "health_wellbeing"
    assert result["route"] == "top_level_to_health_wellbeing"
    assert result["answer"] == "wellbeing answer"


def test_health_safety_boundary_is_preserved(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_health_wellbeing_question_v1", lambda q: {"available": True, "prohibited_request_detected": True, "primary_intent": "unknown"})
    monkeypatch.setattr(module, "route_health_wellbeing_question_v1", lambda c, q, m: {"available": True, "event": "health_wellbeing", "route": "health_wellbeing_safety_boundary_v1", "answer": "medical prediction blocked", "limitation": "non-medical"})
    result = module.route_top_level_question_v1({}, "Will I get cancer next year?", NOW)
    assert result["domain"] == "health_wellbeing"
    assert result["result"]["route"] == "health_wellbeing_safety_boundary_v1"


def test_family_precedence_beats_parent_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_family_children_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_parents_elders_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_family_children_question_v1", lambda c, q, m: {"available": True, "event": "family_children", "answer": "family answer"})
    result = module.route_top_level_question_v1({}, "How will my family life with parents and children develop?", NOW)
    assert result["domain"] == "family_children"


def test_property_precedence_beats_parent_home_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_property_home_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_parents_elders_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_property_home_question_v1", lambda c, q, m: {"available": True, "event": "property_home", "answer": "property answer"})
    result = module.route_top_level_question_v1({}, "Will I buy a home for my parents?", NOW)
    assert result["domain"] == "property_home"


def test_marriage_precedence_beats_parent_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_marriage_question_v3", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_parents_elders_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_marriage_question_v3", lambda c, u, m: {"available": True, "event": "marriage", "answer": "marriage answer"})
    result = module.route_top_level_question_v1({}, "Will my parents influence my marriage?", NOW)
    assert result["domain"] == "marriage"


def test_career_precedence_beats_health_routine_overlap(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(module, "analyze_career_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "analyze_health_wellbeing_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(module, "route_career_question_v1", lambda c, q, m: {"available": True, "event": "career", "answer": "career answer"})
    result = module.route_top_level_question_v1({}, "Will my work routine improve with my career?", NOW)
    assert result["domain"] == "career"


def test_explicit_career_question_beats_generic_marriage_fallback(monkeypatch):
    _disable_all(monkeypatch)
    monkeypatch.setattr(
        module,
        "analyze_marriage_question_v3",
        lambda q: {"available": True, "primary_event": "general_marriage", "detected_events": []},
    )
    monkeypatch.setattr(module, "analyze_career_question_v1", lambda q: {"available": True})
    monkeypatch.setattr(
        module,
        "route_career_question_v1",
        lambda c, q, m: {"available": True, "event": "career", "answer": "career answer"},
    )

    result = module.route_top_level_question_v1({}, "What general career themes does this chart show?", NOW)

    assert result["domain"] == "career"
    assert result["answer"] == "career answer"


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
