from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"anchor not found: {label}")
    return text.replace(old, new, 1)


# Intelligence V3
p = Path("app/astrology/features/marriage_question_intelligence_v3.py")
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    '    "marriage_compatibility_dynamics": (\n        "Marriage Compatibility / Partner Dynamics"\n    ),\n',
    '    "marriage_compatibility_dynamics": (\n        "Marriage Compatibility / Partner Dynamics"\n    ),\n    "post_marriage_life_changes": (\n        "Post-Marriage Life Changes"\n    ),\n',
    "event label",
)
helper = '''\n\n# =========================================================\n# POST-MARRIAGE LIFE CHANGES DETECTION\n# =========================================================\n\ndef _detect_post_marriage_life_changes(question: str) -> dict[str, Any] | None:\n    patterns = (\n        (r"\\blife\\s+change\\s+after\\s+marriage\\b", "post-marriage life change"),\n        (r"\\bafter\\s+marriage\\b.{0,28}\\b(?:relocate|relocation|move|career|job|finances?|money|lifestyle|responsibilit|abroad|overseas|international)\\b", "post-marriage change"),\n        (r"\\b(?:relocate|relocation|move\\s+(?:city|cities|abroad|overseas)|change\\s+city)\\b.{0,28}\\bafter\\s+marriage\\b", "post-marriage relocation"),\n        (r"\\b(?:career|job|profession)\\s+(?:change|shift)\\b.{0,28}\\bafter\\s+marriage\\b", "post-marriage career change"),\n        (r"\\b(?:finances?|money|income|wealth)\\b.{0,28}\\bafter\\s+marriage\\b", "post-marriage financial change"),\n        (r"\\b(?:lifestyle|daily\\s+life|home\\s+life|domestic\\s+life)\\b.{0,28}\\bafter\\s+marriage\\b", "post-marriage lifestyle change"),\n        (r"\\bfamily\\s+responsibilit(?:y|ies)\\b.{0,28}\\bafter\\s+marriage\\b", "post-marriage responsibility change"),\n        (r"\\b(?:move|live|settle)\\s+(?:abroad|overseas)\\b.{0,28}\\bafter\\s+marriage\\b", "post-marriage international exposure"),\n    )\n    matched = []\n    for pattern, label in patterns:\n        if re.search(pattern, question) and label not in matched:\n            matched.append(label)\n    if not matched:\n        return None\n    return {"event": "post_marriage_life_changes", "event_label": EVENT_LABELS["post_marriage_life_changes"], "matched_keywords": matched}\n'''
s = replace_once(
    s,
    '\n# =========================================================\n# SPECIAL EVENT DETECTION\n# =========================================================\n',
    helper + '\n# =========================================================\n# SPECIAL EVENT DETECTION\n# =========================================================\n',
    "helper insertion",
)
s = replace_once(
    s,
    '    detected = []\n\n',
    '    detected = []\n\n    post_marriage_life_changes = _detect_post_marriage_life_changes(question)\n    if post_marriage_life_changes:\n        detected.append(post_marriage_life_changes)\n\n',
    "detector call",
)
s = replace_once(
    s,
    '        if (\n            "relationship_challenges" in special_names\n            and event_name in ("general_marriage", "relationship_stability", "marriage_delay_challenge", "marriage_timing")\n        ):\n            continue\n',
    '        if (\n            "post_marriage_life_changes" in special_names\n            and event_name in ("general_marriage", "marriage_timing", "relationship_stability")\n        ):\n            continue\n\n        if (\n            "relationship_challenges" in special_names\n            and event_name in ("general_marriage", "relationship_stability", "marriage_delay_challenge", "marriage_timing")\n        ):\n            continue\n',
    "base cleanup",
)
s = replace_once(
    s,
    '        "spouse_family_background",\n        "relationship_challenges",\n',
    '        "spouse_family_background",\n        "post_marriage_life_changes",\n        "relationship_challenges",\n',
    "priority",
)
p.write_text(s, encoding="utf-8")


