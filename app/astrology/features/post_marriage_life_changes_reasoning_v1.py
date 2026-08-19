from __future__ import annotations

from typing import Any


PROFILE_LABELS = {
    "relocation": "relocation / geographic change",
    "career_shift": "career or work-pattern change",
    "financial_change": "financial or resource change",
    "lifestyle_change": "lifestyle / domestic adjustment",
    "family_responsibility": "family-responsibility expansion",
    "international_exposure": "international / cross-border exposure",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def analyze_post_marriage_life_changes_v1(chart: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    houses = _safe_dict(chart.get("houses"))
    planets = _safe_dict(chart.get("planets"))

    seventh = _safe_dict(houses.get("7"))
    fourth = _safe_dict(houses.get("4"))
    tenth = _safe_dict(houses.get("10"))
    eleventh = _safe_dict(houses.get("11"))
    twelfth = _safe_dict(houses.get("12"))
    eighth = _safe_dict(houses.get("8"))

    seventh_lord = str(seventh.get("lord", "") or "")
    fourth_lord = str(fourth.get("lord", "") or "")
    tenth_lord = str(tenth.get("lord", "") or "")
    eleventh_lord = str(eleventh.get("lord", "") or "")
    twelfth_lord = str(twelfth.get("lord", "") or "")
    eighth_lord = str(eighth.get("lord", "") or "")

    if not seventh_lord or seventh_lord not in planets:
        return {
            "available": False,
            "event": "post_marriage_life_changes",
            "model_version": "v1",
            "reason": "The chart does not contain enough 7th-house information for post-marriage life-change reasoning.",
        }

    scores = {name: 0.0 for name in PROFILE_LABELS}
    evidence: list[dict[str, Any]] = []

    def add(profile: str, weight: float, rule: str, detail: Any) -> None:
        scores[profile] += weight
        evidence.append({"profile": profile, "weight": weight, "rule": rule, "detail": detail})

    seventh_lord_house = _safe_int(_safe_dict(planets.get(seventh_lord)).get("house"))

    if seventh_lord_house in (4, 12):
        add("relocation", 1.0, "seventh_lord_home_or_away_axis", seventh_lord_house)
    if seventh_lord_house in (9, 12):
        add("international_exposure", 1.0, "seventh_lord_long_distance_axis", seventh_lord_house)
    if seventh_lord_house in (10, 6):
        add("career_shift", 1.0, "seventh_lord_work_axis", seventh_lord_house)
    if seventh_lord_house in (2, 8, 11):
        add("financial_change", 1.0, "seventh_lord_resource_axis", seventh_lord_house)
    if seventh_lord_house in (4, 2):
        add("lifestyle_change", 0.9, "seventh_lord_domestic_axis", seventh_lord_house)
    if seventh_lord_house in (2, 4, 8):
        add("family_responsibility", 0.8, "seventh_lord_family_axis", seventh_lord_house)

    for lord_name, profile, rule, relevant_houses in (
        (fourth_lord, "relocation", "fourth_lord_mobility", (7, 9, 12)),
        (fourth_lord, "lifestyle_change", "fourth_lord_marriage_link", (7, 8, 12)),
        (tenth_lord, "career_shift", "tenth_lord_marriage_link", (7, 8, 9, 12)),
        (eleventh_lord, "financial_change", "eleventh_lord_marriage_link", (7, 8)),
        (twelfth_lord, "international_exposure", "twelfth_lord_marriage_link", (7, 9)),
        (eighth_lord, "financial_change", "eighth_lord_shared_resources", (2, 7, 11)),
        (eighth_lord, "family_responsibility", "eighth_lord_adjustment_axis", (4, 7)),
    ):
        if lord_name and lord_name in planets:
            house = _safe_int(_safe_dict(planets.get(lord_name)).get("house"))
            if house in relevant_houses:
                add(profile, 0.8, rule, {"lord": lord_name, "house": house})

    for planet_name, profile_map in {
        "Rahu": (("relocation", 0.7), ("international_exposure", 1.0), ("lifestyle_change", 0.5)),
        "Saturn": (("family_responsibility", 0.8), ("career_shift", 0.5)),
        "Jupiter": (("financial_change", 0.6), ("family_responsibility", 0.5)),
        "Venus": (("lifestyle_change", 0.8), ("financial_change", 0.4)),
        "Mercury": (("career_shift", 0.5), ("relocation", 0.3)),
    }.items():
        pdata = _safe_dict(planets.get(planet_name))
        house = _safe_int(pdata.get("house"))
        if house in (7, 8, 9, 10, 11, 12):
            for profile, weight in profile_map:
                add(profile, weight, "planet_in_post_marriage_axis", {"planet": planet_name, "house": house})

    max_raw = max(scores.values(), default=0.0)
    normaliser = max(1.0, max_raw)
    profile_scores = {key: round(min(value / normaliser, 1.0), 3) for key, value in scores.items()}
    ranked = sorted(profile_scores.items(), key=lambda item: item[1], reverse=True)
    dominant_profile = ranked[0][0] if ranked else "lifestyle_change"

    strongest = [
        {"profile": name, "label": PROFILE_LABELS[name], "relative_strength": score}
        for name, score in ranked[:3]
    ]

    confidence = round(min(0.88, 0.55 + min(len(evidence), 8) * 0.035), 3)

    return {
        "available": True,
        "event": "post_marriage_life_changes",
        "model_version": "v1",
        "dominant_profile": dominant_profile,
        "dominant_profile_label": PROFILE_LABELS[dominant_profile],
        "confidence": confidence,
        "summary": (
            f"The strongest symbolic post-marriage theme is {PROFILE_LABELS[dominant_profile]}. "
            "This is a tendency profile rather than a guaranteed real-world event."
        ),
        "profile": {"profile_scores": profile_scores},
        "ranked_profiles": strongest,
        "evidence": evidence,
        "limitation": (
            "This one-chart model can describe symbolic life-change tendencies associated with marriage, but it cannot guarantee relocation, a career move, income change, migration, or any specific event or timeline."
        ),
    }
