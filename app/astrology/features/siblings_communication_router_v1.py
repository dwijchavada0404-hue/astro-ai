from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.siblings_communication_event_intelligence_v1 import analyze_siblings_communication_event_intelligence_v1
from app.astrology.features.siblings_communication_question_intelligence_v1 import analyze_siblings_communication_question_v1
from app.astrology.features.siblings_communication_reasoning_v1 import analyze_siblings_communication_v1
from app.astrology.features.siblings_communication_synthesis_v1 import analyze_siblings_communication_synthesis_v1
from app.astrology.features.siblings_communication_timing_v1 import analyze_siblings_communication_timing_v1


EVENT_INTENTS = {"sibling_relationship", "communication_expression", "initiative_courage", "learning_skills", "collaboration_exchange", "boundaries_competition"}
EVENT_MAP = {
    "sibling_relationship": "sibling_peer_connection",
    "communication_expression": "communication_expression",
    "initiative_courage": "initiative_skill_building",
    "learning_skills": "initiative_skill_building",
    "collaboration_exchange": "collaboration_exchange",
    "boundaries_competition": "boundary_assertiveness",
}


def route_siblings_communication_question_v1(chart: dict[str, Any], question: str, reference_moment: datetime) -> dict[str, Any]:
    understanding = analyze_siblings_communication_question_v1(question)
    if not understanding.get("available"):
        return {"available": False, "route": "unsupported", "event": "unknown", "understanding": understanding, "reason": "The question was not identified as a Siblings & Communication question."}

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_siblings_communication_v1(chart)

    if intent == "siblings_communication_overview":
        synthesis = analyze_siblings_communication_synthesis_v1(chart, reference_moment)
        return {"available": bool(synthesis.get("available")), "route": "siblings_communication_synthesis_v1", "event": "siblings_communication", "primary_intent": intent, "understanding": understanding, "synthesis": synthesis, "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"), "limitation": synthesis.get("limitation") or natal.get("limitation")}

    if intent in EVENT_INTENTS:
        events = analyze_siblings_communication_event_intelligence_v1(chart, reference_moment)
        event_key = EVENT_MAP[intent]
        return {"available": bool(events.get("available")), "route": "siblings_communication_event_v1", "event": "siblings_communication", "event_key": event_key, "primary_intent": intent, "understanding": understanding, "event_intelligence": events, "event_result": (events.get("events") or {}).get(event_key) if events.get("available") else None, "answer": events.get("answer") if events.get("available") else events.get("reason"), "limitation": events.get("limitation") or natal.get("limitation")}

    if understanding.get("requires_timing_engine") or intent == "siblings_communication_timing":
        timing = analyze_siblings_communication_timing_v1(chart, reference_moment)
        return {"available": bool(timing.get("available")), "route": "siblings_communication_timing_v1", "event": "siblings_communication", "primary_intent": intent, "understanding": understanding, "timing": timing, "answer": timing.get("answer") if timing.get("available") else timing.get("reason"), "limitation": timing.get("limitation") or natal.get("limitation")}

    return {"available": bool(natal.get("available")), "route": "siblings_communication_natal_v1", "event": "siblings_communication", "primary_intent": intent, "understanding": understanding, "natal": natal, "answer": natal.get("summary") if natal.get("available") else natal.get("reason"), "limitation": natal.get("limitation")}
