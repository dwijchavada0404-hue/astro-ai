from app.astrology.features.career_direction_intelligence_v1 import (
    analyze_career_direction_v1 as analyze_canonical_career_direction_v1,
)
from app.astrology.features.career_direction_v1 import analyze_career_direction_v1


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


def test_compatibility_alias_matches_canonical_direction_engine():
    assert analyze_career_direction_v1(_chart()) == analyze_canonical_career_direction_v1(_chart())


def test_compatibility_alias_preserves_bounded_scores_and_environments():
    result = analyze_career_direction_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "career_direction"
    assert len(result["ranked_directions"]) == 9
    assert len(result["ranked_environments"]) == 4
    assert all(0.0 <= score <= 1.0 for score in result["direction_scores"].values())
    assert all(0.0 <= score <= 1.0 for score in result["environment_scores"].values())
