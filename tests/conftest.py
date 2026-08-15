import pytest

import app.services.chart_service as chart_service
import app.services.geocoding as geocoding


# =========================================================
# DETERMINISTIC TEST GEOCODING
# =========================================================

def _mock_resolve_place(
    place: str,
) -> dict:
    """
    Deterministic geocoding used only during pytest.

    Production code continues to use Nominatim normally.

    Tests must not depend on:
    - internet availability
    - Nominatim rate limits
    - external geocoding changes
    """

    normalized = (
        place
        .strip()
        .lower()
    )

    # -----------------------------------------------------
    # MUMBAI / BORIVALI TEST LOCATIONS
    # -----------------------------------------------------

    if (
        "mumbai" in normalized
        or "borivali" in normalized
    ):
        return {
            "query": place,
            "resolved_name": (
                "Mumbai, Maharashtra, India"
            ),
            "latitude": 19.0760,
            "longitude": 72.8777,
            "timezone": "Asia/Kolkata",
        }

    # -----------------------------------------------------
    # UNKNOWN TEST LOCATION
    # -----------------------------------------------------

    raise ValueError(
        f"Could not find birth place: {place}"
    )


# =========================================================
# GLOBAL PYTEST FIXTURE
# =========================================================

@pytest.fixture(
    autouse=True
)
def mock_geocoding(
    monkeypatch,
):
    """
    Replace live geocoding for every pytest test.

    chart_service imports resolve_place directly, so
    both module references are patched.
    """

    monkeypatch.setattr(
        chart_service,
        "resolve_place",
        _mock_resolve_place,
    )

    monkeypatch.setattr(
        geocoding,
        "resolve_place",
        _mock_resolve_place,
    )