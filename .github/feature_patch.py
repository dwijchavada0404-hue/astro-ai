from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"anchor not found: {label}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------
# Marriage Question Intelligence V3
# ---------------------------------------------------------

p = Path("app/astrology/features/marriage_question_intelligence_v3.py")
s = p.read_text(encoding="utf-8")

s = replace_once(
    s,
    '    "spouse_age_profile": (\n        "Spouse Age / Maturity Profile"\n    ),\n',
    '    "spouse_age_profile": (\n        "Spouse Age / Maturity Profile"\n    ),\n    "married_life_quality": (\n        "Married Life / Relationship Quality"\n    ),\n',
    "intelligence label",
)

helper = '''\n\n# =========================================================\n# MARRIED LIFE / RELATIONSHIP QUALITY DETECTION\n# =========================================================\n\ndef _detect_married_life_quality(question: str) -> dict[str, Any] | None:\n    # Keep explicit spouse-profile questions in their dedicated modules.\n    spouse_profile_terms = (\n        "spouse profession", "spouse career", "spouse education",\n        "spouse appearance", "spouse wealth", "spouse age",\n        "family background",\n    )\n    if any(term in question for term in spouse_profile_terms):\n        return None\n\n    patterns = (\n        (r"\\bmarried\\s+life\\b", "married life"),\n        (r"\\bmarital\\s+(?:harmony|quality|stability|relationship)\\b", "marital relationship quality"),\n        (r"\\bmarriage\\s+(?:be\\s+)?(?:happy|harmonious|stable|peaceful|supportive|passionate)\\b", "marriage quality"),\n        (r"\\bhappy\\s+marriage\\b", "happy marriage"),\n        (r"\\bharmonious\\s+marriage\\b", "harmonious marriage"),\n        (r"\\bstable\\s+marriage\\b", "stable marriage"),\n        (r"\\bmarriage\\s+last\\b", "marriage stability"),\n        (r"\\blong[- ]lasting\\s+marriage\\b", "marriage stability"),\n        (r"\\bpassionate\\s+marriage\\b", "passionate marriage"),\n        (r"\\bstrong\\s+chemistry\\b", "relationship chemistry"),\n        (r"\\bmarriage\\s+(?:have\\s+)?(?:ups\\s+and\\s+downs|conflict|challenges)\\b", "marriage variability"),\n        (r"\\bunconventional\\s+marriage\\b", "unconventional marriage"),\n        (r"\\brelationship\\s+(?:be\\s+)?(?:stable|harmonious|supportive|passionate)\\b", "relationship quality"),\n    )\n    matched = []\n    for pattern, label in patterns:\n        if re.search(pattern, question) and label not in matched:\n            matched.append(label)\n    if not matched:\n        return None\n    return {\n        "event": "married_life_quality",\n        "event_label": EVENT_LABELS["married_life_quality"],\n        "matched_keywords": matched,\n    }\n'''

s = replace_once(
    s,
    '\n# =========================================================\n# SPECIAL EVENT DETECTION\n# =========================================================\n',
    helper + '\n# =========================================================\n# SPECIAL EVENT DETECTION\n# =========================================================\n',
    "intelligence helper insertion",
)

s = replace_once(
    s,
    '    detected = []\n\n',
    '    detected = []\n\n    married_life_quality = _detect_married_life_quality(question)\n    if married_life_quality:\n        detected.append(married_life_quality)\n\n',
    "special event call",
)

s = replace_once(
    s,
    '        if (\n            "spouse_age_profile" in special_names\n            and event_name in ("spouse_traits", "general_marriage", "marriage_timing")\n        ):\n            continue\n',
    '        if (\n            "spouse_age_profile" in special_names\n            and event_name in ("spouse_traits", "general_marriage", "marriage_timing")\n        ):\n            continue\n\n        if (\n            "married_life_quality" in special_names\n            and event_name in ("general_marriage", "relationship_stability", "marriage_timing")\n        ):\n            continue\n',
    "base cleanup",
)

s = replace_once(
    s,
    '        if (\n            "spouse_age_profile" in names\n            and event_name == "spouse_traits"\n        ):\n            continue\n',
    '        if (\n            "spouse_age_profile" in names\n            and event_name == "spouse_traits"\n        ):\n            continue\n\n        if (\n            "married_life_quality" in names\n            and event_name in ("spouse_traits",)\n        ):\n            continue\n',
    "special conflict cleanup",
)

s = replace_once(
    s,
    '        "spouse_age_profile",\n        "spouse_profession",\n',
    '        "spouse_age_profile",\n        "married_life_quality",\n        "spouse_profession",\n',
    "comparison specific events",
)

# Priority tuple occurs later and intentionally gets a separate insertion.
priority_anchor = '        "spouse_family_background",\n        "spouse_education",\n'
if priority_anchor not in s:
    raise RuntimeError("anchor not found: priority")
s = s.replace(priority_anchor, '        "spouse_family_background",\n        "married_life_quality",\n        "spouse_education",\n', 1)

# Neutral/general-outlook question type for a qualitative relationship question.
s = replace_once(
    s,
    '    if primary_event in (\n        "spouse_traits",\n        "love_vs_arranged",\n    ):\n',
    '    if primary_event in (\n        "spouse_traits",\n        "love_vs_arranged",\n        "married_life_quality",\n    ):\n',
    "question type",
)

