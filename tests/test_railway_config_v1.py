from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_railway_gates_deployments_on_database_readiness():
    config = tomllib.loads((ROOT / "railway.toml").read_text(encoding="utf-8"))
    deploy = config["deploy"]
    assert deploy["healthcheckPath"] == "/readyz"
    assert deploy["numReplicas"] == 1
    assert deploy["restartPolicyType"] == "ON_FAILURE"
