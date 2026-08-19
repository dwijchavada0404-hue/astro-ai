from pathlib import Path

p = Path('app/astrology/features/marriage_question_intelligence_v3.py')
s = p.read_text()
start = s.index('def _detect_spouse_age_profile')
end = s.index('# =========================================================\n# SPECIAL EVENT DETECTION', start)
segment = s[start:end]
segment = segment.replace('\\\\b', '\\b').replace('\\\\s', '\\s')
segment = segment.replace('    spouse_context = (\n', '    if re.search(r"\\blook\\s+(?:youthful|mature)\\b", question):\n        return None\n\n    spouse_context = (\n', 1)
s = s[:start] + segment + s[end:]
p.write_text(s)
