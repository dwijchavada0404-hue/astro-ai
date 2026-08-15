from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


TEST_BIRTH = {
    "date": "2000-04-04",
    "time": "10:32:00",
    "place": "Mumbai",
}


TEST_PAYLOAD = {
    "birth": TEST_BIRTH,
    "transit_moment": "2026-08-15T12:00:00+05:30",
}


def _response():
    response = client.post(
        "/api/v1/career-transits",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    return response.json()


def test_career_transit_endpoint():
    data = _response()

    assert (
        data["transit_moment"]
        == "2026-08-15T12:00:00+05:30"
    )

    assert (
        data["current_dasha"]["mahadasha"]
        == "Ketu"
    )

    assert (
        data["current_dasha"]["antardasha"]
        == "Saturn"
    )


def test_career_transit_job_change_confirmation():
    data = _response()

    event = (
        data["career_events"][
            "dasha_transit_confirmation"
        ]["events"]["job_change"]
    )

    assert (
        event["period"]
        == "Ketu/Saturn"
    )

    assert (
        event["confirmation"]
        == "strong_confirmation"
    )

    assert (
        event["specific_transit_confirmation"]
        is True
    )

    assert event["dasha_score"] >= 1.5
    assert event["transit_score"] >= 2.0


def test_career_pressure_confirmation():
    data = _response()

    event = (
        data["career_events"][
            "dasha_transit_confirmation"
        ]["events"][
            "career_pressure_challenge"
        ]
    )

    assert (
        event["confirmation"]
        == "strong_confirmation"
    )

    assert (
        event["specific_transit_confirmation"]
        is True
    )


def test_promotion_requires_specific_transit():
    data = _response()

    event = (
        data["career_events"][
            "dasha_transit_confirmation"
        ]["events"][
            "promotion_recognition"
        ]
    )

    assert (
        event["confirmation"]
        == "dasha_only"
    )

    assert (
        event["specific_transit_confirmation"]
        is False
    )


def test_foreign_opportunity_requires_specific_transit():
    data = _response()

    event = (
        data["career_events"][
            "dasha_transit_confirmation"
        ]["events"][
            "foreign_international_opportunity"
        ]
    )

    assert (
        event["confirmation"]
        == "dasha_only"
    )

    assert (
        event["specific_transit_confirmation"]
        is False
    )


def test_income_gains_remains_weak():
    data = _response()

    event = (
        data["career_events"][
            "dasha_transit_confirmation"
        ]["events"][
            "income_gains"
        ]
    )

    assert (
        event["confirmation"]
        == "weak"
    )


def test_rahu_transits_natal_tenth_house():
    data = _response()

    rahu = (
        data["transits"][
            "natal_house_mapping"
        ]["planets"]["Rahu"]
    )

    assert rahu["sign"] == "Aquarius"
    assert rahu["natal_house"] == 10


def test_saturn_transits_natal_eleventh_house():
    data = _response()

    saturn = (
        data["transits"][
            "natal_house_mapping"
        ]["planets"]["Saturn"]
    )

    assert saturn["sign"] == "Pisces"
    assert saturn["natal_house"] == 11
    assert saturn["retrograde"] is True


def test_transit_moment_requires_timezone():
    payload = {
        "birth": TEST_BIRTH,
        "transit_moment": "2026-08-15T12:00:00",
    }

    response = client.post(
        "/api/v1/career-transits",
        json=payload,
    )

    assert response.status_code == 400

    assert (
        "timezone offset"
        in response.json()["detail"]
    )


def test_requested_date_controls_dasha():
    payload = {
        "birth": TEST_BIRTH,
        "transit_moment": "2027-08-15T12:00:00+05:30",
    }

    response = client.post(
        "/api/v1/career-transits",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["current_dasha"]["mahadasha"]
        == "Ketu"
    )

    assert (
        data["current_dasha"]["antardasha"]
        == "Mercury"
    )