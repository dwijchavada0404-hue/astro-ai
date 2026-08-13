from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


TEST_PAYLOAD = {
    "date": "2000-04-04",
    "time": "10:32:00",
    "place": "Mumbai, Maharashtra, India",
}


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "astro-ai"
    assert data["version"] == "0.4.0"


def test_chart_endpoint():
    response = client.post(
        "/api/v1/chart",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()

    assert "birth" in data
    assert "ascendant" in data
    assert "planets" in data
    assert "houses" in data
    assert "dashas" in data


def test_predictions_endpoint():
    response = client.post(
        "/api/v1/predictions",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()

    assert "birth" in data
    assert "predictions" in data
    assert isinstance(
        data["predictions"],
        list,
    )


def test_marriage_endpoint():
    response = client.post(
        "/api/v1/marriage",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()

    assert "birth" in data
    assert "ascendant" in data
    assert "marriage" in data

    marriage = data["marriage"]

    assert "reading" in marriage
    assert "predictions" in marriage
    assert "seventh_house_analysis" in marriage
    assert "planetary_analysis" in marriage
    assert "synthesis" in marriage
    assert "current_dasha" in marriage
    assert "timing" in marriage

    timing = marriage["timing"]

    assert "seventh_lord" in timing
    assert "total_periods" in timing
    assert "top_periods" in timing
    assert "synthesis" in timing

    assert timing["seventh_lord"] == "Mars"
    assert timing["total_periods"] == 90

    assert isinstance(
        timing["top_periods"],
        list,
    )

    assert len(
        timing["top_periods"]
    ) > 0


def test_marriage_primary_timing_period():
    response = client.post(
        "/api/v1/marriage",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()

    top_periods = (
        data["marriage"]
        ["timing"]
        ["top_periods"]
    )

    primary = top_periods[0]

    assert primary["mahadasha"] == "Venus"
    assert primary["antardasha"] == "Venus"
    assert primary["outlook"] == "strongly_supportive"
    assert primary["score"] > 0


def test_marriage_reading_endpoint():
    response = client.post(
        "/api/v1/marriage-reading",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()

    assert "birth" in data
    assert "reading" in data

    reading = data["reading"]

    assert reading["available"] is True

    assert "overall_outlook" in reading
    assert "marriage_timing" in reading
    assert "current_period" in reading
    assert "relationship_profile" in reading
    assert "meeting_context" in reading
    assert "distance_relocation_theme" in reading
    assert "confidence" in reading


def test_marriage_reading_primary_window():
    response = client.post(
        "/api/v1/marriage-reading",
        json=TEST_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()

    primary_window = (
        data["reading"]
        ["marriage_timing"]
        ["primary_window"]
    )

    assert primary_window["mahadasha"] == "Venus"
    assert primary_window["antardasha"] == "Venus"

    assert primary_window["start"] == "2028-03-28"

    assert (
        primary_window["outlook"]
        == "strongly_supportive"
    )