# Router V3
p = Path("app/astrology/features/marriage_forecast_router_v3.py")
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    'from app.astrology.features.relationship_challenges_reasoning_v2 import (\n    analyze_relationship_challenges_v2,\n)\n',
    'from app.astrology.features.relationship_challenges_reasoning_v2 import (\n    analyze_relationship_challenges_v2,\n)\n\nfrom app.astrology.features.post_marriage_life_changes_reasoning_v2 import (\n    analyze_post_marriage_life_changes_v2,\n)\n',
    "router import",
)
s = replace_once(
    s,
    '    "marriage_compatibility_dynamics": (\n        "Marriage Compatibility / Partner Dynamics"\n    ),\n',
    '    "marriage_compatibility_dynamics": (\n        "Marriage Compatibility / Partner Dynamics"\n    ),\n    "post_marriage_life_changes": (\n        "Post-Marriage Life Changes"\n    ),\n',
    "router label",
)
route_fn = '''\n\n# =========================================================\n# POST-MARRIAGE LIFE CHANGES ROUTE\n# =========================================================\n\ndef _route_post_marriage_life_changes(chart: dict[str, Any], question_analysis: dict[str, Any], reference_moment: datetime) -> dict[str, Any]:\n    intent = _safe_dict(question_analysis.get("intent"))\n    question = str(question_analysis.get("original_question", question_analysis.get("normalised_question", "")) or "")\n    analysis = analyze_post_marriage_life_changes_v2(chart, question)\n    result = {\n        "available": bool(analysis.get("available")), "route": "natal_evidence", "event": "post_marriage_life_changes",\n        "event_label": EVENT_LABELS["post_marriage_life_changes"], "question_type": intent.get("question_type"),\n        "direction": intent.get("direction"), "parser_confidence": intent.get("confidence"),\n        "reference_moment": reference_moment.isoformat(), "evidence_engine": "post_marriage_life_changes_reasoning_v2",\n        "forecast_type": "natal_pattern", "model_version": analysis.get("model_version"),\n        "question": analysis.get("question", question), "normalised_question": analysis.get("normalised_question"),\n        "target": analysis.get("target"), "target_label": analysis.get("target_label"),\n        "matched_keywords": analysis.get("matched_keywords", []), "support_score": analysis.get("support_score"),\n        "support_level": analysis.get("support_level"), "support_label": analysis.get("support_label"),\n        "confidence": analysis.get("confidence"), "answer": analysis.get("answer"), "summary": analysis.get("summary"),\n        "limitation": analysis.get("limitation"), "strongest_themes": analysis.get("strongest_themes", []),\n        "evidence_count": analysis.get("evidence_count", 0), "evidence": analysis.get("evidence", []),\n        "natal_profile": analysis.get("natal_profile", {}), "analysis": analysis,\n    }\n    if not analysis.get("available"):\n        result["reason"] = analysis.get("reason")\n    return result\n'''
s = replace_once(
    s,
    '\n# =========================================================\n# SPOUSE PROFESSION TARGET DETECTION\n# =========================================================\n',
    route_fn + '\n# =========================================================\n# SPOUSE PROFESSION TARGET DETECTION\n# =========================================================\n',
    "route insertion",
)
s = replace_once(
    s,
    '    elif inherited_event == (\n        "relationship_challenges"\n    ):\n\n        result = _route_relationship_challenges(chart, inherited_analysis, reference_moment)\n',
    '    elif inherited_event == (\n        "relationship_challenges"\n    ):\n\n        result = _route_relationship_challenges(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "post_marriage_life_changes"\n    ):\n\n        result = _route_post_marriage_life_changes(chart, inherited_analysis, reference_moment)\n',
    "follow-up dispatch",
)
s = replace_once(
    s,
    '    if query_mode == "single_event" and event_name == "relationship_challenges":\n        return _route_relationship_challenges(chart, question_analysis, reference_moment)\n',
    '    if query_mode == "single_event" and event_name == "relationship_challenges":\n        return _route_relationship_challenges(chart, question_analysis, reference_moment)\n\n    if query_mode == "single_event" and event_name == "post_marriage_life_changes":\n        return _route_post_marriage_life_changes(chart, question_analysis, reference_moment)\n',
    "main dispatch",
)
p.write_text(s, encoding="utf-8")
