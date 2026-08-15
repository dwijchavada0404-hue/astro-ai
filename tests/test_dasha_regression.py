import json

from app.models.chart import BirthInput
from app.services.chart_service import build_chart


# =========================================================
# CANONICAL REFERENCE PLACE
# =========================================================

REFERENCE_PLACE = {
    "query": "Mumbai, Maharashtra, India",
    "resolved_name": (
        "Mumbai, Mumbai Suburban District, "
        "Maharashtra, 400051, India"
    ),
    "latitude": 19.054999,
    "longitude": 72.8692035,
    "timezone": "Asia/Kolkata",
}


# =========================================================
# CANONICAL CHART REGRESSION
# =========================================================

def test_known_chart_dasha_regression(
    monkeypatch,
):
    """
    Regression test for the canonical AstroAI
    reference chart.

    Reference birth details:

        Date:
            2000-04-04

        Time:
            14:04

        Place:
            Mumbai, Maharashtra, India

        Fixed coordinates:
            19.054999 N
            72.8692035 E

        Timezone:
            Asia/Kolkata

    Why the place is fixed:

    This test is intended to protect the astrology
    calculation engine, not the external geocoding
    provider.

    Live Nominatim results for a city-level query can
    change slightly over time. Even a small coordinate
    change can slightly alter the calculated ascendant.

    Therefore this regression test deliberately freezes
    the reference coordinates.

    This protects against unintended changes in:

        - Lahiri sidereal configuration
        - Moon longitude
        - Moon sign
        - Nakshatra
        - Ascendant
        - Vimshottari Mahadasha
        - Vimshottari Antardasha
    """

    # -----------------------------------------------------
    # FREEZE GEOLOCATION
    # -----------------------------------------------------

    monkeypatch.setattr(
        "app.services.chart_service.resolve_place",
        lambda place: {
            **REFERENCE_PLACE,
            "query": place,
        },
    )

    # -----------------------------------------------------
    # LOAD CANONICAL BIRTH INPUT
    # -----------------------------------------------------

    with open(
        "test_request.json",
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(
            file
        )

    chart = build_chart(
        BirthInput(
            **payload
        )
    )

    moon = chart[
        "planets"
    ][
        "Moon"
    ]

    ascendant = chart[
        "ascendant"
    ]

    dashas = chart[
        "dashas"
    ]

    current = dashas[
        "current_period"
    ]

    birth = chart[
        "birth"
    ]

    # =====================================================
    # BIRTH INPUT REGRESSION
    # =====================================================

    assert (
        birth[
            "date"
        ]
        == "2000-04-04"
    )

    assert (
        birth[
            "time"
        ]
        == "14:04:00"
    )

    assert (
        birth[
            "timezone"
        ]
        == "Asia/Kolkata"
    )

    assert (
        birth[
            "latitude"
        ]
        == 19.054999
    )

    assert (
        birth[
            "longitude"
        ]
        == 72.8692035
    )

    # =====================================================
    # MOON REGRESSION
    # =====================================================

    assert (
        moon[
            "longitude"
        ]
        == 345.88769277
    )

    assert (
        moon[
            "sign"
        ]
        == "Pisces"
    )

    assert (
        moon[
            "degree_in_sign"
        ]
        == 15.88769277
    )

    assert (
        moon[
            "nakshatra"
        ][
            "name"
        ]
        == "Uttara Bhadrapada"
    )

    assert (
        moon[
            "nakshatra"
        ][
            "lord"
        ]
        == "Saturn"
    )

    assert (
        moon[
            "nakshatra"
        ][
            "number"
        ]
        == 26
    )

    assert (
        moon[
            "nakshatra"
        ][
            "pada"
        ]
        == 4
    )

    # =====================================================
    # ASCENDANT REGRESSION
    # =====================================================

    assert (
        ascendant[
            "longitude"
        ]
        == 104.55673681
    )

    assert (
        ascendant[
            "sign"
        ]
        == "Cancer"
    )

    assert (
        ascendant[
            "degree_in_sign"
        ]
        == 14.55673681
    )

    # =====================================================
    # CURRENT MAHADASHA REGRESSION
    # =====================================================

    assert (
        current[
            "mahadasha"
        ]
        == "Venus"
    )

    assert (
        current[
            "mahadasha_start"
        ]
        == "2025-05-14T20:08:17.659569+05:30"
    )

    assert (
        current[
            "mahadasha_end"
        ]
        == "2045-05-14T16:32:17.659569+05:30"
    )

    # =====================================================
    # CURRENT ANTARDASHA REGRESSION
    # =====================================================

    assert (
        current[
            "antardasha"
        ]
        == "Venus"
    )

    assert (
        current[
            "antardasha_start"
        ]
        == "2025-05-14T20:08:17.659569+05:30"
    )

    assert (
        current[
            "antardasha_end"
        ]
        == "2028-09-13T07:32:17.659569+05:30"
    )