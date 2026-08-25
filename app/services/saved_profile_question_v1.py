from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from app.models.chart import BirthInput
from app.services.chart_service import build_chart
from app.services.unified_question_service_v1 import answer_unified_question_v1
from app.storage.profile_store_v1 import ProfileStoreV1


def _resolve_profile(store: ProfileStoreV1, user_id: str, profile_id: str | None) -> dict[str, Any]:
    if profile_id:
        profile = store.get_birth_profile(user_id, profile_id)
        if profile is None:
            raise LookupError("Birth profile not found.")
        return profile

    profiles = store.list_birth_profiles(user_id)
    if not profiles:
        raise LookupError("No saved birth profile is available for this user.")
    default_profile = next((item for item in profiles if item.get("is_default")), None)
    return default_profile or profiles[0]


def _birth_input_from_profile(profile: dict[str, Any]) -> BirthInput:
    try:
        return BirthInput(
            date=date.fromisoformat(str(profile["birth_date"])),
            time=time.fromisoformat(str(profile["birth_time"])),
            place=str(profile["place"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Saved birth profile contains invalid birth data.") from exc


def answer_saved_profile_question_v1(
    store: ProfileStoreV1,
    user_id: str,
    question: str,
    reference_moment: datetime,
    *,
    profile_id: str | None = None,
    life_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Answer a unified AstroAI question using an authenticated user's saved birth profile."""
    if not user_id.strip():
        raise ValueError("user_id must not be empty.")

    profile = _resolve_profile(store, user_id, profile_id)
    birth_input = _birth_input_from_profile(profile)
    chart = build_chart(birth_input)
    response = answer_unified_question_v1(
        chart,
        question,
        reference_moment,
        life_context=life_context,
    )
    routed = response.get("result", {}) if isinstance(response, dict) else {}
    next_life_context = routed.get("life_context") or life_context

    return {
        **response,
        "birth": chart.get("birth", {}),
        "birth_profile": {
            "profile_id": profile.get("profile_id"),
            "label": profile.get("label"),
            "is_default": bool(profile.get("is_default")),
        },
        "birth_source": "saved_profile",
        "life_context": routed.get("life_context"),
        "next_life_context": next_life_context,
        "reality_reconciliation": routed.get("reality_reconciliation"),
    }
