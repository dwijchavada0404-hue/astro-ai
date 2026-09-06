from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KUNDLI = ROOT / "web" / "src" / "kundli-chart.tsx"
VIEWER = ROOT / "web" / "src" / "chart-viewer.tsx"


def test_chart_viewer_exposes_north_and_south_indian_kundli_styles():
    kundli = KUNDLI.read_text(encoding="utf-8")
    viewer = VIEWER.read_text(encoding="utf-8")

    assert "SouthIndianKundli" in kundli
    assert "SOUTH_INDIAN_SIGNS" in kundli
    assert '"Pisces", "Aries", "Taurus", "Gemini"' in kundli
    assert 'aria-label="Kundli chart style"' in kundli
    assert "Selected house" in kundli
    assert "North Indian" in kundli
    assert "South Indian" in kundli
    assert "<KundliChart houses={chart.houses} planets={chart.planets} />" in viewer
