from pathlib import Path

INTEL = Path("app/astrology/features/marriage_question_intelligence_v3.py")
ROUTER = Path("app/astrology/features/marriage_forecast_router_v3.py")


def rep(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing patch anchor: {label}")
    return text.replace(old, new, 1)


# -------------------------- intelligence --------------------------
text = INTEL.read_text(encoding="utf-8-sig")

text = rep(
    text,
    '    "spouse_education": (\n        "Spouse Education / Intellectual Profile"\n    ),\n    "spouse_profession": (',
    '    "spouse_education": (\n        "Spouse Education / Intellectual Profile"\n    ),\n    "spouse_wealth": (\n        "Spouse Wealth / Financial Profile"\n    ),\n    "spouse_profession": (',
    "event label",
)

wealth_detector = '''# =========================================================
# SPOUSE WEALTH DETECTION
# =========================================================

def _detect_spouse_wealth(question: str) -> dict[str, Any] | None:
    spouse_markers = (
        "spouse", "future spouse", "partner", "future partner",
        "husband", "wife", "person i marry", "person i will marry",
    )
    if not any(marker in question for marker in spouse_markers):
        return None

    patterns = (
        (r"\\bfinancial\\s+profile\\b", "spouse financial profile"),
        (r"\\bfinancial\\s+background\\b", "spouse financial background"),
        (r"\\bfinancially\\s+stable\\b", "spouse financial stability"),
        (r"\\bfinancial\\s+stability\\b", "spouse financial stability"),
        (r"\\b(?:wealthy|rich|affluent|well[- ]off)\\b", "spouse wealth"),
        (r"\\b(?:family\\s+wealth|wealthy\\s+family|rich\\s+family)\\b", "spouse family wealth"),
        (r"\\b(?:inherited\\s+wealth|inheritance)\\b", "spouse inherited wealth"),
        (r"\\b(?:own\\s+property|property\\s+assets?|asset[- ]rich|real\\s+estate\\s+assets?)\\b", "spouse property assets"),
        (r"\\b(?:professional\\s+income|high\\s+income|high\\s+salary|salary\\s+level)\\b", "spouse professional income"),
        (r"\\b(?:business\\s+wealth|business\\s+income|entrepreneurial\\s+wealth)\\b", "spouse business wealth"),
        (r"\\b(?:foreign\\s+income|international\\s+income|income\\s+abroad|earn\\s+abroad|overseas\\s+income)\\b", "spouse international income"),
        (r"\\b(?:good\\s+with\\s+money|money\\s+management|financially\\s+intelligent|financial\\s+skill)\\b", "spouse financial skill"),
        (r"\\b(?:speculative\\s+income|trading\\s+income|stock\\s+market\\s+income|variable\\s+income|high[- ]risk\\s+income)\\b", "spouse speculative income"),
    )
    matched = []
    for pattern, label in patterns:
        if re.search(pattern, question) and label not in matched:
            matched.append(label)
    if not matched:
        return None
    return {
        "event": "spouse_wealth",
        "event_label": EVENT_LABELS["spouse_wealth"],
        "matched_keywords": matched,
    }


'''
text = rep(
    text,
    '# =========================================================\n# SPOUSE APPEARANCE DETECTION\n# =========================================================\n',
    wealth_detector + '# =========================================================\n# SPOUSE APPEARANCE DETECTION\n# =========================================================\n',
    "detector",
)

text = rep(
    text,
    '    spouse_education = _detect_spouse_education(question)\n    if spouse_education:\n        detected.append(spouse_education)\n\n    # -----------------------------------------------------\n    # SPOUSE APPEARANCE',
    '    spouse_education = _detect_spouse_education(question)\n    if spouse_education:\n        detected.append(spouse_education)\n\n    # -----------------------------------------------------\n    # SPOUSE WEALTH / FINANCIAL PROFILE\n    # -----------------------------------------------------\n\n    spouse_wealth = _detect_spouse_wealth(question)\n    if spouse_wealth:\n        detected.append(spouse_wealth)\n\n    # -----------------------------------------------------\n    # SPOUSE APPEARANCE',
    "special detection",
)

text = rep(
    text,
    '        if (\n            "spouse_education" in special_names\n            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")\n        ):\n            continue\n\n        if (\n            "spouse_appearance"',
    '        if (\n            "spouse_education" in special_names\n            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")\n        ):\n            continue\n\n        if (\n            "spouse_wealth" in special_names\n            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")\n        ):\n            continue\n\n        if (\n            "spouse_appearance"',
    "base cleanup",
)

text = rep(
    text,
    '        if (\n            "spouse_education" in names\n            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n        ):\n            continue\n\n        if (\n            "spouse_profession"',
    '        if (\n            "spouse_wealth" in names\n            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n        ):\n            continue\n\n        if (\n            "spouse_education" in names\n            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n        ):\n            continue\n\n        if (\n            "spouse_profession"',
    "conflict cleanup",
)

text = rep(
    text,
    '    specific_events = {\n        "relationship_commitment",\n        "marriage_delay_challenge",\n        "relationship_stability",\n        "foreign_intercultural_connection",\n        "spouse_traits",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_profession",',
    '    specific_events = {\n        "relationship_commitment",\n        "marriage_delay_challenge",\n        "relationship_stability",\n        "foreign_intercultural_connection",\n        "spouse_traits",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_wealth",\n        "spouse_profession",',
    "comparison set",
)

text = rep(
    text,
    '    priority = (\n        "love_vs_arranged",\n        "spouse_meeting",\n        "spouse_education",\n        "spouse_profession",',
    '    priority = (\n        "love_vs_arranged",\n        "spouse_meeting",\n        "spouse_wealth",\n        "spouse_education",\n        "spouse_profession",',
    "priority",
)

text = rep(
    text,
    '    if primary_event in (\n        "spouse_profession",\n        "spouse_appearance",\n        "spouse_education",\n        "foreign_intercultural_connection",',
    '    if primary_event in (\n        "spouse_profession",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_wealth",\n        "foreign_intercultural_connection",',
    "question type",
)

text = rep(
    text,
    '    if primary_event in (\n        "spouse_traits",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_profession",\n        "love_vs_arranged",',
    '    if primary_event in (\n        "spouse_traits",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_wealth",\n        "spouse_profession",\n        "love_vs_arranged",',
    "direction",
)

text = rep(
    text,
    '        "spouse_traits",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_profession",\n        "foreign_intercultural_connection",',
    '        "spouse_traits",\n        "spouse_appearance",\n        "spouse_education",\n        "spouse_wealth",\n        "spouse_profession",\n        "foreign_intercultural_connection",',
    "confidence",
)

INTEL.write_text(text, encoding="utf-8")


# ----------------------------- router -----------------------------
text = ROUTER.read_text(encoding="utf-8-sig")

text = rep(
    text,
    'from app.astrology.features.spouse_education_reasoning_v2 import (\n    analyze_spouse_education_v2,\n)\n\nfrom app.astrology.features.spouse_profession_reasoning_v2 import (',
    'from app.astrology.features.spouse_education_reasoning_v2 import (\n    analyze_spouse_education_v2,\n)\n\nfrom app.astrology.features.spouse_wealth_reasoning_v2 import (\n    analyze_spouse_wealth_v2,\n)\n\nfrom app.astrology.features.spouse_profession_reasoning_v2 import (',
    "router import",
)

text = rep(
    text,
    '    "spouse_education": (\n        "Spouse Education / Intellectual Profile"\n    ),\n    "spouse_profession": (',
    '    "spouse_education": (\n        "Spouse Education / Intellectual Profile"\n    ),\n    "spouse_wealth": (\n        "Spouse Wealth / Financial Profile"\n    ),\n    "spouse_profession": (',
    "router label",
)

route = '''# =========================================================
# SPOUSE WEALTH ROUTE
# =========================================================

def _route_spouse_wealth(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
) -> dict[str, Any]:
    intent = _safe_dict(question_analysis.get("intent"))
    question = str(
        question_analysis.get(
            "original_question",
            question_analysis.get("normalised_question", ""),
        )
        or ""
    )
    analysis = analyze_spouse_wealth_v2(chart, question)
    result = {
        "available": bool(analysis.get("available")),
        "route": "natal_evidence",
        "event": "spouse_wealth",
        "event_label": EVENT_LABELS["spouse_wealth"],
        "question_type": intent.get("question_type"),
        "direction": intent.get("direction"),
        "parser_confidence": intent.get("confidence"),
        "reference_moment": reference_moment.isoformat(),
        "evidence_engine": "spouse_wealth_reasoning_v2",
        "forecast_type": "natal_pattern",
        "model_version": analysis.get("model_version"),
        "question": analysis.get("question", question),
        "normalised_question": analysis.get("normalised_question", str(question_analysis.get("normalised_question", "") or "")),
        "target": analysis.get("target"),
        "target_label": analysis.get("target_label"),
        "matched_keywords": analysis.get("matched_keywords", []),
        "support_score": analysis.get("support_score"),
        "support_level": analysis.get("support_level"),
        "support_label": analysis.get("support_label"),
        "confidence": analysis.get("confidence"),
        "answer": analysis.get("answer"),
        "summary": analysis.get("summary"),
        "limitation": analysis.get("limitation"),
        "strongest_themes": analysis.get("strongest_themes", []),
        "evidence_count": analysis.get("evidence_count", 0),
        "evidence": analysis.get("evidence", []),
        "natal_profile": analysis.get("natal_profile", {}),
        "natal_analysis": analysis.get("natal_analysis", {}),
        "analysis": analysis,
    }
    if not analysis.get("available"):
        result["reason"] = analysis.get("reason")
    return result


'''
text = rep(
    text,
    '# =========================================================\n# SPOUSE APPEARANCE ROUTE\n# =========================================================\n',
    route + '# =========================================================\n# SPOUSE APPEARANCE ROUTE\n# =========================================================\n',
    "route function",
)

text = rep(
    text,
    '    elif inherited_event == (\n        "spouse_education"\n    ):\n\n        result = _route_spouse_education(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "spouse_profession"',
    '    elif inherited_event == (\n        "spouse_education"\n    ):\n\n        result = _route_spouse_education(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "spouse_wealth"\n    ):\n\n        result = _route_spouse_wealth(chart, inherited_analysis, reference_moment)\n\n    elif inherited_event == (\n        "spouse_profession"',
    "follow up",
)

text = rep(
    text,
    '    if query_mode == "single_event" and event_name == "spouse_education":\n        return _route_spouse_education(chart, question_analysis, reference_moment)\n\n    # -----------------------------------------------------\n    # SPOUSE PROFESSION',
    '    if query_mode == "single_event" and event_name == "spouse_education":\n        return _route_spouse_education(chart, question_analysis, reference_moment)\n\n    # -----------------------------------------------------\n    # SPOUSE WEALTH / FINANCIAL PROFILE\n    # -----------------------------------------------------\n\n    if query_mode == "single_event" and event_name == "spouse_wealth":\n        return _route_spouse_wealth(chart, question_analysis, reference_moment)\n\n    # -----------------------------------------------------\n    # SPOUSE PROFESSION',
    "dispatch",
)

ROUTER.write_text(text, encoding="utf-8")
