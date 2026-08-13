import json

from app.models.chart import BirthInput
from app.services.chart_service import build_chart


def test_known_chart_dasha_regression():
    """
    Regression test for a known reference chart.

    This protects against unintended changes in:
    - Lahiri sidereal configuration
    - Moon longitude
    - Vimshottari Mahadasha sequence
    - current Mahadasha / Antardasha
    """

    with open(
        "test_request.json",
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(file)

    chart = build_chart(
        BirthInput(**payload)
    )

    moon = chart["planets"]["Moon"]
    dashas = chart["dashas"]
    current = dashas["current_period"]

    assert moon["longitude"] == 343.87226074

    assert (
        moon["nakshatra"]["name"]
        == "Uttara Bhadrapada"
    )

    assert (
        dashas["first_mahadasha_lord"]
        == "Saturn"
    )

    assert (
        dashas["nakshatra_elapsed_fraction"]
        == 0.79041956
    )

    assert current["mahadasha"] == "Ketu"
    assert current["antardasha"] == "Saturn"

    assert (
        current["mahadasha_start"]
        == "2021-03-28T23:13:04.517280+05:30"
    )

    assert (
        current["mahadasha_end"]
        == "2028-03-28T15:57:28.517280+05:30"
    )

    assert (
        current["antardasha_start"]
        == "2026-02-20T15:44:09.317280+05:30"
    )

    assert (
        current["antardasha_end"]
        == "2027-04-01T11:11:11.117280+05:30"
    )