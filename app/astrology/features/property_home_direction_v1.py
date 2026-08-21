from __future__ import annotations

from typing import Any

from app.astrology.features.property_home_reasoning_v1 import analyze_property_home_v1


DIRECTION_LABELS = {
    "ownership_establishment": "property ownership or establishment of a durable home base",
    "residential_stability": "long-term residential stability and rootedness",
    "asset_building": "gradual accumulation of property or tangible home-linked assets",
    "relocation_mobility": "relocation, residence change or a more mobile home pattern",
    "domestic_comfort": "quality, comfort and emotional support of the living environment",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_property_home_direction_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Translate the Property & Home natal foundation into distinct life directions.

    This layer deliberately separates acquisition/ownership symbolism from residential
    stability, asset accumulation, mobility and domestic comfort. A strong 4th-house
    signature must therefore not be interpreted automatically as confirmed ownership.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    foundation = analyze_property_home_v1(chart)
    if not foundation.get("available"):
        return {
            "available": False,
            "event": "property_home_direction",
            "model_version": "v1",
            "reason": "Property & Home natal foundation is unavailable.",
        }

    themes = _safe_dict(foundation.get("theme_scores"))
    home_stability = float(themes.get("home_stability") or 0.0)
    property_acquisition = float(themes.get("property_acquisition") or 0.0)
    asset_accumulation = float(themes.get("asset_accumulation") or 0.0)
    home_comfort = float(themes.get("home_comfort") or 0.0)
    relocation_change = float(themes.get("relocation_change") or 0.0)

    scores = {
        "ownership_establishment": _bounded(
            0.52 * property_acquisition + 0.24 * asset_accumulation + 0.16 * home_stability + 0.08 * home_comfort
        ),
        "residential_stability": _bounded(
            0.58 * home_stability + 0.22 * home_comfort + 0.12 * asset_accumulation - 0.18 * relocation_change
        ),
        "asset_building": _bounded(
            0.55 * asset_accumulation + 0.27 * property_acquisition + 0.10 * home_stability + 0.08 * home_comfort
        ),
        "relocation_mobility": _bounded(
            0.66 * relocation_change + 0.14 * property_acquisition + 0.10 * home_comfort - 0.18 * home_stability
        ),
        "domestic_comfort": _bounded(
            0.64 * home_comfort + 0.22 * home_stability + 0.08 * property_acquisition + 0.06 * asset_accumulation
        ),
    }

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary, primary_score = ranked[0]
    secondary, secondary_score = ranked[1]
    margin = primary_score - secondary_score
    confidence = round(min(0.94, 0.48 + 0.28 * primary_score + 0.18 * max(0.0, margin)), 2)

    evidence = [
        {"source": "property_home_foundation", "theme": key, "score": round(float(value), 3)}
        for key, value in themes.items()
    ]

    return {
        "available": True,
        "event": "property_home_direction",
        "model_version": "v1",
        "primary_direction": primary,
        "primary_direction_label": DIRECTION_LABELS[primary],
        "primary_score": primary_score,
        "secondary_direction": secondary,
        "secondary_direction_label": DIRECTION_LABELS[secondary],
        "secondary_score": secondary_score,
        "direction_scores": scores,
        "ranked_directions": [
            {"direction": key, "label": DIRECTION_LABELS[key], "score": score}
            for key, score in ranked
        ],
        "confidence": confidence,
        "evidence": evidence,
        "reality_override": {
            "known_facts_override": True,
            "rule": (
                "Known ownership, residence, purchase, sale, inheritance and relocation facts override astrological "
                "inference. Strong ownership symbolism describes a tendency only and must never be converted into a "
                "claim that the user owns or will definitely acquire property."
            ),
        },
        "answer": (
            f"The strongest Property & Home direction is {DIRECTION_LABELS[primary]}, followed by "
            f"{DIRECTION_LABELS[secondary]}."
        ),
        "limitation": (
            "This direction analysis does not predict or guarantee a property purchase, ownership, sale, inheritance, "
            "financing approval, investment return, relocation or residential stability."
        ),
    }
