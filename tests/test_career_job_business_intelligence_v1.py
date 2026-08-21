from app.astrology.features.career_job_business_intelligence_v1 import analyze_job_vs_business_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"},
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "5": {"lord": "Mercury"},
            "6": {"lord": "Saturn"},
            "7": {"lord": "Venus"},
            "8": {"lord": "Jupiter"},
            "9": {"lord": "Jupiter"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Mercury"},
            "12": {"lord": "Jupiter"},
        },
        "planets": {
            "Sun": {"house": 10},
            "Mercury": {"house": 11},
            "Mars": {"house": 3},
            "Jupiter": {"house": 9},
            "Venus": {"house": 7},
            "Saturn": {"house": 10},
            "Rahu": {"house": 11},
        },
    }


def test_job_business_engine_returns_bounded_comparison():
    result = analyze_job_vs_business_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "career_job_vs_business"
    assert result["orientation"] in {"structured_employment", "independent_business", "mixed_hybrid"}
    assert 0.0 <= result["job_score"] <= 1.0
    assert 0.0 <= result["business_score"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


def test_job_business_engine_uses_foundation_and_direction_evidence():
    result = analyze_job_vs_business_v1(_chart())
    rules = {item["rule"] for item in result["evidence"]}
    assert "foundation_service_support" in rules
    assert "foundation_enterprise_support" in rules
    assert any(rule.startswith("direction_") for rule in rules)


def test_job_business_output_is_non_prescriptive():
    result = analyze_job_vs_business_v1(_chart())
    limitation = result["limitation"].lower()
    assert "not career" in limitation
    assert "financial advice" in limitation
    assert "guaranteed" in limitation


def test_missing_house_data_returns_unavailable():
    result = analyze_job_vs_business_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_input_validation():
    try:
        analyze_job_vs_business_v1([])  # type: ignore[arg-type]
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
