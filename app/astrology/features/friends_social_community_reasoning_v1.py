from __future__ import annotations

from typing import Any


SOCIAL_THEMES = {
    "close_friendship": "capacity for close, reciprocal friendship and trusted peer bonds",
    "social_breadth": "breadth of social circles, acquaintances and group participation",
    "community_belonging": "belonging, participation and contribution within communities or groups",
    "networking_collaboration": "forming useful peer connections and collaborative relationships",
    "communication_connection": "social connection through conversation, exchange and shared interests",
    "selective_boundaries": "discernment, selectivity and boundaries within friendships and networks",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _house(chart: dict[str, Any], number: int) -> dict[str, Any]:
    houses = _safe_dict(chart.get("houses"))
    return _safe_dict(houses.get(str(number)) or houses.get(number))


def _planet_house(chart: dict[str, Any], planet: str) -> int | None:
    placement = _safe_dict(_safe_dict(chart.get("planets")).get(planet))
    try:
        return int(placement.get("house"))
    except (TypeError, ValueError):
        return None


def _lord_house(chart: dict[str, Any], house_no: int) -> tuple[str | None, int | None]:
    lord = _house(chart, house_no).get("lord")
    if not isinstance(lord, str) or not lord:
        return None, None
    return lord, _planet_house(chart, lord)


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_friends_social_community_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Assess symbolic friendship, networking and community themes.

    The 11th house is the primary group/network axis, the 3rd supports peer communication,
    the 7th one-to-one reciprocity, the 5th shared interests and social enjoyment, and the
    9th broader communities/worldviews. No placement is treated as proof of a person's
    actual friend count, popularity, loyalty, betrayal, isolation or social status.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not _safe_dict(chart.get("houses")):
        return {
            "available": False,
            "event": "friends_social_community",
            "model_version": "v1",
            "reason": "House data required for Friends, Social Networks & Community reasoning is unavailable.",
        }

    scores = {key: 0.0 for key in SOCIAL_THEMES}
    evidence: list[dict[str, Any]] = []
    house_weights = {
        11: (("social_breadth", 0.34), ("community_belonging", 0.26), ("networking_collaboration", 0.24)),
        3: (("communication_connection", 0.30), ("networking_collaboration", 0.12)),
        7: (("close_friendship", 0.26), ("networking_collaboration", 0.12)),
        5: (("close_friendship", 0.16), ("community_belonging", 0.12)),
        9: (("community_belonging", 0.16), ("social_breadth", 0.10)),
    }
    supportive_houses = {1, 3, 5, 7, 9, 10, 11}
    for house_no, theme_weights in house_weights.items():
        lord, placed = _lord_house(chart, house_no)
        if not lord:
            continue
        for theme, weight in theme_weights:
            scores[theme] += weight * 0.62
            if placed in supportive_houses:
                scores[theme] += weight * 0.38
                evidence.append({"rule": "social_house_lord_support", "house": house_no, "lord": lord, "lord_house": placed, "theme": theme})
        if placed in {6, 8, 12} and house_no in {7, 11}:
            scores["selective_boundaries"] += 0.10
            evidence.append({"rule": "social_boundary_emphasis", "house": house_no, "lord": lord, "lord_house": placed})

    significators = {
        "Mercury": ("communication_connection", "networking_collaboration"),
        "Venus": ("close_friendship", "community_belonging"),
        "Jupiter": ("community_belonging", "social_breadth"),
        "Moon": ("close_friendship",),
        "Saturn": ("selective_boundaries",),
        "Rahu": ("social_breadth", "networking_collaboration"),
        "Sun": ("community_belonging",),
    }
    for planet, themes in significators.items():
        placed = _planet_house(chart, planet)
        if placed in {3, 5, 7, 9, 11}:
            for theme in themes:
                scores[theme] += 0.065
                evidence.append({"rule": "social_significator_support", "planet": planet, "house": placed, "theme": theme})

    eleventh_lord, eleventh_house = _lord_house(chart, 11)
    third_lord, third_house = _lord_house(chart, 3)
    seventh_lord, seventh_house = _lord_house(chart, 7)
    if eleventh_lord and third_lord and eleventh_house in {3, 7, 11} and third_house in {3, 7, 11}:
        scores["communication_connection"] += 0.10
        scores["networking_collaboration"] += 0.10
        evidence.append({"rule": "network_communication_link", "eleventh_lord": eleventh_lord, "third_lord": third_lord})
    if eleventh_lord and seventh_lord and eleventh_house in {7, 11} and seventh_house in {7, 11}:
        scores["close_friendship"] += 0.08
        scores["networking_collaboration"] += 0.08
        evidence.append({"rule": "network_reciprocity_link", "eleventh_lord": eleventh_lord, "seventh_lord": seventh_lord})

    scores = {key: _bounded(value) for key, value in scores.items()}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    dominant, dominant_score = ranked[0]
    secondary, secondary_score = ranked[1]
    confidence = round(min(0.94, 0.44 + 0.035 * len(evidence) + 0.10 * max(0.0, dominant_score - secondary_score)), 2)

    return {
        "available": True,
        "event": "friends_social_community",
        "model_version": "v1",
        "dominant_theme": dominant,
        "dominant_theme_label": SOCIAL_THEMES[dominant],
        "dominant_score": dominant_score,
        "secondary_theme": secondary,
        "secondary_theme_label": SOCIAL_THEMES[secondary],
        "secondary_score": secondary_score,
        "theme_scores": scores,
        "ranked_themes": [{"theme": theme, "label": SOCIAL_THEMES[theme], "score": score} for theme, score in ranked],
        "confidence": confidence,
        "evidence": evidence,
        "known_reality_rule": (
            "Known friendships, social history, community ties and interpersonal experiences override astrological inference. "
            "Astrology must not invent friends, enemies, betrayal, loyalty, popularity, isolation or specific social events."
        ),
        "summary": f"The strongest social theme is {SOCIAL_THEMES[dominant]}, followed by {SOCIAL_THEMES[secondary]}.",
        "limitation": (
            "This is symbolic social-pattern analysis. It does not determine whether specific people are trustworthy, predict betrayal or conflict, "
            "guarantee popularity, friendship, networking success, community acceptance or a particular number of friends."
        ),
    }
