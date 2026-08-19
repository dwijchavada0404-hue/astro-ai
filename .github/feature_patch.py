from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing anchor: {label}")
    return text.replace(old, new, 1)


# ---------------- Intelligence V3 ----------------
p = Path("app/astrology/features/marriage_question_intelligence_v3.py")
s = p.read_text()

s = replace_once(s,
'''    "spouse_family_background": (\n        "Spouse Family / Social Background"\n    ),\n''',
'''    "spouse_family_background": (\n        "Spouse Family / Social Background"\n    ),\n    "spouse_age_profile": (\n        "Spouse Age / Maturity Profile"\n    ),\n''', "intelligence label")

marker = "# =========================================================\n# SPECIAL EVENT DETECTION\n# =========================================================\n"
detector = '''# =========================================================\n# SPOUSE AGE / MATURITY DETECTION\n# =========================================================\n\ndef _detect_spouse_age_profile(question: str) -> dict[str, Any] | None:\n    # Protect marriage-timing questions such as \"At what age will I get married?\".\n    if re.search(r"\\b(?:what|which)\\s+age\\b.{0,25}\\b(?:marry|married|marriage)\\b", question):\n        return None\n\n    spouse_context = (\n        "spouse", "future spouse", "partner", "future partner",\n        "husband", "wife", "person i marry", "person i will marry",\n    )\n    if not any(value in question for value in spouse_context):\n        return None\n\n    pattern_map = (\n        (r"\\bolder(?:\\s+than\\s+me)?\\b", "older spouse"),\n        (r"\\belder(?:\\s+than\\s+me)?\\b", "older spouse"),\n        (r"\\bmore\\s+mature(?:\\s+than\\s+me)?\\b", "more mature spouse"),\n        (r"\\byounger(?:\\s+than\\s+me)?\\b", "younger spouse"),\n        (r"\\byouthful\\b", "younger spouse"),\n        (r"\\b(?:same|similar)\\s+age\\b", "similar age spouse"),\n        (r"\\bclose\\s+in\\s+age\\b", "similar age spouse"),\n        (r"\\baround\\s+my\\s+age\\b", "similar age spouse"),\n        (r"\\bage\\s+(?:profile|difference|gap)\\b", "spouse age profile"),\n        (r"\\b(?:age|maturity)\\s+profile\\b", "spouse age profile"),\n    )\n    matched = []\n    for pattern, keyword in pattern_map:\n        if re.search(pattern, question) and keyword not in matched:\n            matched.append(keyword)\n    if not matched:\n        return None\n    return {\n        "event": "spouse_age_profile",\n        "event_label": EVENT_LABELS["spouse_age_profile"],\n        "matched_keywords": matched,\n    }\n\n\n'''
s = replace_once(s, marker, detector + marker, "intelligence detector location")

anchor = '''def _detect_special_events(\n    question: str,\n) -> list[dict[str, Any]]:\n\n    detected = []\n'''
replacement = anchor + '''\n    spouse_age_profile = _detect_spouse_age_profile(question)\n    if spouse_age_profile:\n        detected.append(spouse_age_profile)\n'''
s = replace_once(s, anchor, replacement, "special event hook")

for label in ("primary priority", "comparison specific events"):
    s = replace_once(s,
    '''        "spouse_family_background",\n        "spouse_profession",\n''',
    '''        "spouse_family_background",\n        "spouse_age_profile",\n        "spouse_profession",\n''', label)

s = replace_once(s,
'''    if primary_event in (\n        "spouse_traits",\n        "spouse_appearance",\n''',
'''    if primary_event == "spouse_age_profile":\n        if any(question.startswith(prefix) for prefix in ("will ", "could ", "can ", "is ", "would ")):\n            return "probability"\n        return "general_outlook"\n\n    if primary_event in (\n        "spouse_traits",\n        "spouse_appearance",\n''', "question type")

direction_anchor = '''def _resolve_direction(\n    primary_event: str,\n    base_analysis: dict[str, Any],\n) -> str:\n\n'''
s = replace_once(
    s,
    direction_anchor,
    direction_anchor + '''    if primary_event == "spouse_age_profile":\n        return "neutral"\n\n''',
    "direction function",
)

confidence_anchor = '''def _resolve_confidence(\n    primary_event: str,\n    base_analysis: dict[str, Any],\n    comparison: dict[str, Any],\n) -> float:\n\n'''
s = replace_once(
    s,
    confidence_anchor,
    confidence_anchor + '''    if primary_event == "spouse_age_profile":\n        base_intent = _safe_dict(base_analysis.get("intent"))\n        base_confidence = float(base_intent.get("confidence", 0.60) or 0.60)\n        return max(base_confidence, 0.82)\n\n''',
    "confidence function",
)

cleanup_anchor = '''def _clean_base_events(\n    base_events: list[Any],\n    special_events: list[dict[str, Any]],\n) -> list[dict[str, Any]]:\n'''
cleanup_insertion = '''\n    # spouse_age_profile is handled below through special_names; age-specific\n    # questions should not retain generic spouse/marriage detections.\n'''
s = replace_once(s, cleanup_anchor, cleanup_anchor + cleanup_insertion, "base cleanup function")

