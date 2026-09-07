from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "app" / "services" / "chart_service.py"
VIEW = ROOT / "web" / "src" / "navamsa-view.tsx"


def test_saved_chart_response_exposes_navamsa_and_viewer_uses_engine_output():
    service = SERVICE.read_text(encoding="utf-8")
    view = VIEW.read_text(encoding="utf-8")

    assert "build_navamsa_chart(calculated)" in service
    assert '"divisional_charts"' in service
    assert '"D9": navamsa' in service
    assert "NavamsaView" in view
    assert "D1 sign" in view
    assert "D9 sign" in view
    assert "Vargottama" in view
    assert "KundliChart houses={chart.houses} planets={chart.planets}" in view
