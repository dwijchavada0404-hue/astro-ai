from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.education_learning_event_intelligence_v1 import analyze_education_learning_event_intelligence_v1
from app.astrology.features.education_learning_question_intelligence_v1 import analyze_education_learning_question_v1
from app.astrology.features.education_learning_reasoning_v1 import analyze_education_learning_v1
from app.astrology.features.education_learning_synthesis_v1 import analyze_education_learning_synthesis_v1
from app.astrology.features.education_learning_timing_v1 import analyze_education_learning_timing_v1


EVENT_INTENTS = {
    "admission_enrolment", "exam_assessment", "higher_study_transition", "skill_certification", "research_deep_study",
}


def route_education_learning_question_v1(
    chart: dict[str, Any], question: str, reference_moment: datetime
) -> dict[str, Any]:
    understanding = analyze_education_learning_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as an Education & Learning question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_education_learning_v1(chart)

    if intent == "education_overview":
        synthesis = analyze_education_learning_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")), "route": "education_learning_synthesis_v1",
            "event": "education_learning", "primary_intent": intent, "understanding": understanding,
            "synthesis": synthesis, "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_education_learning_event_intelligence_v1(chart, reference_moment)
        event_result = events.get("events", {}).get(intent) if events.get("available") else None
        return {
            "available": bool(events.get("available")), "route": "education_learning_event_v1",
            "event": "education_learning", "event_key": intent, "primary_intent": intent,
            "understanding": understanding, "event_intelligence": events, "event_result": event_result,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "education_timing":
        timing = analyze_education_learning_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")), "route": "education_learning_timing_v1",
            "event": "education_learning", "primary_intent": intent, "understanding": understanding,
            "timing": timing, "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")), "route": "education_learning_natal_v1",
        "event": "education_learning", "primary_intent": intent, "understanding": understanding,
        "natal": natal, "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
