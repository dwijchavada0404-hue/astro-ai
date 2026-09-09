from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.top_level_question_router_v1 import route_top_level_question_v1
from app.services.answer_experience_v2 import AnswerLanguage, present_answer_v2
from app.services.question_language_aliases_v1 import normalize_question_for_routing_v1


MAX_QUESTION_LENGTH = 1000
API_CONTRACT_VERSION = "v1"


def _validate_reference_moment(reference_moment: datetime) -> None:
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")


def _validate_question(question: str) -> str:
    if not isinstance(question, str):
        raise ValueError("question must be a string.")
    cleaned = " ".join(question.strip().split())
    if not cleaned:
        raise ValueError("question must not be empty.")
    if len(cleaned) > MAX_QUESTION_LENGTH:
        raise ValueError(f"question must not exceed {MAX_QUESTION_LENGTH} characters.")
    return cleaned


def _validate_chart(chart: dict[str, Any]) -> None:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not chart:
        raise ValueError("chart must not be empty.")


def _validate_life_context(life_context: dict[str, Any] | None) -> None:
    if life_context is not None and not isinstance(life_context, dict):
        raise ValueError("life_context must be a dictionary when provided.")


def _nonempty_text(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _month(value: Any) -> str | None:
    if not value:
        return None
    try:
        dt = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%b %Y")
    except (TypeError, ValueError):
        return None


def _period_range(period: Any) -> str | None:
    if not isinstance(period, dict):
        return None
    start, end = _month(period.get("start")), _month(period.get("end"))
    if start and end:
        return start if start == end else f"{start} – {end}"
    return start or end


def _career_event_narrative(routed: dict[str, Any], language: AnswerLanguage) -> str | None:
    """Answer career-event timing directly from deterministic event windows."""
    if routed.get("domain") != "career":
        return None
    result = routed.get("result") if isinstance(routed.get("result"), dict) else {}
    intent = str(result.get("primary_intent") or "")
    if intent not in {"job_change", "new_job", "promotion", "foreign_work"}:
        return None
    event_result = result.get("event_result") if isinstance(result.get("event_result"), dict) else {}
    future = event_result.get("future") if isinstance(event_result.get("future"), dict) else {}
    period = future.get("event_specific_period") or future.get("career_timing_period")
    window = _period_range(period)
    if not window:
        return None

    labels = {
        "job_change": ("job change", "job change", "नौकरी बदलने"),
        "new_job": ("new job", "new job", "नई नौकरी"),
        "promotion": ("promotion", "promotion", "प्रमोशन"),
        "foreign_work": ("foreign/MNC work", "foreign or international work", "विदेशी या अंतरराष्ट्रीय काम"),
    }
    hinglish_label, english_label, hindi_label = labels[intent]
    return {
        "hinglish": (
            f"Aapki kundli mein {hinglish_label} ke liye {window} ka period comparatively sabse strong dikh raha hai. "
            "Is phase mein professional transition aur career movement ke signals zyada active hote hain, isliye interviews, offers ya role/company change ki movement isi window ke aas-paas stronger ho sakti hai. "
            "Isse favourable timing samjhein, fixed guarantee nahi."
        ),
        "english": (
            f"Your chart shows {window} as the comparatively strongest upcoming period for a {english_label}. "
            "Professional-transition and career-movement indicators are more active in this phase, so interviews, offers or a role/company change may gain momentum around this window. "
            "Treat it as favourable timing rather than a fixed guarantee."
        ),
        "hindi": (
            f"आपकी कुंडली में {hindi_label} के लिए {window} का समय तुलनात्मक रूप से सबसे मजबूत दिखाई देता है। "
            "इस चरण में पेशेवर बदलाव और करियर मूवमेंट के संकेत अधिक सक्रिय रहते हैं, इसलिए इंटरव्यू, ऑफर या भूमिका/कंपनी बदलने की प्रक्रिया इस समय के आसपास तेज हो सकती है। "
            "इसे अनुकूल समय मानें, निश्चित गारंटी नहीं।"
        ),
    }[language]


def _fallback_narrative(routed: dict[str, Any], language: AnswerLanguage) -> str:
    """Guarantee that an API response never persists a null assistant narrative."""
    result = routed.get("result") if isinstance(routed.get("result"), dict) else {}
    direct = _nonempty_text(
        routed.get("answer"),
        routed.get("reason"),
        result.get("answer"),
        result.get("summary"),
        result.get("reason"),
    )
    if direct:
        return direct

    domain = str(routed.get("domain") or "")
    messages = {
        "hinglish": {
            "marriage": "Is sawaal ke liye chart signals mil rahe hain, lekin current calculation se reliable marriage conclusion complete nahi ho paaya. Main incomplete ya invented prediction dene ke bajay is reading ko dobara calculate karne ki zarurat bata raha hoon.",
            "family_children": "Is sawaal ke liye family/parenting signals mil rahe hain, lekin current calculation se reliable timing window complete nahi ho paayi. Main incomplete ya invented date dene ke bajay is reading ko dobara calculate karne ki zarurat bata raha hoon.",
            "default": "Chart analysis complete hua, lekin is request ke liye reliable narrative generate nahi ho paaya. Incomplete ya invented prediction dikhane ke bajay AstroAI is reading ko unavailable mark kar raha hai.",
        },
        "english": {
            "marriage": "The chart signals were found, but the current calculation could not complete a reliable marriage conclusion. Rather than inventing a prediction, this reading needs to be recalculated.",
            "family_children": "The family/parenting signals were found, but the current calculation could not complete a reliable timing window. Rather than inventing a date, this reading needs to be recalculated.",
            "default": "The chart analysis completed, but a reliable narrative could not be generated for this request. AstroAI is marking the reading unavailable rather than inventing a prediction.",
        },
        "hindi": {
            "marriage": "कुंडली में संकेत मिले हैं, लेकिन वर्तमान गणना विश्वसनीय विवाह निष्कर्ष पूरा नहीं कर पाई। अनुमान गढ़ने के बजाय इस रीडिंग की दोबारा गणना आवश्यक है।",
            "family_children": "परिवार और पालन-पोषण के संकेत मिले हैं, लेकिन वर्तमान गणना विश्वसनीय समय-सीमा पूरी नहीं कर पाई। कोई तारीख गढ़ने के बजाय इस रीडिंग की दोबारा गणना आवश्यक है।",
            "default": "कुंडली का विश्लेषण पूरा हुआ, लेकिन इस प्रश्न के लिए विश्वसनीय उत्तर तैयार नहीं हो पाया। अनुमान गढ़ने के बजाय AstroAI इस रीडिंग को अनुपलब्ध बता रहा है।",
        },
    }
    selected = messages[language]
    return selected.get(domain, selected["default"])


def answer_unified_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
    life_context: dict[str, Any] | None = None,
    answer_language: AnswerLanguage = "hinglish",
) -> dict[str, Any]:
    """Production-facing service contract with deterministic routing and natural presentation."""
    _validate_chart(chart)
    cleaned_question = _validate_question(question)
    _validate_reference_moment(reference_moment)
    _validate_life_context(life_context)

    routing_question = normalize_question_for_routing_v1(cleaned_question)
    routed = route_top_level_question_v1(
        chart,
        routing_question,
        reference_moment,
        life_context=life_context,
    )
    if not isinstance(routed, dict):
        raise RuntimeError("Top-level question router returned an invalid response.")

    available = bool(routed.get("available"))
    domain = routed.get("domain")
    route = routed.get("route") or "unsupported"

    # Presentation can synthesize a natural answer from structured engine output.
    # Career-event timing is handled first so internal score/methodology copy can
    # never leak as the primary response to questions such as job-change timing.
    career_presented = _career_event_narrative(routed, answer_language) if available else None
    presented = present_answer_v2(routed, answer_language) if available else None
    answer = _nonempty_text(career_presented, presented, routed.get("answer"), routed.get("reason"))
    if answer is None:
        answer = _fallback_narrative(routed, answer_language)

    status = "answered" if available else "unsupported"
    return {
        "api_contract_version": API_CONTRACT_VERSION,
        "status": status,
        "question": cleaned_question,
        "reference_moment": reference_moment.isoformat(),
        "domain": domain,
        "route": route,
        "answer": answer,
        "answer_language": answer_language,
        "limitation": routed.get("limitation"),
        "result": routed,
        "meta": {
            "deterministic_router": True,
            "answer_experience": "v2",
            "reality_override_enabled": life_context is not None,
            "guaranteed_outcome": False,
            "routing_alias_applied": routing_question != cleaned_question,
        },
    }
