from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "web" / "src" / "App.tsx"


def test_privacy_notice_does_not_claim_unverified_provider_regions():
    app = APP.read_text(encoding="utf-8")

    assert "Railway in the EU region" not in app
    assert "Auth0 in the EU region" not in app
    assert "Application data is hosted on Railway. Authentication is provided by Auth0." in app


def test_legal_notice_date_reflects_disclosure_update():
    app = APP.read_text(encoding="utf-8")

    assert "Last updated 6 September 2026" in app
