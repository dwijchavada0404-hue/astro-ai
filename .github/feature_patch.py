from pathlib import Path

viewer = Path("web/src/chart-viewer.tsx")
text = viewer.read_text(encoding="utf-8")
text = text.replace('import { apiRequest, type BirthProfile } from "./api";\n', 'import { apiRequest, type BirthProfile } from "./api";\nimport { NorthIndianKundli } from "./kundli-chart";\nimport "./kundli-chart.css";\n')
needle = '        <section className="chart-section"><div className="chart-section-title"><h4>Planetary positions</h4><span>Calculated at birth</span></div>'
replacement = '        <section className="chart-section"><div className="chart-section-title"><h4>North Indian Kundli</h4><span>Visual house map</span></div><NorthIndianKundli houses={chart.houses} planets={chart.planets} /></section>\n' + needle
if needle not in text:
    raise SystemExit("chart viewer integration anchor not found")
text = text.replace(needle, replacement, 1)
viewer.write_text(text, encoding="utf-8")
