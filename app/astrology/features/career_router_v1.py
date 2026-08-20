from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.career_direction_intelligence_v1 import analyze_career_direction_v1
from app.astrology.features.career_event_intelligence_v1 import analyze_career_event_intelligence_v1
from app.astrology.features.career_job_business_intelligence_v1 import analyze_job_vs_business_v1
from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1
from app.astrology.features.career_question_intelligence_v1 import analyze_career_question_v1
from app.astrology.features.career_synthesis_v1 import analyze_career_synthesis_v1
from app.astrology.features.career_timing_v1 import analyze_career_timing_v1
from app.astrology.features.career_trajectory_v1 import analyze_career_trajectory_v1


EVENT_ROUTE = {
    "promotion": "promotion",
    "job_change": "job_change",
    "new_job": "new_job",
    "foreign_work": "foreign_work",
    "career_challenges": "job_loss_challenge",
}

SYNTHESIS_PHRASES = (
    "overall career", "complete career", "full career", "career overview", "career future",
    "tell me about my career", "how will my career progress", "career progression",
)


def _is_synthesis_question(question: str) -> bool:
    q = question.strip().lower()
    if any(phrase in q for phrase in SYNTHESIS_PHRASES):
        return True
    dimensions = 0
    dimensions += int(any(token in q for token in ("career", "profession", "direction", "field")))
    dimensions += int(any(token in q for token in ("job or business", "job vs business", "business or job")))
    dimensions += int(any(token in q for token in ("when", "timing", "period", "future")))
    dimensions += int(any(token in q for token in ("promotion", "job change", "new job", "foreign work")))
    dimensions += int(any(token in q for token in ("progress", "trajectory", "challenge", "recovery", "stability")))
    return dimensions >= 3


def route_career_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    """Route Career questions to the most specific Career V1 reasoning layer."""
    understanding = analyze_career_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Career & Profession question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_career_profession_v1(chart)

    if _is_synthesis_question(question):
        synthesis = analyze_career_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")), "route": "career_synthesis_v1",
            "event": "career_profession", "primary_intent": intent, "understanding": understanding,
            "natal": natal, "synthesis": synthesis,
            "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_ROUTE:
        intelligence = analyze_career_event_intelligence_v1(chart, reference_moment)
        event_key = EVENT_ROUTE[intent]
        event_result = intelligence.get("events", {}).get(event_key) if intelligence.get("available") else None
        return {
            "available": bool(intelligence.get("available")), "route": "career_event_v1",
            "event": "career_profession", "primary_intent": intent, "event_key": event_key,
            "understanding": understanding, "natal": natal, "event_intelligence": intelligence,
            "event_result": event_result,
            "answer": intelligence.get("answer") if intelligence.get("available") else intelligence.get("reason"),
            "limitation": intelligence.get("limitation") or natal.get("limitation"),
        }

    if intent == "job_vs_business":
        result = analyze_job_vs_business_v1(chart)
        return {
            "available": bool(result.get("available")), "route": "career_job_vs_business_v1",
            "event": "career_profession", "primary_intent": intent, "understanding": understanding,
            "natal": natal, "job_vs_business": result,
            "answer": result.get("answer") if result.get("available") else result.get("reason"),
            "limitation": result.get("limitation") or natal.get("limitation"),
        }

    if intent == "career_direction":
        result = analyze_career_direction_v1(chart)
        return {
            "available": bool(result.get("available")), "route": "career_direction_v1",
            "event": "career_profession", "primary_intent": intent, "understanding": understanding,
            "natal": natal, "direction": result,
            "answer": result.get("answer") if result.get("available") else result.get("reason"),
            "limitation": result.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "career_timing":
        result = analyze_career_timing_v1(chart, reference_moment)
        return {
            "available": bool(result.get("available")), "route": "career_timing_v1",
            "event": "career_profession", "primary_intent": intent, "understanding": understanding,
            "natal": natal, "timing": result,
            "answer": result.get("answer") if result.get("available") else result.get("reason"),
            "limitation": result.get("limitation") or natal.get("limitation"),
        }

    if intent == "career_overview":
        trajectory = analyze_career_trajectory_v1(chart, reference_moment)
        return {
            "available": bool(trajectory.get("available")), "route": "career_trajectory_v1",
            "event": "career_profession", "primary_intent": intent, "understanding": understanding,
            "natal": natal, "trajectory": trajectory,
            "answer": trajectory.get("answer") if trajectory.get("available") else trajectory.get("reason"),
            "limitation": trajectory.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")), "route": "career_natal_v1",
        "event": "career_profession", "primary_intent": intent, "understanding": understanding,
        "natal": natal, "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
