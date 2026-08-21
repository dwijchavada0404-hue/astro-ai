from __future__ import annotations

from typing import Any

from app.astrology.features.family_children_reasoning_v1 import analyze_family_children_v1


DIRECTION_LABELS = {
    "family_stability": "stable and supportive family environment",
    "parenting_nurturing": "parenting, mentoring and nurturing responsibilities",
    "family_growth": "growth or expansion of family responsibilities and bonds",
    "intergenerational_support": "support through elders, relatives or intergenerational networks",
    "family_change": "change in family structure, responsibilities or domestic dynamics",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_family_children_direction_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Translate the Family & Children natal foundation into distinct directions.

    Parenting symbolism is intentionally broader than biological parenthood. A strong
    score can describe nurturing, mentoring or family responsibility and must never be
    converted into a fertility, pregnancy, childbirth or child-count prediction.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")

    foundation = analyze_family_children_v1(chart)
    if not foundation.get("available"):
        return {
            "available": False,
            "event": "family_children_direction",
            "model_version": "v1",
            "reason": "Family & Children natal foundation is unavailable.",
        }

    themes = _safe_dict(foundation.get("theme_scores"))
    stability = float(themes.get("family_stability") or 0.0)
    children = float(themes.get("children_parenthood") or 0.0)
    growth = float(themes.get("family_growth") or 0.0)
    support = float(themes.get("family_support") or 0.0)
    change = float(themes.get("family_change") or 0.0)

    scores = {
        "family_stability": _bounded(0.68 * stability + 0.18 * support + 0.08 * growth - 0.16 * change),
        "parenting_nurturing": _bounded(0.64 * children + 0.16 * growth + 0.12 * stability + 0.08 * support),
        "family_growth": _bounded(0.58 * growth + 0.20 * children + 0.14 * support + 0.08 * stability),
        "intergenerational_support": _bounded(0.62 * support + 0.20 * stability + 0.10 * growth + 0.08 * children),
        "family_change": _bounded(0.70 * change + 0.12 * growth + 0.10 * children - 0.16 * stability),
    }

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary, primary_score = ranked[0]
    secondary, secondary_score = ranked[1]
    margin = primary_score - secondary_score
    confidence = round(min(0.94, 0.48 + 0.28 * primary_score + 0.18 * max(0.0, margin)), 2)

    return {
        "available": True,
        "event": "family_children_direction",
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
        "evidence": [
            {"source": "family_children_foundation", "theme": key, "score": round(float(value), 3)}
            for key, value in themes.items()
        ],
        "reality_override": {
            "known_facts_override": True,
            "rule": (
                "Known family and children milestones override astrological inference. Parenting or family-growth symbolism "
                "must never be converted into a claim of conception, pregnancy, childbirth, adoption or biological parenthood."
            ),
        },
        "answer": (
            f"The strongest Family & Children direction is {DIRECTION_LABELS[primary]}, followed by "
            f"{DIRECTION_LABELS[secondary]}."
        ),
        "limitation": (
            "This direction analysis is symbolic only. It is not fertility or medical advice and does not predict or "
            "guarantee conception, pregnancy, childbirth, adoption, number or sex of children, or another family outcome."
        ),
    }
