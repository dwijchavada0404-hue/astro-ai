from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.family_children_direction_v1 import analyze_family_children_direction_v1
from app.astrology.features.family_children_events_v1 import analyze_family_children_events_v1
from app.astrology.features.family_children_question_intelligence_v1 import analyze_family_children_question_v1
from app.astrology.features.family_children_reasoning_v1 import analyze_family_children_v1
from app.astrology.features.family_children_synthesis_v1 import analyze_family_children_synthesis_v1
from app.astrology.features.family_children_timing_v1 import analyze_family_children_timing_v1


EVENT_MAP = {
    "children_parenting": "parenting_nurturing",
    "family_growth": "family_growth_responsibility",
    "family_change": "family_structure_change",
    "family_support": "intergenerational_support",
}


def route_family_children_question_v1(chart: dict[str, Any], question: str, reference_moment: datetime) -> dict[str, Any]:
    understanding = analyze_family_children_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Family & Children question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_family_children_v1(chart)

    if intent == "family_overview":
        synthesis = analyze_family_children_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")),
            "route": "family_children_synthesis_v1",
            "event": "family_children",
            "primary_intent": intent,
            "understanding": understanding,
            "synthesis": synthesis,
            "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
            "children_question_boundary": synthesis.get("children_question_boundary"),
        }

    if intent in EVENT_MAP:
        events = analyze_family_children_events_v1(chart, reference_moment)
        event_key = EVENT_MAP[intent]
        event_result = None
        if events.get("available"):
            event_result = next((item for item in events.get("ranked_events", []) if item.get("event") == event_key), None)
        return {
            "available": bool(events.get("available")),
            "route": "family_children_event_v1",
            "event": "family_children",
            "event_key": event_key,
            "primary_intent": intent,
            "understanding": understanding,
            "event_intelligence": events,
            "event_result": event_result,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
            "children_question_boundary": events.get("children_question_boundary"),
        }

    if understanding.get("requires_timing_engine") or intent == "family_timing":
        timing = analyze_family_children_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")),
            "route": "family_children_timing_v1",
            "event": "family_children",
            "primary_intent": intent,
            "understanding": understanding,
            "timing": timing,
            "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    if intent == "family_direction":
        direction = analyze_family_children_direction_v1(chart)
        return {
            "available": bool(direction.get("available")),
            "route": "family_children_direction_v1",
            "event": "family_children",
            "primary_intent": intent,
            "understanding": understanding,
            "direction": direction,
            "answer": direction.get("answer") if direction.get("available") else direction.get("reason"),
            "limitation": direction.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")),
        "route": "family_children_natal_v1",
        "event": "family_children",
        "primary_intent": intent,
        "understanding": understanding,
        "natal": natal,
        "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
