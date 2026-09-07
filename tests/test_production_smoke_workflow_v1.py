from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "production-smoke.yml"
SCRIPT = ROOT / "scripts" / "smoke_production.sh"


def test_production_smoke_is_manual_and_uses_explicit_repository_variables():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "workflow_run:" not in workflow
    assert "schedule:" not in workflow
    assert "vars.ASTROAI_PRODUCTION_FRONTEND_URL" in workflow
    assert "vars.ASTROAI_PRODUCTION_API_URL" in workflow
    assert "bash scripts/smoke_production.sh" in workflow


def test_production_smoke_requires_production_identity_and_storage_boundaries():
    script = SCRIPT.read_text(encoding="utf-8")

    assert "ASTROAI_PRODUCTION_FRONTEND_URL is required" in script
    assert "ASTROAI_PRODUCTION_API_URL is required" in script
    assert '"environment"[[:space:]]*:[[:space:]]*"production"' in script
    assert '"profile_database"[[:space:]]*:[[:space:]]*"ok"' in script
    assert 'test "$auth_status" = "401"' in script
    assert "access-control-allow-origin" in script
    assert "Production smoke URLs must not point to localhost" in script


def test_production_smoke_allows_deployment_settle_time():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "timeout-minutes: 10" in workflow
    assert "for attempt in 1 2 3 4 5 6 7 8 9 10 11 12; do" in workflow
    assert "retrying in 30 seconds" in workflow
