from pathlib import Path

path = Path("app/astrology/features/marriage_question_intelligence_v3.py")
text = path.read_text(encoding="utf-8")
old = '            "spouse_family_background" in names\n            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n'
new = '            "spouse_family_background" in names\n            and event_name in ("spouse_education","spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")\n'
if old not in text:
    raise RuntimeError("Missing spouse family conflict-cleanup anchor")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
