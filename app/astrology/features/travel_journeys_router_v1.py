from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.travel_journeys_event_intelligence_v1 import analyze_travel_journeys_event_intelligence_v1
from app.astrology.features.travel_journeys_question_intelligence_v1 import analyze_travel_journeys_question_v1
from app.astrology.features.travel_journeys_reasoning_v1 import analyze_travel_journeys_v1
from app.astrology.features.travel_journeys_synthesis_v1 import analyze_travel_journeys_synthesis_v1
from app.astrology.features.travel_journeys_timing_v1 import analyze_travel_journeys_timing_v1


EVENT_INTENTS = {
    "short_journeys": "short_journey",
    "long_distance_travel": "long_distance_travel",
    "international_travel": "international_exposure",
    "work_study_travel": "work_study_travel",
    "recurring_mobility": "recurring_mobility",
    "travel_adaptability": "travel_adaptability",
}


def _restricted_response(understanding: dict[str, Any]) -> dict[str, Any]:
    return {
        "available": True,
        "route": "travel_journeys_safety_boundary_v1",
        "event": "travel_journeys",
        "primary_intent": understanding.get("primary_intent"),
        "understanding": understanding,
        "answer": "AstroAI can discuss symbolic travel and mobility themes, but it cannot predict visa approval, exact destinations, travel safety, accidents, delays or disruptions.",
        "limitation": "Visa/immigration approval, exact-destination certainty and travel-safety/accident prediction are outside this domain's allowed outputs.",
    }


def route_travel_journeys_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    understanding = analyze_travel_journeys_question_v1(question)

    if understanding.get("handoff_to_location_settlement"):
        return {
            "available": False,
            "route": "travel_to_location_settlement_handoff_v1",
            "event": "travel_journeys",
            "understanding": understanding,
            "reason": "Permanent relocation or settlement belongs to the Location & Foreign Settlement domain.",
        }
    if understanding.get("restricted_outcome_requested"):
        return _restricted_response(understanding)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Travel & Journeys question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_travel_journeys_v1(chart)

    if intent == "travel_overview":
        synthesis = analyze_travel_journeys_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")),
            "route": "travel_journeys_synthesis_v1",
            "event": "travel_journeys",
            "primary_intent": intent,
            "understanding": understanding,
            "synthesis": synthesis,
            "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "travel_timing":
        timing = analyze_travel_journeys_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")),
            "route": "travel_journeys_timing_v1",
            "event": "travel_journeys",
            "primary_intent": intent,
            "understanding": understanding,
            "timing": timing,
            "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_travel_journeys_event_intelligence_v1(chart, reference_moment)
        event_key = EVENT_INTENTS[intent]
        return {
            "available": bool(events.get("available")),
            "route": "travel_journeys_event_v1",
            "event": "travel_journeys",
            "event_key": event_key,
            "primary_intent": intent,
            "understanding": understanding,
            "event_intelligence": events,
            "event_result": (events.get("events") or {}).get(event_key) if events.get("available") else None,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")),
        "route": "travel_journeys_natal_v1",
        "event": "travel_journeys",
        "primary_intent": intent,
        "understanding": understanding,
        "natal": natal,
        "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
