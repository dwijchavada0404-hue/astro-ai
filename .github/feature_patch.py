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
    '    "relationship_challenges": (\n        "Relationship Challenges / Stress & Repair"\n    ),\n',
    '    "relationship_challenges": (\n        "Relationship Challenges / Stress & Repair"\n    ),\n    "marriage_compatibility_dynamics": (\n        "Marriage Compatibility / Partner Dynamics"\n    ),\n',
    "intelligence event label",
)

helper = '''\n\n# =========================================================\n# MARRIAGE COMPATIBILITY / PARTNER DYNAMICS DETECTION\n# =========================================================\n\ndef _detect_marriage_compatibility_dynamics(question: str) -> dict[str, Any] | None:\n    patterns = (\n        (r"\\bmarriage\\s+compatibility\\b", "marriage compatibility"),\n        (r"\\brelationship\\s+compatibility\\b", "relationship compatibility"),\n        (r"\\bpartner\\s+dynamics?\\b", "partner dynamics"),\n        (r"\\brelationship\\s+dynamics?\\b", "relationship dynamics"),\n        (r"\\bhow\\s+(?:well\\s+)?(?:will|would|do)\\s+(?:we|my\\s+partner\\s+and\\s+i)\\s+(?:get\\s+along|understand\\s+each\\s+other)\\b", "mutual compatibility"),\n        (r"\\bcommunication\\s+(?:flow|style|compatibility)\\b", "communication flow"),\n        (r"\\b(?:communicate|communication)\\b.{0,24}\\b(?:marriage|relationship|partner)\\b", "relationship communication"),\n        (r"\\b(?:marriage|relationship|partner)\\b.{0,24}\\b(?:communicate|communication)\\b", "relationship communication"),\n        (r"\\bshared\\s+(?:values|beliefs|goals)\\b", "shared values"),\n        (r"\\bvalues?\\s+(?:alignment|compatibility)\\b", "values alignment"),\n        (r"\\bemotional\\s+(?:attunement|connection|understanding|compatibility)\\b", "emotional attunement"),\n        (r"\\b(?:need|needs|want|wants)\\s+(?:for\\s+)?(?:space|independence)\\b", "independence and space"),\n        (r"\\bindependence\\s+in\\s+(?:marriage|relationship)\\b", "independence and space"),\n        (r"\\badjustment\\s+(?:style|dynamics|compatibility)\\b", "adjustment dynamics"),\n        (r"\\bchemistry\\s+(?:between\\s+us|with\\s+(?:my\\s+)?partner)\\b", "partner chemistry"),\n    )\n    matched = []\n    for pattern, label in patterns:\n        if re.search(pattern, question) and label not in matched:\n            matched.append(label)\n    if not matched:\n        return None\n    return {\n        "event": "marriage_compatibility_dynamics",\n        "event_label": EVENT_LABELS["marriage_compatibility_dynamics"],\n        "matched_keywords": matched,\n    }\n'''

s = replace_once(
    s,
    '\n# =========================================================\n# RELATIONSHIP CHALLENGES DETECTION\n# =========================================================\n',
    helper + '\n# =========================================================\n# RELATIONSHIP CHALLENGES DETECTION\n# =========================================================\n',
    "compatibility detector insertion",
)

s = replace_once(
    s,
    '    relationship_challenges = _detect_relationship_challenges(question)\n    if relationship_challenges:\n        detected.append(relationship_challenges)\n\n    married_life_quality = _detect_married_life_quality(question)\n',
    '    relationship_challenges = _detect_relationship_challenges(question)\n    if relationship_challenges:\n        detected.append(relationship_challenges)\n\n    marriage_compatibility_dynamics = _detect_marriage_compatibility_dynamics(question)\n    if marriage_compatibility_dynamics:\n        detected.append(marriage_compatibility_dynamics)\n\n    married_life_quality = _detect_married_life_quality(question)\n',
    "compatibility detector call",
)

s = replace_once(
    s,
    '        if (\n            "relationship_challenges" in special_names\n            and event_name in ("general_marriage", "relationship_stability", "marriage_delay_challenge", "marriage_timing")\n        ):\n            continue\n\n        if (\n            "married_life_quality" in special_names\n',
    '        if (\n            "relationship_challenges" in special_names\n            and event_name in ("general_marriage", "relationship_stability", "marriage_delay_challenge", "marriage_timing")\n        ):\n            continue\n\n        if (\n            "marriage_compatibility_dynamics" in special_names\n            and event_name in ("general_marriage", "relationship_stability", "marriage_timing", "spouse_traits")\n        ):\n            continue\n\n        if (\n            "married_life_quality" in special_names\n',
    "base event cleanup",
)

s = replace_once(
    s,
    '        if (\n            "married_life_quality" in names\n            and event_name in ("spouse_traits",)\n        ):\n            continue\n\n        cleaned.append(\n',
    '        if (\n            "marriage_compatibility_dynamics" in names\n            and event_name in ("married_life_quality", "spouse_traits")\n        ):\n            continue\n\n        if (\n            "married_life_quality" in names\n            and event_name in ("spouse_traits",)\n        ):\n            continue\n\n        cleaned.append(\n',
    "special event conflict cleanup",
)

s = replace_once(
    s,
    '        "spouse_age_profile",\n        "married_life_quality",\n        "spouse_profession",\n',
    '        "spouse_age_profile",\n        "marriage_compatibility_dynamics",\n        "married_life_quality",\n        "spouse_profession",\n',
    "comparison specific events",
)

