from datetime import datetime, timezone

from app.astrology.features import life_settlement_synthesis_v1 as life_synthesis
from app.astrology.features import life_settlement_timing_v1 as life_timing
from app.astrology.features import top_level_question_router_v1 as top_router


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_top_level_routes_location_question(monkeypatch):
    unavailable = lambda q: {"available": False}
    monkeypatch.setattr(top_router, "analyze_life_settlement_question_v1", unavailable)
    monkeypatch.setattr(top_router, "analyze_marriage_question_v3", unavailable)
    monkeypatch.setattr(top_router, "analyze_career_question_v1", unavailable)
    monkeypatch.setattr(top_router, "analyze_finance_question_v1", unavailable)
    monkeypatch.setattr(top_router, "analyze_property_home_question_v1", unavailable)
    monkeypatch.setattr(top_router, "analyze_family_children_question_v1", unavailable)
    monkeypatch.setattr(top_router, "analyze_location_settlement_question_v1", lambda q: {"available": True, "primary_intent": "foreign_settlement"})
    monkeypatch.setattr(top_router, "route_location_settlement_question_v1", lambda chart, q, moment: {"available": True, "event": "location_settlement", "answer": "location answer"})

    result = top_router.route_top_level_question_v1({}, "Will I settle abroad?", NOW)
    assert result["domain"] == "location_settlement"
    assert result["route"] == "top_level_to_location_settlement"


def test_life_synthesis_domain_order_includes_location():
    assert "location_settlement" in life_synthesis.DOMAIN_ORDER
    assert life_synthesis.DOMAIN_LABELS["location_settlement"] == "Location & Foreign Settlement"


def test_location_future_period_can_enter_convergence():
    component = {
        "available": True,
        "strongest_future_period": {
            "start": "2027-01-01T00:00:00+00:00",
            "end": "2028-01-01T00:00:00+00:00",
            "foreign_settlement_support_score": 0.74,
            "foreign_exposure_score": 0.82,
        },
    }
    candidates = life_timing._domain_future_candidates("location_settlement", component, NOW)
    assert len(candidates) == 1
    assert candidates[0]["domain"] == "location_settlement"
    assert candidates[0]["score"] == 0.74


def test_location_reality_context_is_separate_from_property(monkeypatch):
    routed = {"domain": "location_settlement", "answer": "symbolic location answer"}
    context = {"milestones": {"location_settlement": {"state": "user_confirmed_achieved"}}}
    from app.astrology.features.life_context_v1 import reconcile_answer_with_life_context_v1
    result = reconcile_answer_with_life_context_v1(routed, context)
    assert result["reality_reconciliation"]["applied"] is True
    assert "location_settlement" in result["reality_reconciliation"]["status"]["confirmed_achieved"]
