from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.property_home_direction_v1 import analyze_property_home_direction_v1
from app.astrology.features.property_home_event_intelligence_v1 import analyze_property_home_event_intelligence_v1
from app.astrology.features.property_home_question_intelligence_v1 import analyze_property_home_question_v1
from app.astrology.features.property_home_reasoning_v1 import analyze_property_home_v1
from app.astrology.features.property_home_synthesis_v1 import analyze_property_home_synthesis_v1
from app.astrology.features.property_home_timing_v1 import analyze_property_home_timing_v1


EVENT_INTENTS = {
    "property_acquisition",
    "property_sale_disposal",
    "relocation",
    "inheritance_family_property",
    "renovation_construction",
}


def route_property_home_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    understanding = analyze_property_home_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Property & Home question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_property_home_v1(chart)

    if intent == "property_overview":
        synthesis = analyze_property_home_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")),
            "route": "property_home_synthesis_v1",
            "event": "property_home",
            "primary_intent": intent,
            "understanding": understanding,
            "synthesis": synthesis,
            "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_property_home_event_intelligence_v1(chart, reference_moment)
        event_result = None
        if events.get("available"):
            event_result = events.get("events", {}).get(intent)
        return {
            "available": bool(events.get("available")),
            "route": "property_home_event_v1",
            "event": "property_home",
            "event_key": intent,
            "primary_intent": intent,
            "understanding": understanding,
            "event_intelligence": events,
            "event_result": event_result,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "property_timing":
        timing = analyze_property_home_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")),
            "route": "property_home_timing_v1",
            "event": "property_home",
            "primary_intent": intent,
            "understanding": understanding,
            "timing": timing,
            "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    if intent == "property_direction":
        direction = analyze_property_home_direction_v1(chart)
        return {
            "available": bool(direction.get("available")),
            "route": "property_home_direction_v1",
            "event": "property_home",
            "primary_intent": intent,
            "understanding": understanding,
            "direction": direction,
            "answer": direction.get("answer") if direction.get("available") else direction.get("reason"),
            "limitation": direction.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")),
        "route": "property_home_natal_v1",
        "event": "property_home",
        "primary_intent": intent,
        "understanding": understanding,
        "natal": natal,
        "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