s = replace_once(
    s,
    '        "spouse_family_background",\n        "relationship_challenges",\n        "married_life_quality",\n',
    '        "spouse_family_background",\n        "relationship_challenges",\n        "marriage_compatibility_dynamics",\n        "married_life_quality",\n',
    "primary priority",
)

s = replace_once(
    s,
    '        "spouse_traits",\n        "love_vs_arranged",\n        "married_life_quality",\n',
    '        "spouse_traits",\n        "love_vs_arranged",\n        "marriage_compatibility_dynamics",\n        "married_life_quality",\n',
    "question type",
)

p.write_text(s, encoding="utf-8")


# ---------------------------------------------------------
# Marriage Forecast Router V3
# ---------------------------------------------------------
p = Path("app/astrology/features/marriage_forecast_router_v3.py")
s = p.read_text(encoding="utf-8")

s = replace_once(
    s,
    'from app.astrology.features.relationship_challenges_reasoning_v2 import (\n    analyze_relationship_challenges_v2,\n)\n',
    'from app.astrology.features.relationship_challenges_reasoning_v2 import (\n    analyze_relationship_challenges_v2,\n)\n\nfrom app.astrology.features.marriage_compatibility_dynamics_reasoning_v2 import (\n    analyze_marriage_compatibility_dynamics_v2,\n)\n',
    "router import",
)

s = replace_once(
    s,
    '    "relationship_challenges": (\n        "Relationship Challenges / Stress & Repair"\n    ),\n',
    '    "relationship_challenges": (\n        "Relationship Challenges / Stress & Repair"\n    ),\n    "marriage_compatibility_dynamics": (\n        "Marriage Compatibility / Partner Dynamics"\n    ),\n',
    "router event label",
)

route_fn = '''\n\n# =========================================================\n# MARRIAGE COMPATIBILITY / PARTNER DYNAMICS ROUTE\n# =========================================================\n\ndef _route_marriage_compatibility_dynamics(chart: dict[str, Any], question_analysis: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:\n    intent = _safe_dict(question_analysis.get("intent"))\n    question = str(question_analysis.get("original_question", question_analysis.get("normalised_question", "")) or "")\n    analysis = analyze_marriage_compatibility_dynamics_v2(chart, question)\n    result = {\n        "available": bool(analysis.get("available")),\n        "route": "natal_evidence",\n        "event": "marriage_compatibility_dynamics",\n        "event_label": EVENT_LABELS["marriage_compatibility_dynamics"],\n        "question_type": intent.get("question_type"),\n        "direction": intent.get("direction"),\n        "parser_confidence": intent.get("confidence"),\n        "reference_moment": reference_moment.isoformat(),\n        "evidence_engine": "marriage_compatibility_dynamics_reasoning_v2",\n        "forecast_type": "natal_pattern",\n        "model_version": analysis.get("model_version"),\n        "question": analysis.get("question", question),\n        "normalised_question": analysis.get("normalised_question"),\n        "target": analysis.get("target"),\n        "target_label": analysis.get("target_label"),\n        "matched_keywords": analysis.get("matched_keywords", []),\n        "support_score": analysis.get("support_score"),\n        "support_level": analysis.get("support_level"),\n        "support_label": analysis.get("support_label"),\n        "confidence": analysis.get("confidence"),\n        "answer": analysis.get("answer"),\n        "summary": analysis.get("summary"),\n        "limitation": analysis.get("limitation"),\n        "strongest_themes": analysis.get("strongest_themes", []),\n        "evidence_count": analysis.get("evidence_count", 0),\n        "evidence": analysis.get("evidence", []),\n        "natal_profile": analysis.get("natal_profile", {}),\n        "analysis": analysis,\n    }\n    if not analysis.get("available"):\n        result["reason"] = analysis.get("reason")\n    return result\n'''

s = replace_once(
    s,
    '\n# =========================================================\n# SPOUSE PROFESSION TARGET DETECTION\n# =========================================================\n',
    route_fn + '\n# =========================================================\n# SPOUSE PROFESSION TARGET DETECTION\n# =========================================================\n',
    "compatibility route insertion",
)

s = replace_once(
    s,
    '    elif inherited_event == (\n        "relationship_challenges"\n    ):\n\n        result = _route_relationship_challenges(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "spouse_profession"\n',
    '    elif inherited_event == (\n        "relationship_challenges"\n    ):\n\n        result = _route_relationship_challenges(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "marriage_compatibility_dynamics"\n    ):\n\n        result = _route_marriage_compatibility_dynamics(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "spouse_profession"\n',
    "follow-up dispatch",
)

s = replace_once(
    s,
    '    if query_mode == "single_event" and event_name == "relationship_challenges":\n        return _route_relationship_challenges(chart, question_analysis, reference_moment)\n\n    # -----------------------------------------------------\n    # SPOUSE PROFESSION\n',
    '    if query_mode == "single_event" and event_name == "relationship_challenges":\n        return _route_relationship_challenges(chart, question_analysis, reference_moment)\n\n    if query_mode == "single_event" and event_name == "marriage_compatibility_dynamics":\n        return _route_marriage_compatibility_dynamics(chart, question_analysis, reference_moment)\n\n    # -----------------------------------------------------\n    # SPOUSE PROFESSION\n',
    "main dispatch",
)

p.write_text(s, encoding="utf-8")
