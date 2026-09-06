from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "web" / "src" / "chart-viewer.tsx"


def test_chart_viewer_exposes_engine_mahadasha_timeline():
    viewer = VIEWER.read_text(encoding="utf-8")

    assert "mahadashas?: Mahadasha[]" in viewer
    assert "Vimshottari Mahadasha timeline" in viewer
    assert "120-year deterministic sequence" in viewer
    assert "mahadashaRows(chart?.dashas)" in viewer
    assert 'aria-current={period.isCurrent ? "true" : undefined}' in viewer
