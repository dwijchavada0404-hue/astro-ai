from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.legal_disputes_conflict_event_intelligence_v1 import analyze_legal_disputes_conflict_event_intelligence_v1
from app.astrology.features.legal_disputes_conflict_question_intelligence_v1 import analyze_legal_disputes_conflict_question_v1
from app.astrology.features.legal_disputes_conflict_reasoning_v1 import analyze_legal_disputes_conflict_v1
from app.astrology.features.legal_disputes_conflict_synthesis_v1 import analyze_legal_disputes_conflict_synthesis_v1
from app.astrology.features.legal_disputes_conflict_timing_v1 import analyze_legal_disputes_conflict_timing_v1


EVENT_INTENTS = {
    "dispute_engagement",
    "negotiation_mediation",
    "complexity_endurance",
    "principles_fairness",
    "competition_assertiveness",
    "resolution_capacity",
}


def _blocked_response(understanding: dict[str, Any]) -> dict[str, Any]:
    return {
        "available": True,
        "route": "legal_disputes_conflict_safety_boundary_v1",
        "event": "legal_disputes_conflict",
        "primary_intent": understanding.get("primary_intent"),
        "understanding": understanding,
        "answer": (
            "AstroAI can discuss symbolic themes around conflict, negotiation, endurance, fairness and resolution, "
            "but it cannot provide legal advice or predict guilt, liability, verdicts, arrest, imprisonment, criminal or regulatory outcomes, exact settlement amounts, or whether a matter will be won or lost."
        ),
        "limitation": (
            "Known legal history and actual outcomes override astrology. Legal strategy, rights, remedies and case-specific decisions require a qualified legal professional."
        ),
    }


def route_legal_disputes_conflict_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    understanding = analyze_legal_disputes_conflict_question_v1(question)
    if understanding.get("prohibited_request_detected"):
        return _blocked_response(understanding)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Legal, Disputes & Conflict question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_legal_disputes_conflict_v1(chart)

    if understanding.get("requires_timing_engine") or intent == "legal_disputes_timing":
        timing = analyze_legal_disputes_conflict_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")),
            "route": "legal_disputes_conflict_timing_v1",
            "event": "legal_disputes_conflict",
            "primary_intent": intent,
            "understanding": understanding,
            "timing": timing,
            "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    if intent == "legal_disputes_overview":
        synthesis = analyze_legal_disputes_conflict_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")),
            "route": "legal_disputes_conflict_synthesis_v1",
            "event": "legal_disputes_conflict",
            "primary_intent": intent,
            "understanding": understanding,
            "synthesis": synthesis,
            "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_legal_disputes_conflict_event_intelligence_v1(chart, reference_moment)
        return {
            "available": bool(events.get("available")),
            "route": "legal_disputes_conflict_event_v1",
            "event": "legal_disputes_conflict",
            "primary_intent": intent,
            "understanding": understanding,
            "event_intelligence": events,
            "event_result": (events.get("events") or {}).get(intent) if events.get("available") else None,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")),
        "route": "legal_disputes_conflict_natal_v1",
        "event": "legal_disputes_conflict",
        "primary_intent": intent,
        "understanding": understanding,
        "natal": natal,
        "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
