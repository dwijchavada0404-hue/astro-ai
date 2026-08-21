from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.friends_social_community_event_intelligence_v1 import analyze_friends_social_community_event_intelligence_v1
from app.astrology.features.friends_social_community_question_intelligence_v1 import analyze_friends_social_community_question_v1
from app.astrology.features.friends_social_community_reasoning_v1 import analyze_friends_social_community_v1
from app.astrology.features.friends_social_community_synthesis_v1 import analyze_friends_social_community_synthesis_v1
from app.astrology.features.friends_social_community_timing_v1 import analyze_friends_social_community_timing_v1


EVENT_INTENTS = {"friendship_connection", "network_collaboration", "community_participation", "social_boundary_reset"}


def route_friends_social_community_question_v1(chart: dict[str, Any], question: str, reference_moment: datetime) -> dict[str, Any]:
    understanding = analyze_friends_social_community_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Friends, Social Networks & Community question.",
        }

    intent = str(understanding.get("primary_intent") or "unknown")
    natal = analyze_friends_social_community_v1(chart)

    if intent == "social_overview":
        synthesis = analyze_friends_social_community_synthesis_v1(chart, reference_moment)
        return {
            "available": bool(synthesis.get("available")), "route": "friends_social_community_synthesis_v1",
            "event": "friends_social_community", "primary_intent": intent, "understanding": understanding,
            "synthesis": synthesis, "answer": synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason"),
            "limitation": synthesis.get("limitation") or natal.get("limitation"),
        }

    if intent in EVENT_INTENTS:
        events = analyze_friends_social_community_event_intelligence_v1(chart, reference_moment)
        event_result = events.get("events", {}).get(intent) if events.get("available") else None
        return {
            "available": bool(events.get("available")), "route": "friends_social_community_event_v1",
            "event": "friends_social_community", "event_key": intent, "primary_intent": intent,
            "understanding": understanding, "event_intelligence": events, "event_result": event_result,
            "answer": events.get("answer") if events.get("available") else events.get("reason"),
            "limitation": events.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine") or intent == "social_timing":
        timing = analyze_friends_social_community_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")), "route": "friends_social_community_timing_v1",
            "event": "friends_social_community", "primary_intent": intent, "understanding": understanding,
            "timing": timing, "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    return {
        "available": bool(natal.get("available")), "route": "friends_social_community_natal_v1",
        "event": "friends_social_community", "primary_intent": intent, "understanding": understanding,
        "natal": natal, "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
