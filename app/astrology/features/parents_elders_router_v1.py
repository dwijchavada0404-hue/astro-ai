from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.parents_elders_event_intelligence_v1 import analyze_parents_elders_event_intelligence_v1
from app.astrology.features.parents_elders_question_intelligence_v1 import analyze_parents_elders_question_v1
from app.astrology.features.parents_elders_reasoning_v1 import analyze_parents_elders_v1
from app.astrology.features.parents_elders_synthesis_v1 import analyze_parents_elders_synthesis_v1
from app.astrology.features.parents_elders_timing_v1 import analyze_parents_elders_timing_v1


EVENT_INTENTS = {"emotional_support", "guidance_mentorship", "duty_responsibility", "authority_structure", "independence_boundaries", "family_continuity"}
EVENT_MAP = {
    "emotional_support": "emotional_support",
    "guidance_mentorship": "guidance_mentorship",
    "duty_responsibility": "duty_responsibility",
    "authority_structure": "authority_structure",
    "independence_boundaries": "independence_boundaries",
    "family_continuity": "family_continuity",
}


def _blocked_response(understanding: dict[str, Any]) -> dict[str, Any]:
    return {
        "available": True,
        "route": "parents_elders_safety_boundary_v1",
        "event": "parents_elders",
        "primary_intent": understanding.get("primary_intent"),
        "understanding": understanding,
        "answer": "AstroAI can discuss symbolic parent/elder relationship, responsibility, guidance and boundary themes, but it cannot predict another person's illness, health outcome, lifespan, death, intentions or character.",
        "limitation": "Health diagnosis/prognosis, lifespan/death prediction and specific-person intention/character inference are outside this domain's allowed outputs.",
    }


def route_parents_elders_question_v1(chart: dict[str, Any], question: str, reference_moment: datetime) -> dict[str, Any]:
    understanding = analyze_parents_elders_question_v1(question)
    if not understanding.get("available"):
        return {"available": False, "route": "unsupported", "event": "unknown", "understanding": understanding, "reason": "The question was not identified as a Parents & Elders question."}
    if understanding.get("prohibited_request_detected"):
        return _blocked_response(understanding)

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_parents_elders_v1(chart)
    if intent == "parents_elders_overview":
        synthesis = analyze_parents_elders_synthesis_v1(chart, reference_moment)
        return {"available": bool(synthesis.get("available")), "route": "parents_elders_synthesis_v1", "event": "parents_elders", "primary_intent": intent, "understanding": understanding, "synthesis": synthesis, "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"), "limitation": synthesis.get("limitation") or natal.get("limitation")}
    if intent in EVENT_INTENTS:
        events = analyze_parents_elders_event_intelligence_v1(chart, reference_moment)
        event_key = EVENT_MAP[intent]
        return {"available": bool(events.get("available")), "route": "parents_elders_event_v1", "event": "parents_elders", "event_key": event_key, "primary_intent": intent, "understanding": understanding, "event_intelligence": events, "event_result": (events.get("events") or {}).get(event_key) if events.get("available") else None, "answer": events.get("answer") if events.get("available") else events.get("reason"), "limitation": events.get("limitation") or natal.get("limitation")}
    if understanding.get("requires_timing_engine") or intent == "parents_elders_timing":
        timing = analyze_parents_elders_timing_v1(chart, reference_moment)
        return {"available": bool(timing.get("available")), "route": "parents_elders_timing_v1", "event": "parents_elders", "primary_intent": intent, "understanding": understanding, "timing": timing, "answer": timing.get("answer") if timing.get("available") else timing.get("reason"), "limitation": timing.get("limitation") or natal.get("limitation")}
    return {"available": bool(natal.get("available")), "route": "parents_elders_natal_v1", "event": "parents_elders", "primary_intent": intent, "understanding": understanding, "natal": natal, "answer": natal.get("summary") if natal.get("available") else natal.get("reason"), "limitation": natal.get("limitation")}
