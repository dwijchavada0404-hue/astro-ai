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
    "start": "2026-08-15T12:00:00+05:30",
    "end": "2027-02-15T12:00:00+05:30",
    "step_days": 7,
}


def _response():
    response = client.post(
        "/api/v1/career-forecast",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    return response.json()


def test_career_forecast_endpoint():
    data = _response()

    assert (
        data["request"]["start"]
        == "2026-08-15T12:00:00+05:30"
    )

    assert (
        data["request"]["end"]
        == "2027-02-15T12:00:00+05:30"
    )

    assert (
        data["request"]["step_days"]
        == 7
    )


def test_career_forecast_scan_metadata():
    data = _response()

    metadata = data[
        "scan_metadata"
    ]

    assert (
        metadata["available"]
        is True
    )

    assert (
        metadata["snapshot_count"]
        == 27
    )

    assert (
        metadata["step_days"]
        == 7
    )


def test_job_change_is_strongest_event():
    data = _response()

    overall = (
        data["forecast"][
            "overall"
        ]
    )

    assert (
        overall["strongest_event"]
        == "job_change"
    )

    assert (
        overall["outlook"]
        == "professional_transition_emphasised"
    )


def test_job_change_primary_window():
    data = _response()

    job = (
        data["forecast"][
            "events"
        ]["job_change"]
    )

    assert (
        job["available"]
        is True
    )

    assert (
        job["outlook"]
        == "very_strong"
    )

    assert (
        job["window"]["start"]
        == "2026-08-29"
    )

    assert (
        job["window"]["end"]
        == "2026-11-14"
    )

    assert (
        job["window"]["peak_date"]
        == "2026-10-24"
    )

    assert (
        job["window"]["period"]
        == "Ketu/Saturn"
    )

    assert (
        job["window"]["confirmation"]
        == "strong_confirmation"
    )


def test_promotion_window_is_separate():
    data = _response()

    promotion = (
        data["forecast"][
            "events"
        ]["promotion_recognition"]
    )

    assert (
        promotion["available"]
        is True
    )

    assert (
        promotion["outlook"]
        == "strong"
    )

    assert (
        promotion["window"]["peak_date"]
        == "2027-02-13"
    )

    assert (
        promotion["window"]["confirmation"]
        == "confirmed"
    )


def test_income_has_no_strong_window():
    data = _response()

    income = (
        data["forecast"][
            "events"
        ]["income_gains"]
    )

    assert (
        income["available"]
        is False
    )

    assert (
        income["outlook"]
        == "no_strong_window"
    )

    assert (
        income["window"]
        == {}
    )


def test_foreign_theme_is_not_fully_confirmed():
    data = _response()

    foreign = (
        data["forecast"][
            "events"
        ][
            "foreign_international_opportunity"
        ]
    )

    assert (
        foreign["available"]
        is True
    )

    assert (
        foreign["outlook"]
        == "moderate"
    )

    assert (
        foreign["window"]["confirmation"]
        == "dasha_only"
    )


def test_career_pressure_window():
    data = _response()

    pressure = (
        data["forecast"][
            "events"
        ][
            "career_pressure_challenge"
        ]
    )

    assert (
        pressure["available"]
        is True
    )

    assert (
        pressure["outlook"]
        == "very_strong"
    )

    assert (
        pressure["window"]["start"]
        == "2026-08-15"
    )

    assert (
        pressure["window"]["confirmation"]
        == "strong_confirmation"
    )


def test_forecast_requires_timezone():
    payload = {
        "birth": TEST_BIRTH,
        "start": "2026-08-15T12:00:00",
        "end": "2027-02-15T12:00:00+05:30",
        "step_days": 7,
    }

    response = client.post(
        "/api/v1/career-forecast",
        json=payload,
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        "timezone offset"
        in response.json()["detail"]
    )


def test_forecast_rejects_invalid_date_range():
    payload = {
        "birth": TEST_BIRTH,
        "start": "2027-02-15T12:00:00+05:30",
        "end": "2026-08-15T12:00:00+05:30",
        "step_days": 7,
    }

    response = client.post(
        "/api/v1/career-forecast",
        json=payload,
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        "end must be later than start"
        in response.json()["detail"]
    )


def test_forecast_rejects_invalid_step_days():
    payload = {
        "birth": TEST_BIRTH,
        "start": "2026-08-15T12:00:00+05:30",
        "end": "2027-02-15T12:00:00+05:30",
        "step_days": 0,
    }

    response = client.post(
        "/api/v1/career-forecast",
        json=payload,
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        "step_days must be at least 1"
        in response.json()["detail"]
    )