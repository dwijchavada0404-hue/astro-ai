from pathlib import Path


def test_frontend_dockerfile_promotes_public_vite_settings_into_build_stage():
    dockerfile = (Path(__file__).resolve().parents[1] / "web" / "Dockerfile").read_text()

    for variable in (
        "VITE_ASTROAI_API_URL",
        "VITE_OIDC_AUTHORITY",
        "VITE_OIDC_CLIENT_ID",
        "VITE_OIDC_SCOPE",
        "VITE_OIDC_AUDIENCE",
    ):
        assert f"ARG {variable}" in dockerfile
        assert variable + "=${" + variable + "}" in dockerfile
