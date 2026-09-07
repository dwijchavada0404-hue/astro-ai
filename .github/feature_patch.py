from pathlib import Path

path = Path("web/src/chart-viewer.tsx")
text = path.read_text(encoding="utf-8")

text = text.replace(
    'import { KundliChart } from "./kundli-chart";\nimport "./kundli-chart.css";',
    'import { KundliChart } from "./kundli-chart";\nimport { NavamsaView } from "./navamsa-view";\nimport "./kundli-chart.css";',
)

text = text.replace(
    '  houses?: Record<string, House>;\n  dashas?: Dashas;',
    '  houses?: Record<string, House>;\n  divisional_charts?: { D9?: any };\n  dashas?: Dashas;',
)

needle = '        <section className="chart-section"><div className="chart-section-title"><h4>Kundli</h4><span>Choose North or South Indian layout</span></div><KundliChart houses={chart.houses} planets={chart.planets} /></section>\n'
replacement = needle + '        <NavamsaView chart={chart.divisional_charts?.D9} />\n'
if needle not in text:
    raise SystemExit("Kundli integration point not found")
text = text.replace(needle, replacement, 1)

path.write_text(text, encoding="utf-8")
