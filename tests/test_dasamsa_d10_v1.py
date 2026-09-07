import pytest

from app.astrology.dasamsa import build_dasamsa_chart, dasamsa_longitude


def test_dasamsa_odd_sign_counts_from_same_sign():
    assert dasamsa_longitude(0.0) == pytest.approx(0.0)
    assert dasamsa_longitude(5.0) == pytest.approx(50.0)
    assert dasamsa_longitude(7.0) == pytest.approx(70.0)


def test_dasamsa_even_sign_counts_from_ninth_sign():
    assert dasamsa_longitude(30.0) == pytest.approx(270.0)
    assert dasamsa_longitude(35.0) == pytest.approx(320.0)
    assert dasamsa_longitude(47.5) == pytest.approx(85.0)


def test_dasamsa_advances_at_exact_three_degree_boundary():
    assert dasamsa_longitude(2.999999999) < 30.0
    assert dasamsa_longitude(3.0) == pytest.approx(30.0)


def test_dasamsa_wraps_at_full_zodiac_boundary():
    assert dasamsa_longitude(360.0) == pytest.approx(0.0)
    assert 0.0 <= dasamsa_longitude(359.999999) < 360.0


def test_build_dasamsa_uses_d10_lagna_for_houses():
    calculated = {
        "ascendant": {"longitude": 0.0, "sign": "Aries"},
        "planets": {
            "Sun": {"longitude": 7.0, "sign": "Aries", "retrograde": False},
            "Moon": {"longitude": 35.0, "sign": "Taurus", "retrograde": False},
            "Saturn": {"longitude": 60.0, "sign": "Gemini", "retrograde": True},
        },
    }

    d10 = build_dasamsa_chart(calculated)

    assert d10["chart"] == "D10"
    assert d10["name"] == "Dashamsha"
    assert d10["ascendant"]["sign"] == "Aries"
    assert d10["planets"]["Sun"]["sign"] == "Gemini"
    assert d10["planets"]["Sun"]["house"] == 3
    assert d10["planets"]["Moon"]["sign"] == "Aquarius"
    assert d10["planets"]["Moon"]["house"] == 11
    assert d10["planets"]["Saturn"]["retrograde"] is True
    assert d10["houses"]["1"]["sign"] == "Aries"
    assert d10["houses"]["10"]["sign"] == "Capricorn"
