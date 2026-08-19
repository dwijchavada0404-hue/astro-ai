from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Missing patch anchor: {label}")
    return text.replace(old, new, 1)


# =========================================================
# QUESTION INTELLIGENCE V3
# =========================================================

path = Path("app/astrology/features/marriage_question_intelligence_v3.py")
text = path.read_text(encoding="utf-8")

text = replace_once(
    text,
    '    "spouse_wealth": (\n        "Spouse Wealth / Financial Profile"\n    ),\n',
    '    "spouse_wealth": (\n        "Spouse Wealth / Financial Profile"\n    ),\n'
    '    "spouse_family_background": (\n        "Spouse Family / Social Background"\n    ),\n',
    "intelligence event label",
)

family_detector = r'''
# =========================================================
# SPOUSE FAMILY / SOCIAL BACKGROUND DETECTION
# =========================================================

def _detect_spouse_family_background(question: str) -> dict[str, Any] | None:
    spouse_markers = (
        "spouse", "future spouse", "partner", "future partner",
        "husband", "wife", "person i marry", "person i will marry",
    )
    if not any(marker in question for marker in spouse_markers):
        return None

    # Wealth-specific family questions remain owned by spouse_wealth so the
    # existing API contract for "wealthy family" is preserved.
    wealth_family_patterns = (
        r"\bwealthy\s+family\b",
        r"\brich\s+family\b",
        r"\baffluent\s+family\b",
        r"\bfamily\s+wealth\b",
        r"\binherited\s+wealth\b",
        r"\binheritance\b",
    )
    if any(re.search(pattern, question) for pattern in wealth_family_patterns):
        return None

    patterns = (
        (r"\bfamily\s+background\b", "spouse family background"),
        (r"\bsocial\s+background\b", "spouse social background"),
        (r"\bwhat\s+(?:kind|type)\s+of\s+family\b", "spouse family profile"),
        (r"\bfamily\s+(?:will|would)\s+(?:my\s+)?(?:spouse|partner)\s+come\s+from\b", "spouse family profile"),
        (r"\btraditional\s+family\b", "traditional family"),
        (r"\bconservative\s+family\b", "conservative family"),
        (r"\bestablished\s+family\b", "established family"),
        (r"\brespectable\s+family\b", "respectable family"),
        (r"\borthodox\s+family\b", "orthodox family"),
        (r"\beducated\s+family\b", "educated family"),
        (r"\bcultured\s+family\b", "cultured family"),
        (r"\bacademic\s+family\b", "academic family"),
        (r"\bintellectual\s+family\b", "intellectual family"),
        (r"\bbusiness\s+family\b", "business family"),
        (r"\bfamily\s+business\b", "family business"),
        (r"\bentrepreneurial\s+family\b", "entrepreneurial family"),
        (r"\bprofessional\s+family\b", "professional family"),
        (r"\bfamily\s+of\s+professionals\b", "family of professionals"),
        (r"\binternational\s+family\b", "international family"),
        (r"\bmulticultural\s+family\b", "multicultural family"),
        (r"\bmodern\s+family\b", "modern family"),
        (r"\bglobal\s+family\b", "global family"),
        (r"\bcreative\s+family\b", "creative family"),
        (r"\bartistic\s+family\b", "artistic family"),
        (r"\bmedia\s+family\b", "media family"),
    )
    matched = []
    for pattern, label in patterns:
        if re.search(pattern, question) and label not in matched:
            matched.append(label)
    if not matched:
        return None
    return {
        "event": "spouse_family_background",
        "event_label": EVENT_LABELS["spouse_family_background"],
        "matched_keywords": matched,
    }


'''
text = replace_once(
    text,
    "# =========================================================\n# SPOUSE APPEARANCE DETECTION\n# =========================================================\n",
    family_detector + "# =========================================================\n# SPOUSE APPEARANCE DETECTION\n# =========================================================\n",
    "family detector",
)

text = replace_once(
    text,
    '    spouse_wealth = _detect_spouse_wealth(question)\n    if spouse_wealth:\n        detected.append(spouse_wealth)\n\n',
    '    spouse_wealth = _detect_spouse_wealth(question)\n    if spouse_wealth:\n        detected.append(spouse_wealth)\n\n'
    '    # -----------------------------------------------------\n'
    '    # SPOUSE FAMILY / SOCIAL BACKGROUND\n'
    '    # -----------------------------------------------------\n\n'
    '    spouse_family_background = _detect_spouse_family_background(question)\n'
    '    if spouse_family_background:\n'
    '        detected.append(spouse_family_background)\n\n',
    "special event detection",
)

text = replace_once(
    text,
    '        if (\n            "spouse_wealth" in special_names\n            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")\n        ):\n            continue\n\n',
    '        if (\n            "spouse_wealth" in special_names\n            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")\n        ):\n            continue\n\n'
    '        if (\n            "spouse_family_background" in special_names\n            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")\n        ):\n            continue\n\n',
    "base event cleanup",
)

