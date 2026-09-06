from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KUNDLI = ROOT / "web" / "src" / "kundli-chart.tsx"


def test_kundli_house_inspector_uses_engine_chart_details():
    source = KUNDLI.read_text(encoding="utf-8")

    assert "Selected house" in source
    assert "selectedHouse.planets" in source
    assert "planet.degree_dms" in source
    assert "planet.nakshatra" in source
    assert 'aria-pressed={selected}' in source
    assert 'event.key === "Enter" || event.key === " "' in source
