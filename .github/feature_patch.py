from pathlib import Path

p = Path("app/astrology/features/marriage_question_intelligence_v3.py")
s = p.read_text()

old = '''        "spouse_family_background",\n        "spouse_education",\n        "spouse_profession",\n        "foreign_intercultural_connection",\n        "spouse_appearance",\n'''
new = '''        "spouse_family_background",\n        "spouse_education",\n        "spouse_profession",\n        "foreign_intercultural_connection",\n        "spouse_age_profile",\n        "spouse_appearance",\n'''

if old not in s:
    raise RuntimeError("missing primary priority anchor")

s = s.replace(old, new, 1)
p.write_text(s)
