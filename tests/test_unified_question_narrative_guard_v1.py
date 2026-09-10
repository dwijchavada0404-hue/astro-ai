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


def test_unavailable_inner_route_hides_internal_reason_copy(monkeypatch):
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
    assert "No usable dasha" not in answer["answer"]
    assert "clear timing indication" in answer["answer"]
    assert "calculation" not in answer["answer"].lower()
    assert "recalculated" not in answer["answer"].lower()


def test_available_route_hides_internal_methodology_copy(monkeypatch):
    monkeypatch.setattr(service, "route_top_level_question_v1", lambda *args, **kwargs: {
        "available": True, "domain": "career", "route": "career_event",
        "answer": "Career event themes are ranked from natal evidence and available dasha timing. Scores represent symbolic activation strength.",
        "result": {"available": True},
    })
    answer = service.answer_unified_question_v1({"chart": "fixture"}, "Meri job change kab hogi", datetime(2026, 9, 9, tzinfo=timezone.utc))
    assert "ranked from natal" not in answer["answer"].lower()
    assert "symbolic activation" not in answer["answer"].lower()


def test_available_route_hides_remaining_engine_copy(monkeypatch):
    monkeypatch.setattr(service, "route_top_level_question_v1", lambda *args, **kwargs: {
        "available": True, "domain": "education_learning", "route": "education_timing",
        "answer": "Education timing compares symbolic study, skill-development and research activation across dasha periods.",
        "result": {"available": True},
    })
    answer = service.answer_unified_question_v1({"chart": "fixture"}, "When should I study?", datetime(2026, 9, 9, tzinfo=timezone.utc))
    assert "timing compares symbolic" not in answer["answer"].lower()
    assert "guesswork" in answer["answer"].lower()
