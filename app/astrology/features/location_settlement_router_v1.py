from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.location_settlement_event_intelligence_v1 import analyze_location_settlement_event_intelligence_v1
from app.astrology.features.location_settlement_question_intelligence_v1 import analyze_location_settlement_question_v1
from app.astrology.features.location_settlement_reasoning_v1 import analyze_location_settlement_v1
from app.astrology.features.location_settlement_synthesis_v1 import analyze_location_settlement_synthesis_v1
from app.astrology.features.location_settlement_timing_v1 import analyze_location_settlement_timing_v1


EVENT_INTENTS = {
    "domestic_relocation", "foreign_travel_exposure", "long_distance_residence",
    "foreign_settlement", "return_or_re_rooting",
}


def route_location_settlement_question_v1(
    chart: dict[str, Any], question: str, reference_moment: datetime
) -> dict[str, Any]:
    understanding = analyze_location_settlement_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Location & Foreign Settlement question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_location_settlement_v1(chart)

    if intent == "location_overview":
        synthesis = analyze_location_settlement_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")), "route": "location_settlement_synthesis_v1",
            "event": "location_settlement", "primary_intent": intent, "understanding": understanding,
            "synthesis": synthesis, "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_location_settlement_event_intelligence_v1(chart, reference_moment)
        event_result = events.get("events", {}).get(intent) if events.get("available") else None
        return {
            "available": bool(events.get("available")), "route": "location_settlement_event_v1",
            "event": "location_settlement", "event_key": intent, "primary_intent": intent,
            "understanding": understanding, "event_intelligence": events, "event_result": event_result,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "location_timing":
        timing = analyze_location_settlement_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")), "route": "location_settlement_timing_v1",
            "event": "location_settlement", "primary_intent": intent, "understanding": understanding,
            "timing": timing, "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")), "route": "location_settlement_natal_v1",
        "event": "location_settlement", "primary_intent": intent, "understanding": understanding,
        "natal": natal, "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
