from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

AnswerLanguage = Literal["hinglish", "english", "hindi"]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _period(value: Any) -> dict[str, Any]:
    value = _dict(value)
    return _dict(value.get("strongest_period") or value.get("active_period") or value.get("timing_period") or value)


def _month(value: Any) -> str | None:
    if not value:
        return None
    try:
        dt = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%b %Y")
    except (TypeError, ValueError):
        return None


def _range(period: dict[str, Any]) -> str | None:
    start, end = _month(period.get("start")), _month(period.get("end"))
    if start and end:
        return start if start == end else f"{start} – {end}"
    return start or end


def _deep_result(routed: dict[str, Any]) -> dict[str, Any]:
    return _dict(routed.get("result"))


def _future_period(result: dict[str, Any]) -> dict[str, Any]:
    for container_key in ("timing", "event_intelligence", "synthesis"):
        container = _dict(result.get(container_key))
        candidate = _period(container.get("future"))
        if candidate:
            return candidate
    candidate = _period(result.get("future"))
    if candidate:
        return candidate
    event_result = _dict(result.get("event_result"))
    return _period(event_result.get("future"))


def _marriage_period(result: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    candidates = [result, _dict(result.get("forecast")), _dict(result.get("timing")), _dict(result.get("result"))]
    for candidate in candidates:
        window = _dict(candidate.get("strongest_window") or candidate.get("strongest_period") or candidate.get("best_window"))
        if window:
            peak = _month(window.get("peak") or window.get("peak_date") or candidate.get("peak_activation"))
            return window, peak
        future = _period(candidate.get("future"))
        if future:
            return future, _month(candidate.get("peak_activation"))
    return {}, None


def _copy(language: AnswerLanguage, key: str, **values: str) -> str:
    templates = {
        "marriage": {
            "hinglish": "Aapki kundli mein shaadi ke liye {window} ka period sabse zyada supportive dikh raha hai.{peak} Is dauran relationship aur dasha ke signals ek saath stronger hote hain. Isse ek favourable window samjhein, fixed ya guaranteed date nahi.",
            "english": "Your chart shows {window} as the most supportive period for marriage.{peak} Relationship indicators and dasha timing become stronger together in this phase. Treat this as a favourable window rather than a fixed or guaranteed date.",
            "hindi": "आपकी कुंडली में विवाह के लिए {window} का समय सबसे अधिक अनुकूल दिखाई देता है।{peak} इस दौरान संबंध और दशा के संकेत एक साथ मजबूत होते हैं। इसे अनुकूल समय मानें, निश्चित या गारंटीकृत तारीख नहीं।",
        },
        "property_home": {
            "hinglish": "Aapke chart mein property ya apna ghar lene ke liye {window} ka period zyada supportive dikh raha hai. Is phase mein home/property se jude dasha signals comparatively stronger hain. Purchase isi period mein hona guaranteed nahi hai, lekin astrology ke hisaab se ye ek important window hai.",
            "english": "Your chart shows {window} as a more supportive period for buying property or establishing your own home. Home and property-related dasha indicators are comparatively stronger in this phase. A purchase is not guaranteed, but astrologically this is an important window to watch.",
            "hindi": "आपकी कुंडली में संपत्ति या अपना घर लेने के लिए {window} का समय अधिक अनुकूल दिखाई देता है। इस चरण में घर और संपत्ति से जुड़े दशा संकेत तुलनात्मक रूप से मजबूत हैं। खरीद की गारंटी नहीं है, लेकिन ज्योतिषीय रूप से यह महत्वपूर्ण समय है।",
        },
        "location_settlement": {
            "hinglish": "Foreign travel ya overseas exposure ke liye {window} ka period aapke chart mein comparatively stronger dikh raha hai. Is dauran travel, long-distance movement aur foreign connection ke signals zyada active hote hain. Ye opportunity ka period hai, travel ya visa ki guarantee nahi.",
            "english": "Your chart shows {window} as a comparatively stronger period for foreign travel or overseas exposure. Travel, long-distance movement and foreign-connection indicators are more active in this phase. It suggests opportunity, not a guarantee of travel or visa approval.",
            "hindi": "विदेश यात्रा या विदेशी अवसरों के लिए {window} का समय आपकी कुंडली में तुलनात्मक रूप से अधिक मजबूत दिखाई देता है। इस दौरान यात्रा, लंबी दूरी और विदेशी संपर्क के संकेत अधिक सक्रिय रहते हैं। यह अवसर का संकेत है, यात्रा या वीज़ा की गारंटी नहीं।",
        },
        "generic": {
            "hinglish": "Aapke chart ke hisaab se {answer}",
            "english": "Based on your chart, {answer}",
            "hindi": "आपकी कुंडली के अनुसार, {answer}",
        },
    }
    return templates[key][language].format(**values)


def present_answer_v2(routed: dict[str, Any], language: AnswerLanguage = "hinglish") -> str | None:
    """Turn deterministic router evidence into user-facing copy without changing calculations."""
    result = _deep_result(routed)
    domain = str(routed.get("domain") or "")
    raw = routed.get("answer") or routed.get("reason")

    if domain == "marriage":
        period, peak = _marriage_period(result)
        window = _range(period)
        if window:
            peak_text = ""
            if peak:
                peak_text = {
                    "hinglish": f" {peak} ke aas-paas indications aur strong ho sakte hain.",
                    "english": f" The indications look especially strong around {peak}.",
                    "hindi": f" {peak} के आसपास संकेत और अधिक मजबूत दिखाई देते हैं।",
                }[language]
            return _copy(language, "marriage", window=window, peak=peak_text)

    if domain == "property_home":
        window = _range(_future_period(result))
        if window:
            return _copy(language, "property_home", window=window)

    if domain in {"location_settlement", "travel_journeys"}:
        window = _range(_future_period(result))
        if window:
            return _copy(language, "location_settlement", window=window)

    if isinstance(raw, str) and raw.strip():
        # Preserve mature domain output when no safe evidence-aware V2 template exists.
        # Date cleanup still keeps exact engine values in payload while making prose readable.
        cleaned = raw.strip()
        import re
        cleaned = re.sub(r"\b(\d{4}-\d{2}-\d{2})(?:T[^\s,.;)]*)?\b", lambda m: _month(m.group(1)) or m.group(0), cleaned)
        return cleaned
    return None
