import pytest

from app.astrology.navamsa import build_navamsa_chart, navamsa_longitude


def test_navamsa_longitude_matches_classical_start_sign_rules():
    assert navamsa_longitude(0.0) == pytest.approx(0.0)       # Aries movable -> Aries
    assert navamsa_longitude(30.0) == pytest.approx(270.0)    # Taurus fixed -> Capricorn
    assert navamsa_longitude(60.0) == pytest.approx(180.0)    # Gemini dual -> Libra


def test_navamsa_advances_at_exact_three_degree_twenty_minute_boundary():
    segment = 30.0 / 9.0
    assert navamsa_longitude(segment - 1e-9) < 30.0
    assert navamsa_longitude(segment) == pytest.approx(30.0)


def test_navamsa_wraps_cleanly_at_full_zodiac_boundary():
    assert navamsa_longitude(360.0) == pytest.approx(0.0)
    assert 0.0 <= navamsa_longitude(359.999999) < 360.0


def test_build_navamsa_uses_d9_lagna_for_whole_sign_houses_and_marks_vargottama():
    calculated = {
        "ascendant": {"longitude": 0.0, "sign": "Aries"},
        "planets": {
            "Sun": {"longitude": 0.0, "sign": "Aries", "retrograde": False},
            "Moon": {"longitude": 30.0, "sign": "Taurus", "retrograde": False},
            "Saturn": {"longitude": 60.0, "sign": "Gemini", "retrograde": True},
        },
    }

    d9 = build_navamsa_chart(calculated)

    assert d9["chart"] == "D9"
    assert d9["name"] == "Navamsa"
    assert d9["ascendant"]["sign"] == "Aries"
    assert d9["ascendant"]["vargottama"] is True
    assert d9["planets"]["Sun"]["sign"] == "Aries"
    assert d9["planets"]["Sun"]["house"] == 1
    assert d9["planets"]["Sun"]["vargottama"] is True
    assert d9["planets"]["Moon"]["sign"] == "Capricorn"
    assert d9["planets"]["Moon"]["house"] == 10
    assert d9["planets"]["Moon"]["vargottama"] is False
    assert d9["planets"]["Saturn"]["sign"] == "Libra"
    assert d9["planets"]["Saturn"]["house"] == 7
    assert d9["planets"]["Saturn"]["retrograde"] is True
    assert d9["houses"]["1"]["sign"] == "Aries"
    assert d9["houses"]["7"]["sign"] == "Libra"
