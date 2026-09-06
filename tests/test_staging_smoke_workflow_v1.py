from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "staging-smoke.yml"


def test_staging_smoke_runs_after_successful_main_push_ci():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_run:" in workflow
    assert "- Tests" in workflow
    assert "- completed" in workflow
    assert "github.event.workflow_run.conclusion == 'success'" in workflow
    assert "github.event.workflow_run.head_branch == 'main'" in workflow
    assert "github.event.workflow_run.event == 'push'" in workflow


def test_staging_smoke_keeps_manual_and_scheduled_checks():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert 'cron: "17 */6 * * *"' in workflow


def test_staging_smoke_allows_deployment_settle_time():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "timeout-minutes: 10" in workflow
    assert "for attempt in 1 2 3 4 5 6 7 8 9 10 11 12; do" in workflow
    assert "retrying in 30 seconds" in workflow
