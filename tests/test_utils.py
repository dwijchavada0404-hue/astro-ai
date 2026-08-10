from app.astrology.utils import (
    nakshatra_from_longitude,
    sign_from_longitude,
)


def test_sign_zero():
    sign, degree, index = sign_from_longitude(0)
    assert sign == "Aries"
    assert degree == 0
    assert index == 0


def test_sign_30():
    sign, degree, index = sign_from_longitude(30)
    assert sign == "Taurus"
    assert degree == 0
    assert index == 1


def test_nakshatra_zero():
    result = nakshatra_from_longitude(0)
    assert result["name"] == "Ashwini"
    assert result["lord"] == "Ketu"
    assert result["pada"] == 1


def test_nakshatra_boundary():
    result = nakshatra_from_longitude(13 + 20 / 60)
    assert result["name"] == "Bharani"
    assert result["lord"] == "Venus"
