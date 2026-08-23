from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.health_wellbeing_event_intelligence_v1 import analyze_health_wellbeing_event_intelligence_v1
from app.astrology.features.health_wellbeing_question_intelligence_v1 import analyze_health_wellbeing_question_v1
from app.astrology.features.health_wellbeing_reasoning_v1 import analyze_health_wellbeing_v1
from app.astrology.features.health_wellbeing_synthesis_v1 import analyze_health_wellbeing_synthesis_v1
from app.astrology.features.health_wellbeing_timing_v1 import analyze_health_wellbeing_timing_v1


EVENT_INTENTS = {
    "vitality_energy",
    "routine_discipline",
    "recovery_resilience",
    "stress_balance",
    "rest_restoration",
    "preventive_self_care",
}


def _blocked_response(understanding: dict[str, Any]) -> dict[str, Any]:
    return {
        "available": True,
        "route": "health_wellbeing_safety_boundary_v1",
        "event": "health_wellbeing",
        "primary_intent": understanding.get("primary_intent"),
        "understanding": understanding,
        "answer": (
            "AstroAI can discuss symbolic wellbeing themes such as energy management, routine, resilience, stress balance, rest and self-care, "
            "but it cannot diagnose or predict disease, illness, injury, prognosis, lifespan, death, accidents or fertility, and it cannot recommend treatment, medication, tests, procedures or supplements."
        ),
        "limitation": (
            "Known symptoms, diagnoses, medical history and clinician advice override astrology. Medical diagnosis, prognosis and treatment decisions are outside this domain."
        ),
    }


def route_health_wellbeing_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    understanding = analyze_health_wellbeing_question_v1(question)
    if understanding.get("prohibited_request_detected"):
        return _blocked_response(understanding)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Health & Wellbeing question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_health_wellbeing_v1(chart)

    if intent == "health_wellbeing_overview":
        synthesis = analyze_health_wellbeing_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")),
            "route": "health_wellbeing_synthesis_v1",
            "event": "health_wellbeing",
            "primary_intent": intent,
            "understanding": understanding,
            "synthesis": synthesis,
            "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "health_wellbeing_timing":
        timing = analyze_health_wellbeing_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")),
            "route": "health_wellbeing_timing_v1",
            "event": "health_wellbeing",
            "primary_intent": intent,
            "understanding": understanding,
            "timing": timing,
            "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_health_wellbeing_event_intelligence_v1(chart, reference_moment)
        return {
            "available": bool(events.get("available")),
            "route": "health_wellbeing_event_v1",
            "event": "health_wellbeing",
            "primary_intent": intent,
            "understanding": understanding,
            "event_intelligence": events,
            "event_result": (events.get("events") or {}).get(intent) if events.get("available") else None,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")),
        "route": "health_wellbeing_natal_v1",
        "event": "health_wellbeing",
        "primary_intent": intent,
        "understanding": understanding,
        "natal": natal,
        "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
