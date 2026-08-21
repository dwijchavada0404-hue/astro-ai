from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.purpose_personal_growth_event_intelligence_v1 import analyze_purpose_personal_growth_event_intelligence_v1
from app.astrology.features.purpose_personal_growth_question_intelligence_v1 import analyze_purpose_personal_growth_question_v1
from app.astrology.features.purpose_personal_growth_reasoning_v1 import analyze_purpose_personal_growth_v1
from app.astrology.features.purpose_personal_growth_synthesis_v1 import analyze_purpose_personal_growth_synthesis_v1
from app.astrology.features.purpose_personal_growth_timing_v1 import analyze_purpose_personal_growth_timing_v1


EVENT_INTENTS = {
    "self_development", "creative_expression", "service_contribution", "knowledge_guidance", "public_contribution", "inner_growth",
}


def route_purpose_personal_growth_question_v1(
    chart: dict[str, Any], question: str, reference_moment: datetime
) -> dict[str, Any]:
    understanding = analyze_purpose_personal_growth_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Purpose & Personal Growth question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_purpose_personal_growth_v1(chart)

    if intent == "purpose_overview":
        synthesis = analyze_purpose_personal_growth_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")), "route": "purpose_personal_growth_synthesis_v1",
            "event": "purpose_personal_growth", "primary_intent": intent, "understanding": understanding,
            "synthesis": synthesis, "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_purpose_personal_growth_event_intelligence_v1(chart, reference_moment)
        event_result = events.get("events", {}).get(intent) if events.get("available") else None
        return {
            "available": bool(events.get("available")), "route": "purpose_personal_growth_event_v1",
            "event": "purpose_personal_growth", "event_key": intent, "primary_intent": intent,
            "understanding": understanding, "event_intelligence": events, "event_result": event_result,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "purpose_timing":
        timing = analyze_purpose_personal_growth_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")), "route": "purpose_personal_growth_timing_v1",
            "event": "purpose_personal_growth", "primary_intent": intent, "understanding": understanding,
            "timing": timing, "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")), "route": "purpose_personal_growth_natal_v1",
        "event": "purpose_personal_growth", "primary_intent": intent, "understanding": understanding,
        "natal": natal, "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
