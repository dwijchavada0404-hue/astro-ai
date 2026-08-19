from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)
from app.astrology.features.marriage_forecast_router_v3 import (
    route_marriage_question_v3,
)
from app.astrology.features.marriage_synthesis_reasoning_v1 import (
    synthesize_marriage_profile_v1,
)


DEFAULT_COMPONENT_QUERIES: tuple[tuple[str, str], ...] = (
    ("marriage_timing", "When am I likely to get married?"),
    ("spouse_meeting", "When am I likely to meet my future spouse?"),
    ("love_vs_arranged", "Is my marriage more likely to be love or arranged?"),
    ("foreign_intercultural_connection", "Is there a foreign or intercultural marriage tendency?"),
    ("spouse_traits", "What personality traits may my future spouse have?"),
    ("spouse_appearance", "What may my future spouse look like?"),
    ("spouse_profession", "What profession or career profile may my future spouse have?"),
    ("spouse_education", "What education or intellectual profile may my future spouse have?"),
    ("spouse_wealth", "What financial profile may my future spouse have?"),
    ("spouse_family_background", "What family or social background may my future spouse have?"),
    ("spouse_age_profile", "What age or maturity profile may my future spouse have?"),
    ("married_life_quality", "What is the overall quality of my married life likely to be?"),
    ("relationship_challenges", "What relationship challenges may arise in my marriage?"),
    ("marriage_compatibility_dynamics", "What partner dynamics and compatibility patterns may shape my marriage?"),
    ("post_marriage_life_changes", "How could my life change after marriage?"),
)


def _require_timezone(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")


def _collect_component(
    chart: dict[str, Any],
    reference_moment: datetime,
    expected_event: str,
    question: str,
) -> dict[str, Any]:
    question_analysis = analyze_marriage_question_v3(question)
    result = route_marriage_question_v3(chart, question_analysis, reference_moment)
    if not isinstance(result, dict):
        return {
            "available": False,
            "event": expected_event,
            "reason": "The routed marriage module did not return a dictionary result.",
        }
    return result


def synthesize_marriage_profile_v2(
    chart: dict[str, Any],
    reference_moment: datetime,
    *,
    include_timing: bool = True,
    component_queries: tuple[tuple[str, str], ...] | None = None,
) -> dict[str, Any]:
    """Collect existing V3 marriage capabilities and synthesize them.

    V2 is an orchestration layer: it does not create new astrology evidence.
    Each component is obtained through the same V3 intelligence/router path
    used by the public marriage question flow, then passed into the V1
    synthesis engine.
    """
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    _require_timezone(reference_moment)

    queries = component_queries or DEFAULT_COMPONENT_QUERIES
    components: dict[str, Any] = {}
    collection_errors: list[dict[str, str]] = []

    for expected_event, question in queries:
        if not include_timing and expected_event in {"marriage_timing", "spouse_meeting"}:
            continue
        try:
            result = _collect_component(chart, reference_moment, expected_event, question)
        except Exception as exc:  # isolate one capability from the full synthesis
            collection_errors.append(
                {
                    "event": expected_event,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )
            continue

        actual_event = str(result.get("event") or expected_event)
        # Preserve the expected slot so synthesis remains deterministic even if
        # a future detector chooses a neighbouring route for a phrasing.
        components[expected_event] = result
        if actual_event != expected_event:
            collection_errors.append(
                {
                    "event": expected_event,
                    "error_type": "route_mismatch",
                    "message": f"Expected {expected_event} but router returned {actual_event}.",
                }
            )

    synthesis = synthesize_marriage_profile_v1(components)
    synthesis["model_version"] = "v2"
    synthesis["orchestration"] = {
        "collector": "marriage_question_intelligence_v3 + marriage_forecast_router_v3",
        "requested_component_count": sum(
            1
            for event, _ in queries
            if include_timing or event not in {"marriage_timing", "spouse_meeting"}
        ),
        "collected_component_count": len(components),
        "include_timing": include_timing,
        "collection_errors": collection_errors,
    }
    synthesis["components"] = components
    synthesis["limitation"] = (
        str(synthesis.get("limitation", "")).rstrip()
        + " V2 only orchestrates existing marriage engines and does not manufacture missing evidence."
    ).strip()
    return synthesis
