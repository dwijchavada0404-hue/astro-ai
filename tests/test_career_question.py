from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


TEST_BIRTH = {
    "date": "2000-04-04",
    "time": "10:32:00",
    "place": "Mumbai",
}


BASE_REFERENCE = (
    "2026-08-15T12:00:00+05:30"
)


def _ask(
    question: str,
):
    response = client.post(
        "/api/v1/career-question",
        json={
            "birth": TEST_BIRTH,
            "question": question,
            "reference_moment": BASE_REFERENCE,
        },
    )

    assert response.status_code == 200

    return response.json()


def test_career_question_endpoint():
    data = _ask(
        "Will I change my job in the next 6 months?"
    )

    assert (
        data["question"]
        == "Will I change my job in the next 6 months?"
    )

    assert (
        data["reference_moment"]
        == BASE_REFERENCE
    )


def test_job_change_question_understanding():
    data = _ask(
        "Will I change my job in the next 6 months?"
    )

    intent = (
        data["understanding"]["intent"]
    )

    assert (
        intent["event"]
        == "job_change"
    )

    assert (
        intent["question_type"]
        == "probability"
    )

    assert (
        intent["direction"]
        == "change"
    )

    horizon = (
        data["understanding"][
            "forecast_horizon"
        ]
    )

    assert (
        horizon["type"]
        == "months"
    )

    assert (
        horizon["value"]
        == 6
    )


def test_job_change_resolved_forecast_range():
    data = _ask(
        "Will I change my job in the next 6 months?"
    )

    request = (
        data[
            "resolved_forecast_request"
        ]
    )

    assert (
        request["start"]
        == "2026-08-15T12:00:00+05:30"
    )

    assert (
        request["end"]
        == "2027-02-15T12:00:00+05:30"
    )

    assert (
        request["step_days"]
        == 7
    )


def test_job_change_answer():
    data = _ask(
        "Will I change my job in the next 6 months?"
    )

    answer = data["answer"]

    assert (
        answer["event"]
        == "job_change"
    )

    assert (
        answer["outcome"]
        == "very_strong"
    )

    assert (
        answer["confidence"]
        == 0.95
    )

    assert (
        answer["window"]["start"]
        == "2026-08-29"
    )

    assert (
        answer["window"]["end"]
        == "2026-11-14"
    )

    assert (
        answer["window"]["peak_date"]
        == "2026-10-24"
    )

    assert (
        answer["window"]["confirmation"]
        == "strong_confirmation"
    )


def test_promotion_question():
    data = _ask(
        "When will I get promoted?"
    )

    intent = (
        data["understanding"]["intent"]
    )

    assert (
        intent["event"]
        == "promotion_recognition"
    )

    assert (
        intent["question_type"]
        == "timing"
    )

    assert (
        intent["direction"]
        == "increase"
    )

    answer = data["answer"]

    assert (
        answer["event"]
        == "promotion_recognition"
    )


def test_salary_question():
    data = _ask(
        "Will my salary increase in the next year?"
    )

    intent = (
        data["understanding"]["intent"]
    )

    assert (
        intent["event"]
        == "income_gains"
    )

    assert (
        intent["direction"]
        == "increase"
    )

    horizon = (
        data["understanding"][
            "forecast_horizon"
        ]
    )

    assert (
        horizon["type"]
        == "years"
    )

    assert (
        horizon["value"]
        == 1
    )


def test_foreign_job_calendar_year_question():
    data = _ask(
        "Can I get a foreign job in 2027?"
    )

    intent = (
        data["understanding"]["intent"]
    )

    assert (
        intent["event"]
        == (
            "foreign_international_opportunity"
        )
    )

    assert (
        intent["direction"]
        == "occurrence"
    )

    request = (
        data[
            "resolved_forecast_request"
        ]
    )

    assert (
        request["start"]
        == "2027-01-01T00:00:00+05:30"
    )

    assert (
        request["end"]
        == "2028-01-01T00:00:00+05:30"
    )


def test_general_career_year_question():
    data = _ask(
        "How is my career in 2028?"
    )

    intent = (
        data["understanding"]["intent"]
    )

    assert (
        intent["event"]
        == "general_career"
    )

    assert (
        intent["direction"]
        == "neutral"
    )

    request = (
        data[
            "resolved_forecast_request"
        ]
    )

    assert (
        request["start"]
        == "2028-01-01T00:00:00+05:30"
    )

    assert (
        request["end"]
        == "2029-01-01T00:00:00+05:30"
    )


def test_pressure_reduction_question():
    data = _ask(
        "Will work pressure reduce in the next 3 months?"
    )

    intent = (
        data["understanding"]["intent"]
    )

    assert (
        intent["event"]
        == "career_pressure_challenge"
    )

    assert (
        intent["direction"]
        == "decrease"
    )

    assert (
        data[
            "resolved_forecast_request"
        ]["step_days"]
        == 3
    )

    answer = data["answer"]

    assert (
        answer["event"]
        == "career_pressure_challenge"
    )

    assert (
        answer["direction"]
        == "decrease"
    )


def test_career_question_requires_timezone():
    response = client.post(
        "/api/v1/career-question",
        json={
            "birth": TEST_BIRTH,
            "question": (
                "Will I change my job "
                "in the next 6 months?"
            ),
            "reference_moment": (
                "2026-08-15T12:00:00"
            ),
        },
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        "timezone offset"
        in response.json()["detail"]
    )


def test_career_question_rejects_empty_question():
    response = client.post(
        "/api/v1/career-question",
        json={
            "birth": TEST_BIRTH,
            "question": "   ",
            "reference_moment": (
                BASE_REFERENCE
            ),
        },
    )

    assert (
        response.status_code
        == 400
    )

    assert (
        "must not be empty"
        in response.json()["detail"]
    )