s = replace_once(
    s,
    '        "spouse_age_profile",\n        "love_vs_arranged",\n',
    '        "spouse_age_profile",\n        "married_life_quality",\n        "love_vs_arranged",\n',
    "direction neutral",
)

s = replace_once(
    s,
    '        "spouse_age_profile",\n        "love_marriage",\n',
    '        "spouse_age_profile",\n        "married_life_quality",\n        "love_marriage",\n',
    "confidence",
)

p.write_text(s, encoding="utf-8")


# ---------------------------------------------------------
# Marriage Forecast Router V3
# ---------------------------------------------------------

p = Path("app/astrology/features/marriage_forecast_router_v3.py")
s = p.read_text(encoding="utf-8")

s = replace_once(
    s,
    'from app.astrology.features.spouse_age_profile_reasoning_v2 import (\n    analyze_spouse_age_profile_v2,\n)\n',
    'from app.astrology.features.spouse_age_profile_reasoning_v2 import (\n    analyze_spouse_age_profile_v2,\n)\n\nfrom app.astrology.features.married_life_quality_reasoning_v2 import (\n    analyze_married_life_quality_v2,\n)\n',
    "router import",
)

s = replace_once(
    s,
    '    "spouse_age_profile": (\n        "Spouse Age / Maturity Profile"\n    ),\n',
    '    "spouse_age_profile": (\n        "Spouse Age / Maturity Profile"\n    ),\n    "married_life_quality": (\n        "Married Life / Relationship Quality"\n    ),\n',
    "router label",
)

route_fn = '''\n\n# =========================================================\n# MARRIED LIFE / RELATIONSHIP QUALITY ROUTE\n# =========================================================\n\ndef _route_married_life_quality(\n    chart: dict[str, Any],\n    question_analysis: dict[str, Any],\n    reference_moment: datetime,\n) -> dict[str, Any]:\n    intent = _safe_dict(question_analysis.get("intent"))\n    question = str(question_analysis.get("original_question", question_analysis.get("normalised_question", "")) or "")\n    analysis = analyze_married_life_quality_v2(chart, question)\n    result = {\n        "available": bool(analysis.get("available")),\n        "route": "natal_evidence",\n        "event": "married_life_quality",\n        "event_label": EVENT_LABELS["married_life_quality"],\n        "question_type": intent.get("question_type"),\n        "direction": intent.get("direction"),\n        "parser_confidence": intent.get("confidence"),\n        "reference_moment": reference_moment.isoformat(),\n        "evidence_engine": "married_life_quality_reasoning_v2",\n        "forecast_type": "natal_pattern",\n        "model_version": analysis.get("model_version"),\n        "question": analysis.get("question", question),\n        "normalised_question": analysis.get("normalised_question", str(question_analysis.get("normalised_question", "") or "")),\n        "target": analysis.get("target"),\n        "target_label": analysis.get("target_label"),\n        "matched_keywords": analysis.get("matched_keywords", []),\n        "requested_profile": analysis.get("requested_profile"),\n        "support_score": analysis.get("support_score"),\n        "support_level": analysis.get("support_level"),\n        "support_label": analysis.get("support_label"),\n        "confidence": analysis.get("confidence"),\n        "answer": analysis.get("answer"),\n        "summary": analysis.get("summary"),\n        "limitation": analysis.get("limitation"),\n        "strongest_themes": analysis.get("strongest_themes", []),\n        "evidence_count": analysis.get("evidence_count", 0),\n        "evidence": analysis.get("evidence", []),\n        "natal_profile": analysis.get("natal_profile", {}),\n        "analysis": analysis,\n    }\n    if not analysis.get("available"):\n        result["reason"] = analysis.get("reason")\n    return result\n'''

s = replace_once(
    s,
    '\n# =========================================================\n# SPOUSE PROFESSION TARGET DETECTION\n# =========================================================\n',
    route_fn + '\n# =========================================================\n# SPOUSE PROFESSION TARGET DETECTION\n# =========================================================\n',
    "route function",
)

s = replace_once(
    s,
    '    elif inherited_event == (\n        "spouse_family_background"\n    ):\n\n        result = _route_spouse_family_background(chart, inherited_analysis, reference_moment)\n',
    '    elif inherited_event == (\n        "spouse_family_background"\n    ):\n\n        result = _route_spouse_family_background(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "married_life_quality"\n    ):\n\n        result = _route_married_life_quality(chart, inherited_analysis, reference_moment)\n',
    "follow up dispatch",
)

s = replace_once(
    s,
    '    if query_mode == "single_event" and event_name == "spouse_family_background":\n        return _route_spouse_family_background(chart, question_analysis, reference_moment)\n',
    '    if query_mode == "single_event" and event_name == "spouse_family_background":\n        return _route_spouse_family_background(chart, question_analysis, reference_moment)\n\n    # -----------------------------------------------------\n    # MARRIED LIFE / RELATIONSHIP QUALITY\n    # -----------------------------------------------------\n\n    if query_mode == "single_event" and event_name == "married_life_quality":\n        return _route_married_life_quality(chart, question_analysis, reference_moment)\n',
    "main dispatch",
)

p.write_text(s, encoding="utf-8")
