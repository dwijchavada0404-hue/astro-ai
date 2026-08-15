import json
from datetime import datetime
from zoneinfo import ZoneInfo

import app.services.chart_service as chart_service

from app.models.chart import BirthInput
from app.services.chart_service import build_chart

from app.astrology.features.marriage_forecast_v2 import (
    scan_marriage_forecast_v2,
)


# =========================================================
# TEST HELPERS
# =========================================================

def _build_reference_chart():
    """
    Build the canonical reference chart using the
    fixed Mumbai coordinates already used by the
    existing regression suite.
    """

    chart_service.resolve_place = lambda place: {
        "query": place,
        "resolved_name": (
            "Mumbai, Mumbai Suburban District, "
            "Maharashtra, 400051, India"
        ),
        "latitude": 19.054999,
        "longitude": 72.8692035,
        "timezone": "Asia/Kolkata",
    }

    with open(
        "test_request.json",
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(
            file
        )

    return build_chart(
        BirthInput(
            **payload
        )
    )


def _run_reference_forecast():
    chart = (
        _build_reference_chart()
    )

    timezone = ZoneInfo(
        "Asia/Kolkata"
    )

    start = datetime(
        2026,
        8,
        15,
        12,
        0,
        tzinfo=timezone,
    )

    end = datetime(
        2028,
        8,
        15,
        12,
        0,
        tzinfo=timezone,
    )

    return (
        scan_marriage_forecast_v2(
            chart,
            start,
            end,
            step_days=7,
        )
    )


# =========================================================
# BASIC FORECAST
# =========================================================

def test_marriage_forecast_available():

    result = (
        _run_reference_forecast()
    )

    assert (
        result[
            "available"
        ]
        is True
    )

    assert (
        result[
            "forecast_period"
        ][
            "step_days"
        ]
        == 7
    )

    assert (
        result[
            "forecast_period"
        ][
            "snapshot_count"
        ]
        > 100
    )


# =========================================================
# STRONGEST EVENT
# =========================================================

def test_marriage_forecast_strongest_event():

    result = (
        _run_reference_forecast()
    )

    assert (
        result[
            "strongest_event"
        ]
        == "marriage_timing"
    )


# =========================================================
# PRIMARY MARRIAGE WINDOW
# =========================================================

def test_primary_marriage_window():

    result = (
        _run_reference_forecast()
    )

    marriage = (
        result[
            "events"
        ][
            "marriage_timing"
        ]
    )

    assert (
        marriage[
            "available"
        ]
        is True
    )

    assert (
        marriage[
            "confirmation"
        ]
        == "strong_confirmation"
    )

    window = (
        marriage[
            "primary_window"
        ]
    )

    assert (
        window[
            "start"
        ]
        == "2028-06-10"
    )

    assert (
        window[
            "end"
        ]
        == "2028-07-29"
    )

    assert (
        window[
            "peak"
        ][
            "date"
        ]
        == "2028-07-08"
    )


# =========================================================
# PRIMARY MARRIAGE PEAK EVIDENCE
# =========================================================

def test_primary_marriage_peak_evidence():

    result = (
        _run_reference_forecast()
    )

    peak = (
        result[
            "events"
        ][
            "marriage_timing"
        ][
            "primary_window"
        ][
            "peak"
        ]
    )

    assert (
        peak[
            "period"
        ]
        == "Venus/Venus"
    )

    assert (
        peak[
            "confirmation"
        ]
        == "strong_confirmation"
    )

    assert (
        peak[
            "dasha_score"
        ]
        == 0.953
    )

    assert (
        peak[
            "transit_score"
        ]
        == 0.675
    )

    assert (
        peak[
            "raw_transit_challenge"
        ]
        == 0.239
    )


# =========================================================
# MARCH 2027 POSITIVE WINDOW
# =========================================================

def test_march_2027_remains_positive_window():

    result = (
        _run_reference_forecast()
    )

    marriage = (
        result[
            "events"
        ][
            "marriage_timing"
        ]
    )

    secondary_windows = (
        marriage[
            "secondary_windows"
        ]
    )

    march_window = next(
        window
        for window in secondary_windows
        if window[
            "start"
        ]
        == "2027-02-27"
    )

    assert (
        march_window[
            "end"
        ]
        == "2027-03-27"
    )

    assert (
        march_window[
            "peak"
        ][
            "date"
        ]
        == "2027-03-06"
    )

    assert (
        march_window[
            "peak"
        ][
            "confirmation"
        ]
        == "confirmed"
    )

    assert (
        march_window[
            "peak"
        ][
            "transit_score"
        ]
        == 0.905
    )


# =========================================================
# RELATIONSHIP COMMITMENT
# =========================================================

def test_relationship_commitment_window():

    result = (
        _run_reference_forecast()
    )

    commitment = (
        result[
            "events"
        ][
            "relationship_commitment"
        ]
    )

    assert (
        commitment[
            "available"
        ]
        is True
    )

    assert (
        commitment[
            "primary_window"
        ][
            "peak"
        ][
            "date"
        ]
        == "2028-07-08"
    )

    assert (
        commitment[
            "primary_window"
        ][
            "peak"
        ][
            "confirmation"
        ]
        == "strong_confirmation"
    )


# =========================================================
# OBSTRUCTIVE CHALLENGE WINDOW
# =========================================================

def test_obstructive_challenge_window():

    result = (
        _run_reference_forecast()
    )

    challenge = (
        result[
            "events"
        ][
            "marriage_delay_challenge"
        ]
    )

    assert (
        challenge[
            "available"
        ]
        is True
    )

    assert (
        challenge[
            "primary_window"
        ][
            "start"
        ]
        == "2027-11-27"
    )

    assert (
        challenge[
            "primary_window"
        ][
            "end"
        ]
        == "2027-12-18"
    )

    assert (
        challenge[
            "primary_window"
        ][
            "peak"
        ][
            "date"
        ]
        == "2027-11-27"
    )


# =========================================================
# STRONG POSITIVE ACTIVATION IS NOT MISLABELED AS DELAY
# =========================================================

def test_march_2027_not_primary_delay_window():

    result = (
        _run_reference_forecast()
    )

    challenge = (
        result[
            "events"
        ][
            "marriage_delay_challenge"
        ]
    )

    primary_window = (
        challenge[
            "primary_window"
        ]
    )

    assert not (
        primary_window[
            "start"
        ]
        <= "2027-03-06"
        <= primary_window[
            "end"
        ]
    )


# =========================================================
# SNAPSHOT SCORING
# =========================================================

def test_snapshot_contains_combined_layers():

    result = (
        _run_reference_forecast()
    )

    snapshots = (
        result[
            "snapshots"
        ]
    )

    snapshot = next(
        item
        for item in snapshots
        if item[
            "moment"
        ][
            :10
        ]
        == "2028-07-08"
    )

    assert (
        snapshot[
            "period"
        ]
        == "Venus/Venus"
    )

    assert (
        snapshot[
            "dasha_scores"
        ][
            "marriage_timing"
        ]
        == 0.953
    )

    assert (
        snapshot[
            "transit_scores"
        ][
            "marriage_timing"
        ]
        == 0.675
    )

    assert (
        snapshot[
            "combined_scores"
        ][
            "marriage_timing"
        ]
        == 0.768
    )

    assert (
        snapshot[
            "confirmations"
        ][
            "marriage_timing"
        ]
        == "strong_confirmation"
    )


# =========================================================
# VALIDATION
# =========================================================

def test_marriage_forecast_rejects_invalid_range():

    chart = (
        _build_reference_chart()
    )

    timezone = ZoneInfo(
        "Asia/Kolkata"
    )

    start = datetime(
        2027,
        1,
        1,
        12,
        0,
        tzinfo=timezone,
    )

    end = datetime(
        2026,
        1,
        1,
        12,
        0,
        tzinfo=timezone,
    )

    try:

        scan_marriage_forecast_v2(
            chart,
            start,
            end,
            step_days=7,
        )

    except ValueError as exc:

        assert (
            "end must be later than start"
            in str(
                exc
            )
        )

    else:

        raise AssertionError(
            "Expected ValueError for invalid range."
        )