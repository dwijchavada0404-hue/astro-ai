from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"anchor not found: {label}")
    return text.replace(old, new, 1)


# Accept natural phrasing such as "Could my marriage be unstable?"
p = Path("app/astrology/features/marriage_question_intelligence_v3.py")
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    '        (r"\\b(?:marriage|relationship)\\s+(?:unstable|instability|unpredictable)\\b", "relationship instability"),\n',
    '        (r"\\b(?:marriage|relationship)\\s+(?:be\\s+|feel\\s+|become\\s+)?(?:unstable|instability|unpredictable)\\b", "relationship instability"),\n',
    "instability natural phrasing",
)
p.write_text(s, encoding="utf-8")


# V2's public target contract intentionally uses "distance" while the natal
# profile dimension is named "emotional_distance". Keep the integration test
# aligned with that contract instead of renaming the established V2 target.
p = Path("tests/test_relationship_challenges_v3_integration.py")
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    '    assert result["target"] == "emotional_distance"\n',
    '    assert result["target"] == "distance"\n    assert result["analysis"]["analysis"]["requested_profiles"] == ["emotional_distance"]\n',
    "distance target contract",
)
p.write_text(s, encoding="utf-8")
