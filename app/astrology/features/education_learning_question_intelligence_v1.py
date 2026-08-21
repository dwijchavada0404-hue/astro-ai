from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "admission_enrolment": (
        "get admission", "admission", "enrol", "enroll", "college admission", "university admission",
        "get into college", "get into university",
    ),
    "exam_assessment": (
        "exam", "examination", "test", "assessment", "clear exam", "pass exam", "exam result", "score marks",
    ),
    "higher_study_transition": (
        "higher studies", "higher education", "masters", "master's", "postgraduate", "post graduate", "phd", "doctorate",
        "study further", "further studies",
    ),
    "skill_certification": (
        "certification", "certificate", "professional course", "skill course", "learn a skill", "upskill", "reskill", "licence exam", "license exam",
    ),
    "research_deep_study": (
        "research", "deep study", "thesis", "dissertation", "academic research", "research degree",
    ),
    "education_overview": (
        "education future", "education overview", "education prospects", "learning future", "learning overview", "study prospects",
        "tell me about my education", "tell me about my studies", "education and learning",
    ),
    "education_timing": (
        "when", "what year", "which year", "best period", "strongest period", "education timing", "study timing", "learning timing",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_education_learning_question_v1(question: str) -> dict[str, Any]:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    q = _normalise(question)
    matched: dict[str, list[str]] = {}
    scores: dict[str, int] = {}
    for intent, phrases in INTENTS.items():
        hits = [phrase for phrase in phrases if phrase in q]
        if hits:
            matched[intent] = hits
            scores[intent] = len(hits)

    timing_requested = "education_timing" in matched
    substantive = {key: value for key, value in scores.items() if key != "education_timing"}
    priority = [
        "admission_enrolment", "exam_assessment", "higher_study_transition", "skill_certification",
        "research_deep_study", "education_overview",
    ]
    primary = "unknown"
    if substantive:
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("educat", "study", "studies", "learn", "college", "university", "exam", "course", "research")):
        primary = "education_timing"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "education_learning" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "safety": {
            "education_fact_inference_allowed": False,
            "admission_guarantee_allowed": False,
            "exam_result_prediction_allowed": False,
            "credential_guarantee_allowed": False,
            "employment_outcome_guarantee_allowed": False,
        },
    }
