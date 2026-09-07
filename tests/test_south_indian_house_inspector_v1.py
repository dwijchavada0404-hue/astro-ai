from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KUNDLI = ROOT / "web" / "src" / "kundli-chart.tsx"


def test_south_indian_chart_has_selectable_house_inspector():
    source = KUNDLI.read_text(encoding="utf-8")

    assert "function HouseInspector" in source
    assert "SouthIndianKundli" in source
    assert "setSelectedSign" in source
    assert 'aria-pressed={selected}' in source
    assert "selectedCell.houseNumber" in source
    assert "selectedCell.lord" in source
    assert "selectedCell.planets" in source
    assert "planet.degree_dms" in source
    assert "planet.nakshatra" in source
