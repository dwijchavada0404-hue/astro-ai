from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Literal

AnswerLanguage = Literal["hinglish", "english", "hindi"]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _period(value: Any) -> dict[str, Any]:
    value = _dict(value)
    return _dict(value.get("strongest_period") or value.get("strongest_window") or value.get("active_period") or value.get("timing_period") or value)


def _month(value: Any) -> str | None:
    if not value: return None
    try:
        dt = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%b %Y")
    except (TypeError, ValueError): return None


def _range(period: dict[str, Any]) -> str | None:
    start, end = _month(period.get("start")), _month(period.get("end"))
    if start and end: return start if start == end else f"{start} – {end}"
    return start or end


def _deep_result(routed: dict[str, Any]) -> dict[str, Any]: return _dict(routed.get("result"))


def _timing_period(result: dict[str, Any], direction: str) -> dict[str, Any]:
    for container_key in ("timing", "event_intelligence", "synthesis"):
        candidate = _period(_dict(result.get(container_key)).get(direction))
        if candidate: return candidate
    candidate = _period(result.get(direction))
    if candidate: return candidate
    return _period(_dict(result.get("event_result")).get(direction))


def _marriage_period(result: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    for candidate in (result, _dict(result.get("forecast")), _dict(result.get("timing")), _dict(result.get("result"))):
        window = _dict(candidate.get("strongest_window") or candidate.get("strongest_period") or candidate.get("best_window") or candidate.get("primary_window"))
        if window:
            return window, _month(window.get("peak") or window.get("peak_date") or candidate.get("peak_activation"))
        future = _period(candidate.get("future"))
        if future: return future, _month(candidate.get("peak_activation"))
    return {}, None


def _love_arranged(raw: str, language: AnswerLanguage) -> str | None:
    lower = raw.lower()
    if not any(token in lower for token in ("love marriage", "arranged", "hybrid pathway", "family-mediated")): return None
    arranged_match = re.search(r"arranged(?:/family-mediated)? marriage[^\d]{0,40}(\d+(?:\.\d+)?)%", raw, re.I)
    love_match = re.search(r"love marriage[^\d]{0,40}(\d+(?:\.\d+)?)%", raw, re.I)
    arranged = float(arranged_match.group(1)) if arranged_match else None
    love = float(love_match.group(1)) if love_match else None
    mixed = "mixed" in lower or "hybrid" in lower or (arranged is not None and 40 <= arranged <= 60)
    if mixed:
        return {
            "hinglish": "Aapki kundli ek pure love ya pure arranged marriage ki taraf strongly point nahi karti. Zyada possibility aisi lagti hai ki rishta personal choice aur family involvement dono se develop ho — yani love-cum-arranged type ka pattern. Family ka role rahega, lekin final connection mein aapki apni choice bhi important dikh rahi hai.",
            "english": "Your chart does not strongly point to a purely love or purely arranged marriage. A blended path looks more likely: personal choice together with meaningful family involvement. In simple terms, it resembles a love-cum-arranged pattern rather than either extreme.",
            "hindi": "आपकी कुंडली पूरी तरह प्रेम विवाह या पूरी तरह अरेंज्ड विवाह की ओर मजबूत संकेत नहीं देती। अधिक संभावना ऐसे मिश्रित रास्ते की दिखती है जिसमें आपकी पसंद और परिवार की भागीदारी दोनों महत्वपूर्ण हों — यानी लव-कम-अरेंज्ड जैसा पैटर्न।",
        }[language]
    arranged_lean = arranged is not None and (love is None or arranged > love) or "arranged marriage leaning" in lower
    if arranged_lean:
        return {"hinglish":"Aapki kundli mein arranged marriage ya family ke through rishta aane ka pattern thoda stronger dikh raha hai. Lekin iska matlab ye nahi ki aapki choice nahi hogi — attraction aur personal comfort final decision mein important rahenge.","english":"Your chart leans somewhat more toward an arranged or family-facilitated marriage, while still leaving an important role for your own choice and attraction.","hindi":"आपकी कुंडली में अरेंज्ड या परिवार के माध्यम से रिश्ता आने का संकेत थोड़ा अधिक मजबूत है, लेकिन आपकी अपनी पसंद और आकर्षण भी महत्वपूर्ण रहेंगे।"}[language]
    return {"hinglish":"Aapki kundli mein love marriage ka pattern thoda stronger dikh raha hai. Rishta personal choice ya pehle se bane emotional connection se develop ho sakta hai, halanki family involvement baad mein important reh sakta hai.","english":"Your chart leans somewhat more toward a love marriage or a relationship developing through personal choice, although family involvement can still become important later.","hindi":"आपकी कुंडली में प्रेम विवाह का संकेत थोड़ा अधिक मजबूत है। रिश्ता आपकी पसंद या पहले से बने भावनात्मक संबंध से विकसित हो सकता है, हालांकि परिवार की भूमिका बाद में महत्वपूर्ण रह सकती है।"}[language]


def present_answer_v2(routed: dict[str, Any], language: AnswerLanguage = "hinglish") -> str | None:
    """Turn deterministic router evidence into natural copy without changing astrology calculations."""
    result = _deep_result(routed); domain = str(routed.get("domain") or ""); raw = routed.get("answer") or routed.get("reason")

    if domain == "marriage":
        if isinstance(raw, str):
            pathway = _love_arranged(raw, language)
            if pathway: return pathway
        period, peak = _marriage_period(result); window = _range(period)
        if window:
            peak_text = ""
            if peak: peak_text = {"hinglish":f" {peak} ke aas-paas indications aur strong ho sakte hain.","english":f" The indications look especially strong around {peak}.","hindi":f" {peak} के आसपास संकेत और अधिक मजबूत दिखाई देते हैं।"}[language]
            return {"hinglish":f"Aapki kundli mein shaadi ke liye {window} ka period sabse zyada supportive dikh raha hai.{peak_text} Is dauran relationship aur dasha ke signals ek saath stronger hote hain. Isse favourable window samjhein, fixed date nahi.","english":f"Your chart shows {window} as the most supportive period for marriage.{peak_text} Relationship indicators and dasha timing become stronger together in this phase. Treat it as a favourable window rather than a fixed date.","hindi":f"आपकी कुंडली में विवाह के लिए {window} का समय सबसे अधिक अनुकूल दिखाई देता है।{peak_text} इस दौरान संबंध और दशा के संकेत एक साथ मजबूत होते हैं। इसे अनुकूल समय मानें, निश्चित तारीख नहीं।"}[language]

    if domain == "property_home":
        past, future = _range(_timing_period(result, "past")), _range(_timing_period(result, "future"))
        if past and future:
            return {"hinglish":f"Aapke chart mein property/home ke liye ek strong past window {past} ke aas-paas thi. Agar us phase mein ghar ya property se judi koi important development hui ho, to woh chart ke timing se match karti hai. Aage {future} bhi property matters ke liye supportive dikh raha hai — zaroori nahi ki iska matlab first home ho; ye upgrade, investment, renovation ya next property phase bhi ho sakta hai.","english":f"Your chart shows a strong past property/home window around {past}. If an important home or property development happened then, it fits the chart's timing. Looking ahead, {future} is also supportive for property matters; that does not have to mean a first home and could instead relate to an upgrade, investment, renovation or another property phase.","hindi":f"आपकी कुंडली में घर या संपत्ति के लिए {past} के आसपास एक मजबूत पिछला समय दिखाई देता है। यदि उस समय कोई महत्वपूर्ण घर या संपत्ति संबंधी घटना हुई हो, तो वह इस टाइमिंग से मेल खाती है। आगे {future} भी संपत्ति से जुड़े मामलों के लिए अनुकूल है; इसका अर्थ केवल पहला घर नहीं, बल्कि अपग्रेड, निवेश, नवीनीकरण या अगली संपत्ति भी हो सकता है।"}[language]
        if future:
            return {"hinglish":f"Aapke chart mein property ya ghar se jude matters ke liye {future} ka period zyada supportive dikh raha hai. Ye first purchase ki guarantee nahi, balki property-related opportunity ka stronger phase hai.","english":f"Your chart shows {future} as a more supportive period for home or property matters. It is not a guarantee of a first purchase, but a stronger property-related opportunity phase.","hindi":f"आपकी कुंडली में घर या संपत्ति से जुड़े मामलों के लिए {future} का समय अधिक अनुकूल दिखाई देता है। यह पहली खरीद की गारंटी नहीं, बल्कि संपत्ति संबंधी अवसरों का मजबूत चरण है।"}[language]

    if domain == "family_children":
        past, future = _range(_timing_period(result, "past")), _range(_timing_period(result, "future"))
        if future:
            past_text = {"hinglish":f" Isse pehle {past} bhi family/parenting themes ke liye strong raha tha." if past else "","english":f" An earlier strong family/parenting phase was {past}." if past else "","hindi":f" इससे पहले {past} भी परिवार/पालन-पोषण के विषयों के लिए मजबूत समय था।" if past else ""}[language]
            return {"hinglish":f"Family aur parenting ke perspective se {future} aapke chart ka comparatively stronger upcoming period dikh raha hai.{past_text} Isse conception ya childbirth ki fixed prediction na samjhein; astrology yahan family growth aur parenting-related timing themes dikha rahi hai.","english":f"From a family and parenting perspective, {future} is the comparatively stronger upcoming period in your chart.{past_text} This should not be read as a fixed prediction of conception or childbirth; it reflects stronger family-growth and parenting timing themes.","hindi":f"परिवार और पालन-पोषण के दृष्टिकोण से {future} आपकी कुंडली में तुलनात्मक रूप से अधिक मजबूत आगामी समय है।{past_text} इसे गर्भधारण या बच्चे के जन्म की निश्चित भविष्यवाणी न मानें; यह परिवार-वृद्धि और पालन-पोषण से जुड़े मजबूत समय संकेत हैं।"}[language]

    if domain in {"location_settlement", "travel_journeys"}:
        future = _range(_timing_period(result, "future"))
        if future:
            return {"hinglish":f"Foreign travel ya overseas exposure ke liye {future} ka period aapke chart mein comparatively stronger dikh raha hai. Is dauran travel, long-distance movement aur foreign connection ke signals zyada active hote hain. Ye opportunity ka period hai, travel ya visa ki guarantee nahi.","english":f"Your chart shows {future} as a comparatively stronger period for foreign travel or overseas exposure. Travel, long-distance movement and foreign-connection indicators are more active in this phase. It suggests opportunity, not a guarantee of travel or visa approval.","hindi":f"विदेश यात्रा या विदेशी अवसरों के लिए {future} का समय आपकी कुंडली में तुलनात्मक रूप से अधिक मजबूत दिखाई देता है। इस दौरान यात्रा, लंबी दूरी और विदेशी संपर्क के संकेत अधिक सक्रिय रहते हैं। यह अवसर का संकेत है, यात्रा या वीज़ा की गारंटी नहीं।"}[language]

    if isinstance(raw, str) and raw.strip():
        return re.sub(r"\b(\d{4}-\d{2}-\d{2})(?:T[^\s,.;)]*)?\b", lambda m: _month(m.group(1)) or m.group(0), raw.strip())
    return None
