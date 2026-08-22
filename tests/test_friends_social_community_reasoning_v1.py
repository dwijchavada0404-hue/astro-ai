from app.astrology.features.friends_social_community_reasoning_v1 import analyze_friends_social_community_v1


def _chart():
    return {
        "houses": {
            "3": {"lord": "Mercury"}, "5": {"lord": "Venus"}, "7": {"lord": "Moon"},
            "9": {"lord": "Jupiter"}, "11": {"lord": "Saturn"},
        },
        "planets": {
            "Mercury": {"house": 11}, "Venus": {"house": 5}, "Moon": {"house": 7},
            "Jupiter": {"house": 9}, "Saturn": {"house": 11}, "Rahu": {"house": 3}, "Sun": {"house": 11},
        },
    }


def test_social_scores_are_bounded_and_ranked():
    result = analyze_friends_social_community_v1(_chart())
    assert result["available"] is True
    assert result["dominant_theme"] in result["theme_scores"]
    assert len(result["ranked_themes"]) == 6
    assert all(0.0 <= score <= 1.0 for score in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_friendship_and_networking_are_separate_themes():
    result = analyze_friends_social_community_v1(_chart())
    assert "close_friendship" in result["theme_scores"]
    assert "networking_collaboration" in result["theme_scores"]
    assert "social_breadth" in result["theme_scores"]


def test_reality_overrides_social_inference():
    result = analyze_friends_social_community_v1(_chart())
    rule = result["known_reality_rule"].lower()
    assert "known friendships" in rule
    assert "override" in rule
    assert "must not invent" in rule


def test_specific_people_and_betrayal_predictions_are_disallowed():
    text = analyze_friends_social_community_v1(_chart())["limitation"].lower()
    assert "specific people" in text
    assert "trustworthy" in text
    assert "betrayal" in text
    assert "number of friends" in text


def test_missing_house_data_is_unavailable():
    result = analyze_friends_social_community_v1({})
    assert result["available"] is False
    assert result["event"] == "friends_social_community"