# Put the actual cleanup before the first cleaned.append(raw_item) call within the function.
base_start = s.index("def _clean_base_events(")
base_end = s.index("def _clean_special_event_conflicts(", base_start)
base_block = s[base_start:base_end]
needle = '''        cleaned.append(\n            raw_item\n        )\n'''
replacement = '''        if (\n            "spouse_age_profile" in special_names\n            and event_name in ("spouse_traits", "general_marriage", "marriage_timing")\n        ):\n            continue\n\n''' + needle
if needle not in base_block:
    raise RuntimeError("missing anchor: base cleanup append")
base_block = base_block.replace(needle, replacement, 1)
s = s[:base_start] + base_block + s[base_end:]

special_start = s.index("def _clean_special_event_conflicts(")
special_end = s.index("def _merge_events(", special_start)
special_block = s[special_start:special_end]
needle = '''        cleaned.append(\n            item\n        )\n'''
replacement = '''        if (\n            "spouse_age_profile" in names\n            and event_name == "spouse_traits"\n        ):\n            continue\n\n''' + needle
if needle not in special_block:
    raise RuntimeError("missing anchor: special conflict append")
special_block = special_block.replace(needle, replacement, 1)
s = s[:special_start] + special_block + s[special_end:]

p.write_text(s)


# ---------------- Router V3 ----------------
p = Path("app/astrology/features/marriage_forecast_router_v3.py")
s = p.read_text()

s = replace_once(s,
'''from app.astrology.features.spouse_family_background_reasoning_v2 import (\n    analyze_spouse_family_background_v2,\n)\n''',
'''from app.astrology.features.spouse_family_background_reasoning_v2 import (\n    analyze_spouse_family_background_v2,\n)\n\nfrom app.astrology.features.spouse_age_profile_reasoning_v2 import (\n    analyze_spouse_age_profile_v2,\n)\n''', "router import")

s = replace_once(s,
'''    "spouse_family_background": (\n        "Spouse Family / Social Background"\n    ),\n''',
'''    "spouse_family_background": (\n        "Spouse Family / Social Background"\n    ),\n    "spouse_age_profile": (\n        "Spouse Age / Maturity Profile"\n    ),\n''', "router label")

route_marker = "# =========================================================\n# SPOUSE PROFESSION ROUTE\n# =========================================================\n"
route = '''# =========================================================\n# SPOUSE AGE / MATURITY ROUTE\n# =========================================================\n\ndef _route_spouse_age_profile(chart: dict[str, Any], question_analysis: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:\n    intent = _safe_dict(question_analysis.get("intent"))\n    question = str(question_analysis.get("original_question", question_analysis.get("normalised_question", "")) or "")\n    analysis = analyze_spouse_age_profile_v2(chart, question)\n    if not analysis.get("available"):\n        return {\n            "available": False, "route": "natal_evidence", "event": "spouse_age_profile",\n            "event_label": EVENT_LABELS["spouse_age_profile"],\n            "question_type": intent.get("question_type"), "direction": intent.get("direction"),\n            "parser_confidence": intent.get("confidence"), "reference_moment": reference_moment.isoformat(),\n            "evidence_engine": "spouse_age_profile_reasoning_v2", "forecast_type": "natal_pattern",\n            "reason": analysis.get("reason"),\n        }\n    result = dict(analysis)\n    result.update({\n        "available": True, "route": "natal_evidence", "event": "spouse_age_profile",\n        "event_label": EVENT_LABELS["spouse_age_profile"],\n        "question_type": intent.get("question_type"), "direction": intent.get("direction"),\n        "parser_confidence": intent.get("confidence"), "reference_moment": reference_moment.isoformat(),\n        "evidence_engine": "spouse_age_profile_reasoning_v2", "forecast_type": "natal_pattern",\n    })\n    return result\n\n\n'''
s = replace_once(s, route_marker, route + route_marker, "router route location")

# Main single-event dispatch uses one-line style for family background.
dispatch_anchor = '''    if query_mode == "single_event" and event_name == "spouse_family_background":\n        return _route_spouse_family_background(chart, question_analysis, reference_moment)\n'''
dispatch = '''    if query_mode == "single_event" and event_name == "spouse_age_profile":\n        return _route_spouse_age_profile(chart, question_analysis, reference_moment)\n\n'''
s = replace_once(s, dispatch_anchor, dispatch + dispatch_anchor, "router dispatch")

# Follow-up dispatch should inherit the new event as well.
followup_anchor = '''    elif inherited_event == (\n        "spouse_family_background"\n    ):\n\n        result = _route_spouse_family_background(chart, inherited_analysis, reference_moment)\n'''
followup = '''    elif inherited_event == (\n        "spouse_age_profile"\n    ):\n\n        result = _route_spouse_age_profile(chart, inherited_analysis, reference_moment)\n\n'''
s = replace_once(s, followup_anchor, followup + followup_anchor, "router follow-up dispatch")

p.write_text(s)
