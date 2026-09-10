from __future__ import annotations

import re


def normalize_question_for_routing_v1(question: str) -> str:
    """Map common Roman-Hindi/Hinglish phrasing to router-friendly English.

    The original user question remains untouched for display/storage. This helper
    only improves deterministic intent routing; it does not generate an answer.
    """
    q = " ".join(question.strip().lower().split())

    # Marriage pathway questions.
    has_love = "love marriage" in q
    has_arranged = "arranged marriage" in q or "arrange marriage" in q
    if has_love and has_arranged:
        return "love marriage or arranged marriage"

    # Marriage timing: meri/mera shaadi kab hogi, shaadi kab hogi, etc.
    if ("shaadi" in q or "shadi" in q) and any(token in q for token in ("kab", "when")):
        return "when will i get married"

    child_tokens = (
        "bacha", "baccha", "bachcha", "bachha", "bache", "bacche", "bachche",
        "baby", "child", "children", "kid", "kids",
    )

    # Child-count questions are a Family & Children request, not a marriage
    # event. The family engine deliberately does not claim an exact future
    # child count, but routing it correctly lets the presentation layer explain
    # that boundary naturally instead of leaking an unrelated engine fallback.
    count_tokens = ("kitne", "kitni", "how many", "number of")
    if any(token in q for token in child_tokens) and any(token in q for token in count_tokens):
        return "how many children will i have"

    # Children timing: mera pehla bacha kab hoga / baccha / bachcha / baby.
    if any(token in q for token in child_tokens) and any(token in q for token in ("kab", "when")):
        first = any(token in q for token in ("pehla", "pehli", "first", "1st"))
        return "when will i have my first child" if first else "when will i have children"

    # Common future-family wording without an explicit 'when'.
    if any(token in q for token in ("bacha hoga", "baccha hoga", "bachcha hoga", "baby hoga")):
        return "will i have children"

    # Keep ordinary English and already-supported wording unchanged.
    return question
