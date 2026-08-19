from datetime import datetime, timezone

from app.astrology.features.marriage_contextual_router_v1 import (
    _is_open_ended_marriage_timing,
    route_marriage_question_contextual_v1,
)
from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3


def _chart():
    return {
        "houses": {"7": {"sign": "Scorpio", "lord": "Mars"}},
        "planets": {"Mars": {"house": 12, "sign": "Aries"}},
        "dashas": {
            "mahadashas": [
                {
                    "planet": "Venus",
                    "start": "2018-01-01T00:00:00+00:00",
                    "end": "2038-01-01T00:00:00+00:00",
                    "antardashas": [
                        {
                            "planet": "Jupiter",
                            "start": "2018-01-01T00:00:00+00:00",
                            "end": "2038-01-01T00:00:00+00:00",
                        }
                    ],
                }
            ]
        },
    }


def _ref():
    return datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)


def test_open_ended_timing_detection():
    analysis = analyze_marriage_question_v3("When will I get married?")
    assert _is_open_ended_marriage_timing(analysis) is True


def test_explicit_year_does_not_use_bidirectional_default():
    analysis = analyze_marriage_question_v3("Will I get married in 2027?")
    assert _is_open_ended_marriage_timing(analysis) is False


def test_married_user_is_clarified_before_timing_scan():
    analysis = analyze_marriage_question_v3("When will I get married?")
    result = route_marriage_question_contextual_v1(
        _chart(), analysis, _ref(), relationship_status="married"
    )
    assert result["route"] == "context_guard"
    assert result["requires_clarification"] is True
    assert result["relationship_status"] == "married"


def test_single_user_open_ended_question_gets_bidirectional_enrichment():
    analysis = analyze_marriage_question_v3("When will I get married?")
    result = route_marriage_question_contextual_v1(
        _chart(), analysis, _ref(), relationship_status="single",
        lookback_years=2, lookahead_years=2,
    )
    assert result["route"] == "single_event"
    assert result["event"] == "marriage_timing"
    assert result["timing_mode"] == "bidirectional"
    assert result["forecast_type"] == "past_future_comparison"
    assert "past" in result
    assert "future" in result
    assert result["relationship_status"] == "single"


def test_divorced_open_ended_question_is_marked_for_remarriage_context():
    analysis = analyze_marriage_question_v3("When will I get married?")
    result = route_marriage_question_contextual_v1(
        _chart(), analysis, _ref(), relationship_status="divorced",
        lookback_years=2, lookahead_years=2,
    )
    assert result["route"] == "single_event"
    assert result["event"] == "marriage_timing"
    assert result["timing_mode"] == "bidirectional"
    assert result["context_interpretation"] == "remarriage_timing"
    assert "remarriage" in result["future"]["interpretation"]
