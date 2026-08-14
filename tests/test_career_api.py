from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


TEST_PAYLOAD = {
    "date": "2000-04-04",
    "time": "10:32:00",
    "place": "Mumbai",
}


def test_career_endpoint_returns_200():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200


def test_career_foundation_regression():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    data = response.json()

    foundation = (
        data["career"]["reading"][
            "career_foundation"
        ]
    )

    assert (
        foundation["tenth_house_sign"]
        == "Aquarius"
    )

    assert (
        foundation["tenth_lord"]
        == "Saturn"
    )

    assert (
        foundation["tenth_lord_house"]
        == 12
    )

    assert (
        foundation["tenth_lord_sign"]
        == "Aries"
    )

    assert (
        "Mercury"
        in foundation[
            "tenth_house_occupants"
        ]
    )


def test_current_career_dasha_regression():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    data = response.json()

    current = (
        data["career"]["reading"][
            "current_period"
        ]
    )

    assert (
        current["period"]
        == "Ketu/Saturn"
    )

    assert (
        current["start"]
        == "2026-02-20"
    )

    assert (
        current["end"]
        == "2027-04-01"
    )

    assert (
        current[
            "direct_tenth_lord_activation"
        ]
        is True
    )

    assert (
        current[
            "direct_tenth_house_activation"
        ]
        is False
    )


def test_near_term_career_progression():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    data = response.json()

    windows = (
        data["career"]["reading"][
            "near_term_progression"
        ]["windows"]
    )

    assert len(windows) >= 2

    assert (
        windows[0]["period"]
        == "Ketu/Mercury"
    )

    assert (
        windows[0]["start"]
        == "2027-04-01"
    )

    assert (
        windows[0][
            "direct_tenth_house_activation"
        ]
        is True
    )

    assert (
        windows[1]["period"]
        == "Venus/Venus"
    )

    assert (
        windows[1]["start"]
        == "2028-03-28"
    )


def test_nearest_strong_career_window():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    data = response.json()

    window = (
        data["career"]["reading"][
            "career_timing"
        ]["nearest_strong_window"]
    )

    assert (
        window["period"]
        == "Venus/Venus"
    )

    assert (
        window["start"]
        == "2028-03-28"
    )

    assert (
        window["end"]
        == "2031-07-29"
    )

    assert (
        window["outlook"]
        == "strongly_supportive"
    )


def test_strongest_long_term_career_window():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    data = response.json()

    window = (
        data["career"]["reading"][
            "career_timing"
        ]["strongest_long_term_window"]
    )

    assert (
        window["period"]
        == "Venus/Mercury"
    )

    assert (
        window["start"]
        == "2044-03-28"
    )

    assert (
        window["end"]
        == "2047-01-27"
    )

    assert (
        window[
            "direct_tenth_house_activation"
        ]
        is True
    )


def test_career_outlook_and_challenge():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    data = response.json()

    overall = (
        data["career"]["reading"][
            "overall_outlook"
        ]
    )

    assert (
        overall["outlook"]
        == "favourable"
    )

    assert (
        overall["confidence"]
        >= 0.8
    )

    challenges = overall[
        "challenges"
    ]

    assert any(
        "Saturn is debilitated in Aries"
        in challenge
        for challenge in challenges
    )


def test_career_endpoint_contains_full_layers():
    response = client.post(
        "/api/v1/career",
        json=TEST_PAYLOAD,
    )

    data = response.json()

    career = data["career"]

    assert "reading" in career
    assert "reasoning" in career
    assert "interpretation" in career
    assert "planetary_analysis" in career
    assert "synthesis" in career
    assert "current_dasha" in career
    assert "timing" in career

    assert (
        career["timing"]["tenth_lord"]
        == "Saturn"
    )

    assert (
        career["timing"]["total_periods"]
        == 90
    )