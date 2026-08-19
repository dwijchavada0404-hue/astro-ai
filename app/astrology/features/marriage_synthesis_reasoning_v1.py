from __future__ import annotations

from typing import Any


SECTION_MAP = {
    "marriage_timing": "timing",
    "spouse_meeting": "timing",
    "love_marriage": "relationship_path",
    "arranged_marriage": "relationship_path",
    "love_vs_arranged": "relationship_path",
    "spouse_traits": "spouse_profile",
    "spouse_appearance": "spouse_profile",
    "spouse_profession": "spouse_profile",
    "spouse_education": "spouse_profile",
    "spouse_wealth": "spouse_profile",
    "spouse_family_background": "spouse_profile",
    "spouse_age_profile": "spouse_profile",
    "married_life_quality": "married_life",
    "relationship_challenges": "married_life",
    "marriage_compatibility_dynamics": "married_life",
    "post_marriage_life_changes": "post_marriage",
    "foreign_intercultural_connection": "relationship_path",
}

SECTION_LABELS = {
    "timing": "Timing & Meeting",
    "relationship_path": "Relationship Path",
    "spouse_profile": "Spouse Profile",
    "married_life": "Married Life",
    "post_marriage": "Post-Marriage Changes",
    "other": "Other Marriage Themes",
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _component_confidence(component: dict[str, Any]) -> float:
    for key in ("confidence", "parser_confidence", "support_score"):
        value = component.get(key)
        if value is not None:
            return max(0.0, min(1.0, _safe_float(value)))
    return 0.5


def _component_text(component: dict[str, Any]) -> str:
    for key in ("answer", "summary", "reason"):
        value = component.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalise_components(components: dict[str, Any]) -> list[dict[str, Any]]:
    normalised: list[dict[str, Any]] = []
    for fallback_event, raw in components.items():
        component = _safe_dict(raw)
        if not component or component.get("available") is False:
            continue
        event = str(component.get("event") or fallback_event)
        text = _component_text(component)
        if not text:
            continue
        normalised.append(
            {
                "event": event,
                "event_label": component.get("event_label") or event.replace("_", " ").title(),
                "section": SECTION_MAP.get(event, "other"),
                "text": text,
                "confidence": round(_component_confidence(component), 3),
                "support_level": component.get("support_level"),
                "source_model_version": component.get("model_version"),
                "source": component,
            }
        )
    return normalised


def _detect_tensions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_event = {item["event"]: item for item in items}
    tensions: list[dict[str, Any]] = []

    compatibility = by_event.get("marriage_compatibility_dynamics")
    challenges = by_event.get("relationship_challenges")
    if compatibility and challenges:
        c1 = _safe_float(compatibility.get("source", {}).get("support_score"), compatibility["confidence"])
        c2 = _safe_float(challenges.get("source", {}).get("support_score"), challenges["confidence"])
        if c1 >= 0.5 and c2 >= 0.5:
            tensions.append(
                {
                    "type": "mixed_relationship_signals",
                    "events": ["marriage_compatibility_dynamics", "relationship_challenges"],
                    "interpretation": (
                        "The chart can simultaneously show supportive compatibility patterns and meaningful adjustment pressure; "
                        "these should be presented together rather than treating one as cancelling the other."
                    ),
                }
            )

    quality = by_event.get("married_life_quality")
    if quality and challenges:
        q = _safe_float(quality.get("source", {}).get("support_score"), quality["confidence"])
        ch = _safe_float(challenges.get("source", {}).get("support_score"), challenges["confidence"])
        if q >= 0.5 and ch >= 0.5:
            tensions.append(
                {
                    "type": "quality_with_challenges",
                    "events": ["married_life_quality", "relationship_challenges"],
                    "interpretation": (
                        "Positive married-life potential may coexist with periods of stress or repair work; the synthesis should preserve both signals."
                    ),
                }
            )

    return tensions


def synthesize_marriage_profile_v1(components: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(components, dict):
        raise ValueError("components must be a dictionary.")

    items = _normalise_components(components)
    if not items:
        return {
            "available": False,
            "event": "marriage_synthesis",
            "model_version": "v1",
            "reason": "No usable marriage-analysis components were supplied for synthesis.",
            "component_count": 0,
            "sections": [],
            "tensions": [],
        }

    items.sort(key=lambda item: (-item["confidence"], item["event"]))

    sections: list[dict[str, Any]] = []
    for section_name in ("timing", "relationship_path", "spouse_profile", "married_life", "post_marriage", "other"):
        section_items = [item for item in items if item["section"] == section_name]
        if not section_items:
            continue
        sections.append(
            {
                "section": section_name,
                "label": SECTION_LABELS[section_name],
                "items": [
                    {
                        "event": item["event"],
                        "event_label": item["event_label"],
                        "statement": item["text"],
                        "confidence": item["confidence"],
                        "support_level": item["support_level"],
                        "source_model_version": item["source_model_version"],
                    }
                    for item in section_items
                ],
            }
        )

    strongest = items[:5]
    headline = strongest[0]["text"]
    overview_parts = [item["text"] for item in strongest[:3]]
    overview = " ".join(overview_parts)
    tensions = _detect_tensions(items)
    average_confidence = round(sum(item["confidence"] for item in items) / len(items), 3)

    return {
        "available": True,
        "event": "marriage_synthesis",
        "model_version": "v1",
        "component_count": len(items),
        "average_confidence": average_confidence,
        "headline": headline,
        "overview": overview,
        "sections": sections,
        "strongest_themes": [
            {
                "event": item["event"],
                "event_label": item["event_label"],
                "statement": item["text"],
                "confidence": item["confidence"],
            }
            for item in strongest
        ],
        "tensions": tensions,
        "limitation": (
            "This synthesis combines the supplied astrology modules; it does not create new evidence, override conflicting signals, "
            "or guarantee real-world events. Timing, partner characteristics and relationship outcomes remain probabilistic and symbolic."
        ),
        "components": {item["event"]: item["source"] for item in items},
    }
