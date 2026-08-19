from __future__ import annotations

from typing import Any


VALID_RELATIONSHIP_STATUSES = {
    "single",
    "in_relationship",
    "engaged",
    "married",
    "separated",
    "divorced",
    "widowed",
    "prefer_not_to_say",
    "unknown",
}


def _normalise_status(value: str | None) -> str:
    if value is None:
        return "unknown"
    status = value.strip().lower().replace(" ", "_")
    aliases = {
        "in_a_relationship": "in_relationship",
        "relationship": "in_relationship",
        "never_married": "single",
    }
    status = aliases.get(status, status)
    if status not in VALID_RELATIONSHIP_STATUSES:
        raise ValueError(f"Unsupported relationship_status: {value}")
    return status


def guard_marriage_question(
    question_analysis: dict[str, Any],
    relationship_status: str | None = None,
) -> dict[str, Any]:
    """Resolve known real-world relationship state before astrology routing.

    This layer never infers factual marital status from a birth chart. It only
    uses user-provided/profile context and decides whether the downstream
    Marriage router can proceed or should first clarify the user's intent.
    """
    if not isinstance(question_analysis, dict):
        raise ValueError("question_analysis must be a dictionary.")

    status = _normalise_status(relationship_status)
    event = str(question_analysis.get("primary_event") or question_analysis.get("event") or "")
    intent = question_analysis.get("intent") if isinstance(question_analysis.get("intent"), dict) else {}
    qtype = str(intent.get("question_type") or "")
    question = str(
        question_analysis.get("normalised_question")
        or question_analysis.get("original_question")
        or ""
    ).lower()

    marriage_timing_like = (
        event == "marriage_timing"
        or qtype == "timing" and ("marri" in question or "wedding" in question)
    )
    meeting_spouse_like = event == "spouse_meeting" or "meet my spouse" in question or "meet future spouse" in question

    if status == "married" and (marriage_timing_like or meeting_spouse_like):
        return {
            "action": "clarify",
            "relationship_status": status,
            "reason": "known_status_conflicts_with_literal_question",
            "suggested_interpretations": [
                "retrospective_existing_marriage_timing",
                "future_relationship_or_commitment_phase",
                "remarriage_if_that_is_what_user_means",
            ],
            "message": (
                "Your profile indicates that you are currently married. "
                "Are you asking about the strongest period around your existing marriage, "
                "a future relationship/commitment phase, or remarriage?"
            ),
        }

    if status in {"divorced", "widowed"} and marriage_timing_like:
        return {
            "action": "reinterpret",
            "relationship_status": status,
            "reason": "future_marriage_question_after_previous_marriage",
            "interpretation": "remarriage_timing",
        }

    if status == "engaged" and marriage_timing_like:
        return {
            "action": "reinterpret",
            "relationship_status": status,
            "reason": "engaged_user_marriage_timing",
            "interpretation": "wedding_or_formalisation_timing",
        }

    return {
        "action": "proceed",
        "relationship_status": status,
        "reason": "no_context_conflict",
    }
