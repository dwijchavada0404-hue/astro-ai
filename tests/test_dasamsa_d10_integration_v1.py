from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "app" / "services" / "chart_service.py"
VIEWER = ROOT / "web" / "src" / "chart-viewer.tsx"
VIEW = ROOT / "web" / "src" / "dasamsa-view.tsx"


def test_saved_chart_response_exposes_d10_and_viewer_uses_backend_output():
    service = SERVICE.read_text(encoding="utf-8")
    viewer = VIEWER.read_text(encoding="utf-8")
    view = VIEW.read_text(encoding="utf-8")

    assert "build_dasamsa_chart(calculated)" in service
    assert '"D10": dasamsa' in service
    assert "DasamsaView" in viewer
    assert "chart.divisional_charts?.D10" in viewer
    assert "D1 sign" in view
    assert "D10 sign" in view
    assert "KundliChart houses={chart.houses} planets={chart.planets}" in view
