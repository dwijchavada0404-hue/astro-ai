from __future__ import annotations

from typing import Any


MILESTONE_STATES = ("unknown", "likely_pending", "user_confirmed_achieved")
STATE_RANK = {state: index for index, state in enumerate(MILESTONE_STATES)}

MILESTONE_LABELS = {
    "career_stability": "career stability",
    "financial_stability": "financial stability",
    "committed_relationship": "committed relationship / marriage",
    "home_property": "home / property",
    "family_parenting": "family / parenting",
    "location_settlement": "location / geographic settlement",
}

DOMAIN_MILESTONES = {
    "career": ("career_stability",),
    "finance": ("financial_stability",),
    "marriage": ("committed_relationship",),
    "property_home": ("home_property",),
    "family_children": ("family_parenting",),
    "location_settlement": ("location_settlement",),
    "life_settlement": tuple(MILESTONE_LABELS),
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def normalize_life_context_v1(context: Any) -> dict[str, Any]:
    """Validate and normalize user-supplied milestone reality state."""
    if context is None:
        return {"available": False, "model_version": "v1", "milestones": {}, "confirmed_achieved": [], "likely_pending": [], "unknown": []}
    if not isinstance(context, dict):
        raise ValueError("life_context must be a dictionary when provided.")
    raw_milestones = context.get("milestones", {})
    if not isinstance(raw_milestones, dict):
        raise ValueError("life_context.milestones must be a dictionary.")
    normalized: dict[str, dict[str, Any]] = {}
    for milestone, raw in raw_milestones.items():
        if milestone not in MILESTONE_LABELS:
            raise ValueError(f"Unsupported life milestone: {milestone}.")
        item = {"state": raw} if isinstance(raw, str) else dict(raw) if isinstance(raw, dict) else None
        if item is None:
            raise ValueError(f"Milestone {milestone} must be a state string or dictionary.")
        state = item.get("state", "unknown")
        if state not in MILESTONE_STATES:
            raise ValueError(f"Milestone {milestone} state must be one of: {', '.join(MILESTONE_STATES)}.")
        normalized_item: dict[str, Any] = {"state": state, "label": MILESTONE_LABELS[milestone]}
        if isinstance(item.get("achieved_date"), str) and item["achieved_date"].strip():
            normalized_item["achieved_date"] = item["achieved_date"].strip()
        if isinstance(item.get("note"), str) and item["note"].strip():
            normalized_item["note"] = item["note"].strip()
        normalized[milestone] = normalized_item
    return {
        "available": bool(normalized), "model_version": "v1", "milestones": normalized,
        "confirmed_achieved": [key for key, item in normalized.items() if item["state"] == "user_confirmed_achieved"],
        "likely_pending": [key for key, item in normalized.items() if item["state"] == "likely_pending"],
        "unknown": [key for key, item in normalized.items() if item["state"] == "unknown"],
    }


def merge_life_context_v1(current: Any, updates: Any) -> dict[str, Any]:
    base = normalize_life_context_v1(current)
    incoming = normalize_life_context_v1(updates)
    if not incoming.get("available"):
        return base
    merged = {key: dict(value) for key, value in _safe_dict(base.get("milestones")).items()}
    for milestone, update in _safe_dict(incoming.get("milestones")).items():
        previous = merged.get(milestone, {"state": "unknown", "label": MILESTONE_LABELS[milestone]})
        old_state = str(previous.get("state") or "unknown")
        new_state = str(update.get("state") or "unknown")
        if STATE_RANK[new_state] < STATE_RANK[old_state]:
            raise ValueError(f"Milestone {milestone} cannot move backward from {old_state} to {new_state}.")
        next_item = dict(previous); next_item["state"] = new_state; next_item["label"] = MILESTONE_LABELS[milestone]
        if "achieved_date" in update: next_item["achieved_date"] = update["achieved_date"]
        if "note" in update: next_item["note"] = update["note"]
        merged[milestone] = next_item
    return normalize_life_context_v1({"milestones": merged})


def _context_status_for_domain(domain: str | None, context: dict[str, Any]) -> dict[str, Any]:
    relevant = DOMAIN_MILESTONES.get(str(domain), ())
    milestones = _safe_dict(context.get("milestones"))
    states = {key: milestones[key] for key in relevant if key in milestones}
    achieved = [key for key, item in states.items() if item.get("state") == "user_confirmed_achieved"]
    pending = [key for key, item in states.items() if item.get("state") == "likely_pending"]
    unknown = [key for key, item in states.items() if item.get("state") == "unknown"]
    return {"relevant_milestones": states, "confirmed_achieved": achieved, "likely_pending": pending, "unknown": unknown}


def reconcile_answer_with_life_context_v1(routed_result: dict[str, Any], context: Any) -> dict[str, Any]:
    if not isinstance(routed_result, dict):
        raise ValueError("routed_result must be a dictionary.")
    normalized = normalize_life_context_v1(context)
    if not normalized.get("available"):
        return routed_result
    result = dict(routed_result); domain = result.get("domain"); status = _context_status_for_domain(domain, normalized); achieved = status["confirmed_achieved"]
    reconciliation = {
        "applied": bool(achieved), "domain": domain, "status": status,
        "rule": "Only user_confirmed_achieved milestones override predictive assumptions. likely_pending is not a confirmed fact, and astrology cannot promote a milestone to achieved.",
    }
    if achieved:
        labels = [MILESTONE_LABELS[key] for key in achieved]
        prefix = "Reality override: your supplied context confirms " + ", ".join(labels) + " as already achieved. Astrology for these milestones is therefore interpreted historically or contextually, not as a prediction that they still need to occur. "
        answer = result.get("answer") or result.get("reason")
        result["answer"] = prefix + answer if isinstance(answer, str) and answer.strip() else prefix.strip()
    if domain == "life_settlement":
        supplied = status["relevant_milestones"]; total = len(supplied); achieved_count = len(status["confirmed_achieved"]); pending_count = len(status["likely_pending"]); unknown_count = len(status["unknown"])
        broad_status = "no_milestone_context" if total == 0 else "all_supplied_milestones_confirmed_achieved" if achieved_count == total else "partially_confirmed_achieved" if achieved_count else "supplied_milestones_not_confirmed_achieved" if pending_count else "supplied_milestones_unknown"
        reconciliation["life_settlement_context"] = {"status": broad_status, "supplied_count": total, "confirmed_achieved_count": achieved_count, "likely_pending_count": pending_count, "unknown_count": unknown_count}
    result["life_context"] = normalized; result["reality_reconciliation"] = reconciliation
    return result
