from datetime import datetime, timezone

import pytest

from app.astrology.features.marriage_context_guard import guard_marriage_question
from app.astrology.features.marriage_retrospective_reasoning_v1 import analyze_past_marriage_periods_v1


def _analysis(event="marriage_timing", qtype="timing", question="when will i get married?"):
    return {
        "primary_event": event,
        "original_question": question,
        "normalised_question": question.lower(),
        "intent": {"question_type": qtype},
    }


def test_married_user_gets_clarification_for_future_marriage_question():
    result = guard_marriage_question(_analysis(), "married")
    assert result["action"] == "clarify"
    assert "existing marriage" in result["message"].lower()


def test_divorced_user_marriage_timing_reinterprets_to_remarriage():
    result = guard_marriage_question(_analysis(), "divorced")
    assert result["action"] == "reinterpret"
    assert result["interpretation"] == "remarriage_timing"


def test_engaged_user_timing_reinterprets_to_wedding_timing():
    result = guard_marriage_question(_analysis(), "engaged")
    assert result["action"] == "reinterpret"
    assert result["interpretation"] == "wedding_or_formalisation_timing"


def test_single_user_proceeds():
    result = guard_marriage_question(_analysis(), "single")
    assert result["action"] == "proceed"


def test_unknown_status_proceeds_without_chart_inference():
    result = guard_marriage_question(_analysis(), None)
    assert result["action"] == "proceed"
    assert result["relationship_status"] == "unknown"


def test_retrospective_rejects_more_than_ten_years():
    with pytest.raises(ValueError):
        analyze_past_marriage_periods_v1({}, datetime(2026, 8, 19, tzinfo=timezone.utc), lookback_years=11)


def test_retrospective_rejects_naive_reference_time():
    with pytest.raises(ValueError):
        analyze_past_marriage_periods_v1({}, datetime(2026, 8, 19), lookback_years=5)
