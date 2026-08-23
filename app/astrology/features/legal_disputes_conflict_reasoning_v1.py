from __future__ import annotations

from typing import Any


def _d(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _planet_house(planets: dict[str, Any], name: str) -> int | None:
    try:
        value = _d(planets.get(name)).get("house")
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _b(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def analyze_legal_disputes_conflict_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Evaluate symbolic dispute/conflict-management themes without legal-outcome prediction."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    houses = _d(chart.get("houses"))
    planets = _d(chart.get("planets"))
    required = {"6", "7", "8", "9"}
    if not required.issubset(houses):
        return {"available": False, "event": "legal_disputes_conflict", "model_version": "v1", "reason": "6th, 7th, 8th and 9th houses are required."}

    h6 = _d(houses.get("6")); h7 = _d(houses.get("7")); h8 = _d(houses.get("8")); h9 = _d(houses.get("9"))
    l6, l7, l8, l9 = map(lambda h: str(h.get("lord") or ""), (h6, h7, h8, h9))

    p = {name: _planet_house(planets, name) for name in ("Mars", "Saturn", "Mercury", "Jupiter", "Sun", "Rahu", "Ketu")}

    dispute = _b(.42 + .10*bool(l6) + .08*(p["Mars"] == 6) + .08*(p["Saturn"] == 6) + .06*(p["Rahu"] in {6, 8}))
    negotiation = _b(.38 + .10*bool(l7) + .10*(p["Mercury"] in {3, 7, 9}) + .08*(p["Jupiter"] in {7, 9}) + .06*(p["Venus"] in {7} if "Venus" in planets else False))
    complexity = _b(.36 + .10*bool(l8) + .10*(p["Saturn"] == 8) + .08*(p["Rahu"] == 8) + .06*(p["Ketu"] == 8))
    principles = _b(.38 + .10*bool(l9) + .12*(p["Jupiter"] == 9) + .08*(p["Sun"] == 9) + .06*(p["Mercury"] == 9))
    competition = _b(.40 + .12*(p["Mars"] in {3, 6}) + .10*(p["Saturn"] == 6) + .08*(p["Sun"] in {6, 10}))
    resolution = _b(.32 + .18*negotiation + .18*principles + .10*(p["Jupiter"] in {6, 7, 9}) + .08*(p["Mercury"] in {6, 7, 9}))

    themes = {
        "dispute_engagement": dispute,
        "negotiation_mediation": negotiation,
        "complexity_endurance": complexity,
        "principles_fairness": principles,
        "competition_assertiveness": competition,
        "resolution_capacity": resolution,
    }
    strongest = max(themes.items(), key=lambda item: item[1])
    summary = f"The strongest symbolic Legal, Disputes & Conflict theme is {strongest[0].replace('_', ' ')}."

    evidence = [
        {"factor": "sixth_house", "house": 6, "lord": l6, "interpretation": "6th-house themes are used for competition, disputes, obligations and conflict-handling context."},
        {"factor": "seventh_house", "house": 7, "lord": l7, "interpretation": "7th-house themes are used for counterparties, agreements and negotiation context."},
        {"factor": "eighth_house", "house": 8, "lord": l8, "interpretation": "8th-house themes are used for complexity, escalation and prolonged-process context."},
        {"factor": "ninth_house", "house": 9, "lord": l9, "interpretation": "9th-house themes are used for principles, law, ethics and adjudicative-framework symbolism."},
    ]

    return {
        "available": True,
        "event": "legal_disputes_conflict",
        "model_version": "v1",
        "theme_scores": themes,
        "strongest_theme": strongest[0],
        "strongest_theme_score": strongest[1],
        "summary": summary,
        "evidence": evidence,
        "confidence": _b(.52 + .08*sum(bool(x) for x in (l6, l7, l8, l9)) + .06*strongest[1]),
        "historical_validation": {"status": "unconfirmed", "reality_override": True, "rule": "Known legal history, disputes, agreements and outcomes override astrology. Symbolic signatures must never be treated as proof that litigation, guilt, liability, arrest or a particular judgment occurred."},
        "limitation": "This module is not legal advice and cannot predict guilt, liability, court verdicts, arrest, imprisonment, criminal outcomes, regulatory action, exact dispute outcomes or settlement amounts.",
    }
