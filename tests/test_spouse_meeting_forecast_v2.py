import json
from datetime import datetime
from zoneinfo import ZoneInfo

import app.services.chart_service as chart_service

from app.models.chart import BirthInput
from app.services.chart_service import build_chart

from app.astrology.features.spouse_meeting_forecast_v2 import (
    scan_spouse_meeting_forecast_v2,
    score_spouse_meeting_moment,
)


def _build_reference_chart():

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


def _tz():
    return ZoneInfo(
        "Asia/Kolkata"
    )


def test_spouse_meeting_peak_date():

    chart = _build_reference_chart()

    result = (
        scan_spouse_meeting_forecast_v2(
            chart,
            datetime(
                2026,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            datetime(
                2029,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            step_days=7,
        )
    )

    assert result[
        "forecast_available"
    ] is True

    assert (
        result[
            "primary_window"
        ][
            "peak"
        ][
            "date"
        ]
        == "2027-03-06"
    )

    assert (
        result[
            "primary_window"
        ][
            "peak"
        ][
            "confirmation"
        ]
        == "strong_meeting_signal"
    )


def test_spouse_meeting_primary_window_is_narrow():

    chart = _build_reference_chart()

    result = (
        scan_spouse_meeting_forecast_v2(
            chart,
            datetime(
                2026,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            datetime(
                2029,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            step_days=7,
        )
    )

    primary = (
        result[
            "primary_window"
        ]
    )

    assert (
        primary[
            "start"
        ]
        == "2027-01-30"
    )

    assert (
        primary[
            "end"
        ]
        == "2027-04-03"
    )

    assert (
        primary[
            "snapshot_count"
        ]
        == 9
    )


def test_spouse_meeting_peak_score():

    chart = _build_reference_chart()

    result = (
        scan_spouse_meeting_forecast_v2(
            chart,
            datetime(
                2026,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            datetime(
                2029,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            step_days=7,
        )
    )

    peak = (
        result[
            "primary_window"
        ][
            "peak"
        ]
    )

    assert (
        peak[
            "score"
        ]
        == 0.889
    )

    assert (
        peak[
            "dasha_score"
        ]
        == 1.0
    )

    assert (
        peak[
            "transit_score"
        ]
        == 0.851
    )


def test_spouse_meeting_peak_house_pattern():

    chart = _build_reference_chart()

    result = (
        scan_spouse_meeting_forecast_v2(
            chart,
            datetime(
                2026,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            datetime(
                2029,
                8,
                15,
                12,
                0,
                tzinfo=_tz(),
            ),
            step_days=7,
        )
    )

    houses = (
        result[
            "primary_window"
        ][
            "peak"
        ][
            "houses"
        ]
    )

    assert houses[
        "Venus"
    ] == 7

    assert houses[
        "Moon"
    ] == 7

    assert houses[
        "Mercury"
    ] == 7

    assert houses[
        "Jupiter"
    ] == 1


def test_spouse_meeting_single_moment_scoring():

    chart = _build_reference_chart()

    snapshot = (
        score_spouse_meeting_moment(
            chart,
            datetime(
                2027,
                3,
                6,
                12,
                0,
                tzinfo=_tz(),
            ),
        )
    )

    assert (
        snapshot[
            "period"
        ]
        == "Venus/Venus"
    )

    assert (
        snapshot[
            "combined_score"
        ]
        == 0.889
    )

    assert (
        snapshot[
            "confirmation"
        ]
        == "strong_meeting_signal"
    )


def test_spouse_meeting_requires_timezone():

    chart = _build_reference_chart()

    try:

        scan_spouse_meeting_forecast_v2(
            chart,
            datetime(
                2026,
                8,
                15,
                12,
                0,
            ),
            datetime(
                2027,
                8,
                15,
                12,
                0,
            ),
            step_days=7,
        )

    except ValueError as exc:

        assert (
            "timezone offset"
            in str(
                exc
            )
        )

    else:

        raise AssertionError(
            "Expected timezone validation error."
        )
