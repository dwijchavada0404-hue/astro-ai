from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.travel_journeys_event_intelligence_v1 import analyze_travel_journeys_event_intelligence_v1
from app.astrology.features.travel_journeys_question_intelligence_v1 import analyze_travel_journeys_question_v1
from app.astrology.features.travel_journeys_reasoning_v1 import analyze_travel_journeys_v1
from app.astrology.features.travel_journeys_synthesis_v1 import analyze_travel_journeys_synthesis_v1
from app.astrology.features.travel_journeys_timing_v1 import analyze_travel_journeys_timing_v1
from app.astrology.features.travel_journeys_trajectory_v1 import analyze_travel_journeys_trajectory_v1


def route_travel_journeys_question_v1(question: str, chart: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:
    intelligence = analyze_travel_journeys_question_v1(question)
    if intelligence.get("handoff_to_location_settlement"):
        return {"available": False, "event": "travel_journeys", "model_version": "v1", "reason": "Permanent relocation or settlement belongs to the Location & Foreign Settlement domain.", "question_intelligence": intelligence}
    if intelligence.get("restricted_outcome_requested"):
        return {"available": True, "event": "travel_journeys", "model_version": "v1", "restricted": True, "answer": "I can discuss symbolic travel and mobility themes, but not predict visa approval, exact destinations, travel safety, accidents, delays or disruptions.", "question_intelligence": intelligence}
    if not intelligence.get("available"):
        return {"available": False, "event": "travel_journeys", "model_version": "v1", "reason": "Question was not recognized as a Travel & Journeys question.", "question_intelligence": intelligence}
    intent = intelligence["primary_intent"]
    if intent == "travel_overview":
        result = analyze_travel_journeys_synthesis_v1(chart, reference_moment)
    elif intelligence.get("timing_requested") or intent == "travel_timing":
        result = analyze_travel_journeys_timing_v1(chart, reference_moment)
    elif intent in {"short_journeys", "long_distance_travel", "international_travel", "work_study_travel", "recurring_mobility", "travel_adaptability"}:
        result = analyze_travel_journeys_event_intelligence_v1(chart, reference_moment)
    else:
        result = analyze_travel_journeys_trajectory_v1(chart, reference_moment)
    return {"available": bool(result.get("available")), "event": "travel_journeys", "model_version": "v1", "intent": intent, "question_intelligence": intelligence, "result": result}
