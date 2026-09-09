from datetime import datetime, timezone

import app.services.unified_question_service_v1 as service


def test_available_route_never_returns_null_narrative(monkeypatch):
    monkeypatch.setattr(
        service,
        "route_top_level_question_v1",
        lambda *args, **kwargs: {
            "available": True,
            "domain": "marriage",
            "route": "top_level_to_marriage",
            "result": {"available": True, "event": "love_vs_arranged"},
        },
    )
    answer = service.answer_unified_question_v1(
        {"chart": "fixture"},
        "Meri Love marriage hogi ya arranged marriage",
        datetime(2026, 9, 9, tzinfo=timezone.utc),
    )
    assert isinstance(answer["answer"], str)
    assert answer["answer"].strip()


def test_unavailable_inner_route_surfaces_reason_instead_of_null(monkeypatch):
    monkeypatch.setattr(
        service,
        "route_top_level_question_v1",
        lambda *args, **kwargs: {
            "available": False,
            "domain": "family_children",
            "route": "top_level_to_family_children",
            "answer": "No usable dasha periods are available for Family & Children timing analysis.",
            "result": {"available": False, "reason": "No usable dasha periods are available for Family & Children timing analysis."},
        },
    )
    answer = service.answer_unified_question_v1(
        {"chart": "fixture"},
        "Mera pehla bacha kab hoga",
        datetime(2026, 9, 9, tzinfo=timezone.utc),
    )
    assert answer["answer"] == "No usable dasha periods are available for Family & Children timing analysis."
