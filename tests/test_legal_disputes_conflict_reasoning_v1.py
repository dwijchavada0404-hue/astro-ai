from app.astrology.features.legal_disputes_conflict_reasoning_v1 import analyze_legal_disputes_conflict_v1


def _chart():
    return {
        "houses": {
            "6": {"lord": "Mercury"},
            "7": {"lord": "Venus"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Jupiter"},
        },
        "planets": {
            "Mars": {"house": 6},
            "Saturn": {"house": 8},
            "Mercury": {"house": 7},
            "Jupiter": {"house": 9},
            "Sun": {"house": 10},
            "Rahu": {"house": 6},
            "Ketu": {"house": 12},
            "Venus": {"house": 7},
        },
    }


def test_foundation_scores_are_bounded():
    result = analyze_legal_disputes_conflict_v1(_chart())
    assert result["available"] is True
    assert all(0.0 <= score <= 1.0 for score in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_foundation_is_multi_factor_not_one_planet_rule():
    result = analyze_legal_disputes_conflict_v1(_chart())
    assert len(result["evidence"]) >= 4
    assert set(result["theme_scores"]) == {
        "dispute_engagement",
        "negotiation_mediation",
        "complexity_endurance",
        "principles_fairness",
        "competition_assertiveness",
        "resolution_capacity",
    }


def test_known_legal_history_overrides_astrology():
    rule = analyze_legal_disputes_conflict_v1(_chart())["historical_validation"]["rule"].lower()
    assert "known legal history" in rule
    assert "override" in rule
    assert "must never be treated as proof" in rule


def test_legal_outcomes_and_criminal_predictions_are_disallowed():
    text = analyze_legal_disputes_conflict_v1(_chart())["limitation"].lower()
    for phrase in ("not legal advice", "guilt", "liability", "court verdicts", "arrest", "imprisonment", "criminal outcomes", "regulatory action", "settlement amounts"):
        assert phrase in text


def test_missing_required_houses_returns_unavailable():
    chart = _chart(); chart["houses"].pop("8")
    result = analyze_legal_disputes_conflict_v1(chart)
    assert result["available"] is False
    assert "8th" in result["reason"]
