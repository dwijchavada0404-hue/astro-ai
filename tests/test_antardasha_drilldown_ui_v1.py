from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "web" / "src" / "chart-viewer.tsx"


def test_chart_viewer_exposes_antardasha_drilldown():
    viewer = VIEWER.read_text(encoding="utf-8")
    assert "Antardasha drill-down" in viewer
    assert "Select a period to inspect its Antardashas" in viewer
    assert "antardashaRows(selectedMahadasha, currentPeriod)" in viewer
    assert "aria-pressed={period.start === selectedMahadasha?.start}" in viewer
    assert 'aria-current={subperiod.isCurrent ? "true" : undefined}' in viewer
