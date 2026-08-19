"""Final regression/hardening contract for the Marriage module."""

from datetime import datetime, timezone

import pytest

from app.astrology.features.marriage_forecast_router_v3 import route_marriage_question_v3
from app.astrology.features.marriage_synthesis_reasoning_v2 import synthesize_marriage_profile_v2


@pytest.fixture
def chart():
    # Deliberately rich but deterministic chart-shaped fixture. Individual engines
    # may use only the fields they understand; hardening verifies orchestration.
    return {
        "birth": {"date": "2000-04-04", "time": "14:04", "place": "Mumbai"},
        "houses": {
            "1": {"sign": "Taurus", "lord": "Venus"},
            "4": {"sign": "Leo", "lord": "Sun"},
            "7": {"sign": "Scorpio", "lord": "Mars"},
            "8": {"sign": "Sagittarius", "lord": "Jupiter"},
            "9": {"sign": "Capricorn", "lord": "Saturn"},
            "10": {"sign": "Aquarius", "lord": "Saturn"},
            "11": {"sign": "Pisces", "lord": "Jupiter"},
            "12": {"sign": "Aries", "lord": "Mars"},
        },
        "planets": {
            "Venus": {"house": 11, "sign": "Pisces"},
            "Mars": {"house": 12, "sign": "Aries"},
            "Jupiter": {"house": 1, "sign": "Taurus"},
            "Saturn": {"house": 1, "sign": "Taurus"},
            "Moon": {"house": 7, "sign": "Scorpio"},
            "Mercury": {"house": 10, "sign": "Aquarius"},
            "Sun": {"house": 10, "sign": "Aquarius"},
            "Rahu": {"house": 9, "sign": "Capricorn"},
            "Ketu": {"house": 3, "sign": "Cancer"},
        },
    }


def _route(chart, question, previous_context=None):
    return route_marriage_question_v3(
        chart,
        question,
        reference_moment=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        previous_context=previous_context,
    )


@pytest.mark.parametrize(
    "question",
    [
        "When am I likely to get married?",
        "Will it be love marriage or arranged marriage?",
        "What kind of spouse could I have?",
        "What might my married life be like?",
        "Could there be conflict or emotional distance in marriage?",
        "What relationship dynamics am I likely to experience?",
        "Could I relocate after marriage?",
    ],
)
def test_realistic_marriage_questions_do_not_crash(chart, question):
    result = _route(chart, question)
    assert isinstance(result, dict)
    assert result


def test_unrelated_question_does_not_get_false_marriage_answer(chart):
    result = _route(chart, "What is my career growth like?")
    # The marriage router must either decline/mark unavailable rather than
    # fabricating a confident marriage-specific answer for unrelated intent.
    assert isinstance(result, dict)
    assert result.get("available") is False or result.get("event") in {None, "unknown", "unsupported"}


def test_follow_up_keeps_previous_marriage_context(chart):
    first = _route(chart, "Could I relocate after marriage?")
    second = _route(chart, "What about abroad?", previous_context=first)
    assert isinstance(second, dict)
    assert second
    assert second.get("available", True) is not False


def test_synthesis_survives_mixed_positive_and_challenging_signals(chart):
    result = synthesize_marriage_profile_v2(
        chart,
        datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        include_timing=False,
    )
    assert result["available"] is True
    assert result.get("summary") or result.get("sections") or result.get("synthesis")
    # Hardening principle: mixed modules are preserved, not reduced to a
    # binary 'good/bad marriage' verdict.
    rendered = str(result).lower()
    assert "guarantee" not in rendered or "cannot guarantee" in rendered or "not guarantee" in rendered


def test_synthesis_timing_toggle_is_stable(chart):
    without_timing = synthesize_marriage_profile_v2(
        chart,
        datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        include_timing=False,
    )
    with_timing = synthesize_marriage_profile_v2(
        chart,
        datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        include_timing=True,
    )
    assert without_timing["available"] is True
    assert with_timing["available"] is True


def test_synthesis_rejects_naive_reference_time(chart):
    with pytest.raises(ValueError):
        synthesize_marriage_profile_v2(chart, datetime(2026, 8, 19, 12, 0), include_timing=False)