text = replace_once(
    text,
    '        if (\n            "spouse_wealth" in names\n            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n        ):\n            continue\n\n',
    '        if (\n            "spouse_wealth" in names\n            and event_name in ("spouse_family_background","spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n        ):\n            continue\n\n'
    '        if (\n            "spouse_family_background" in names\n            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n        ):\n            continue\n\n',
    "special event conflicts",
)

text = replace_once(
    text,
    '        "spouse_wealth",\n        "spouse_profession",\n',
    '        "spouse_wealth",\n        "spouse_family_background",\n        "spouse_profession",\n',
    "comparison specific events",
)

text = replace_once(
    text,
    '        "spouse_wealth",\n        "spouse_education",\n',
    '        "spouse_wealth",\n        "spouse_family_background",\n        "spouse_education",\n',
    "primary event priority",
)

# Add the family event to question-type, direction, and confidence tuples.
for label in ("question type", "direction", "confidence"):
    anchor = '        "spouse_wealth",\n        "spouse_profession",\n'
    if anchor in text:
        text = text.replace(anchor, '        "spouse_wealth",\n        "spouse_family_background",\n        "spouse_profession",\n', 1)
    else:
        anchor = '        "spouse_wealth",\n        "foreign_intercultural_connection",\n'
        if label == "question type" and anchor in text:
            text = text.replace(anchor, '        "spouse_wealth",\n        "spouse_family_background",\n        "foreign_intercultural_connection",\n', 1)
        else:
            raise RuntimeError(f"Missing patch anchor: {label}")

path.write_text(text, encoding="utf-8")


# =========================================================
# FORECAST ROUTER V3
# =========================================================

path = Path("app/astrology/features/marriage_forecast_router_v3.py")
text = path.read_text(encoding="utf-8")

text = replace_once(
    text,
    'from app.astrology.features.spouse_wealth_reasoning_v2 import (\n    analyze_spouse_wealth_v2,\n)\n\n',
    'from app.astrology.features.spouse_wealth_reasoning_v2 import (\n    analyze_spouse_wealth_v2,\n)\n\n'
    'from app.astrology.features.spouse_family_background_reasoning_v2 import (\n    analyze_spouse_family_background_v2,\n)\n\n',
    "router import",
)

text = replace_once(
    text,
    '    "spouse_wealth": (\n        "Spouse Wealth / Financial Profile"\n    ),\n',
    '    "spouse_wealth": (\n        "Spouse Wealth / Financial Profile"\n    ),\n'
    '    "spouse_family_background": (\n        "Spouse Family / Social Background"\n    ),\n',
    "router event label",
)

family_route = '''# =========================================================
# SPOUSE FAMILY / SOCIAL BACKGROUND ROUTE
# =========================================================

def _route_spouse_family_background(
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
    analysis = analyze_spouse_family_background_v2(chart, question)
    result = {
        "available": bool(analysis.get("available")),
        "route": "natal_evidence",
        "event": "spouse_family_background",
        "event_label": EVENT_LABELS["spouse_family_background"],
        "question_type": intent.get("question_type"),
        "direction": intent.get("direction"),
        "parser_confidence": intent.get("confidence"),
        "reference_moment": reference_moment.isoformat(),
        "evidence_engine": "spouse_family_background_reasoning_v2",
        "forecast_type": "natal_pattern",
        "model_version": analysis.get("model_version"),
        "question": analysis.get("question", question),
        "normalised_question": analysis.get(
            "normalised_question",
            str(question_analysis.get("normalised_question", "") or ""),
        ),
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
text = replace_once(
    text,
    "# =========================================================\n# SPOUSE APPEARANCE ROUTE\n# =========================================================\n",
    family_route + "# =========================================================\n# SPOUSE APPEARANCE ROUTE\n# =========================================================\n",
    "family route",
)

text = replace_once(
    text,
    '    elif inherited_event == (\n        "spouse_wealth"\n    ):\n\n        result = _route_spouse_wealth(chart, inherited_analysis, reference_moment)\n\n',
    '    elif inherited_event == (\n        "spouse_wealth"\n    ):\n\n        result = _route_spouse_wealth(chart, inherited_analysis, reference_moment)\n\n'
    '    elif inherited_event == (\n        "spouse_family_background"\n    ):\n\n        result = _route_spouse_family_background(chart, inherited_analysis, reference_moment)\n\n',
    "follow up route",
)

text = replace_once(
    text,
    '    if query_mode == "single_event" and event_name == "spouse_wealth":\n        return _route_spouse_wealth(chart, question_analysis, reference_moment)\n\n',
    '    if query_mode == "single_event" and event_name == "spouse_wealth":\n        return _route_spouse_wealth(chart, question_analysis, reference_moment)\n\n'
    '    # -----------------------------------------------------\n'
    '    # SPOUSE FAMILY / SOCIAL BACKGROUND\n'
    '    # -----------------------------------------------------\n\n'
    '    if query_mode == "single_event" and event_name == "spouse_family_background":\n'
    '        return _route_spouse_family_background(chart, question_analysis, reference_moment)\n\n',
    "main family route",
)

path.write_text(text, encoding="utf-8")
