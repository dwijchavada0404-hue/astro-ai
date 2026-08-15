from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.spouse_meeting_forecast_v1 import (
    score_spouse_meeting_moment,
)


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_dict(
    value: Any,
) -> dict[str, Any]:

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def _require_timezone(
    value: datetime,
    field_name: str,
) -> None:

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            f"{field_name} must include a timezone offset."
        )


# =========================================================
# SCORE CLASSIFICATION
# =========================================================

def _classify_score(
    score: float,
) -> str:

    if score >= 0.82:
        return "very_strong"

    if score >= 0.70:
        return "strong"

    if score >= 0.60:
        return "moderate"

    if score >= 0.52:
        return "supportive"

    return "weak"


# =========================================================
# LOCAL PEAK DETECTION
# =========================================================

def _find_local_peaks(
    snapshots: list[dict[str, Any]],
    radius: int = 4,
    minimum_peak_score: float = 0.62,
) -> list[int]:
    """
    Identify genuine local activation peaks instead of
    treating every continuously supportive week as part of
    one giant forecast window.

    radius=4 means each snapshot is compared with roughly
    four weeks on either side for a weekly scan.
    """

    peak_indexes = []

    for index, snapshot in enumerate(
        snapshots
    ):

        score = _safe_float(
            snapshot.get(
                "combined_score"
            )
        )

        if score < minimum_peak_score:
            continue

        start_index = max(
            0,
            index - radius,
        )

        end_index = min(
            len(
                snapshots
            ),
            index + radius + 1,
        )

        neighbourhood = (
            snapshots[
                start_index:
                end_index
            ]
        )

        neighbourhood_scores = [
            _safe_float(
                item.get(
                    "combined_score"
                )
            )
            for item in neighbourhood
        ]

        local_maximum = max(
            neighbourhood_scores
        )

        if score < local_maximum:
            continue

        # Avoid retaining consecutive equal-score plateau
        # snapshots as separate peaks.

        if peak_indexes:

            previous_peak_index = (
                peak_indexes[
                    -1
                ]
            )

            previous_peak = (
                snapshots[
                    previous_peak_index
                ]
            )

            previous_score = (
                _safe_float(
                    previous_peak.get(
                        "combined_score"
                    )
                )
            )

            if (
                index
                - previous_peak_index
                <= radius
                and abs(
                    score
                    - previous_score
                )
                < 0.001
            ):
                continue

        peak_indexes.append(
            index
        )

    return peak_indexes


# =========================================================
# PEAK WINDOW BOUNDARIES
# =========================================================

def _expand_peak_window(
    snapshots: list[dict[str, Any]],
    peak_index: int,
    step_days: int,
) -> dict[str, Any]:
    """
    Expand around a local peak while support remains
    meaningful, but cap the search radius so a sustained
    Dasha period cannot create a six-month "meeting window".
    """

    support_floor = 0.52

    max_radius_days = 35

    peak_snapshot = (
        snapshots[
            peak_index
        ]
    )

    peak_moment = datetime.fromisoformat(
        str(
            peak_snapshot[
                "moment"
            ]
        )
    )

    left_index = (
        peak_index
    )

    while left_index > 0:

        candidate_index = (
            left_index
            - 1
        )

        candidate = (
            snapshots[
                candidate_index
            ]
        )

        candidate_moment = (
            datetime.fromisoformat(
                str(
                    candidate[
                        "moment"
                    ]
                )
            )
        )

        distance_days = (
            peak_moment
            - candidate_moment
        ).days

        candidate_score = (
            _safe_float(
                candidate.get(
                    "combined_score"
                )
            )
        )

        if (
            distance_days
            > max_radius_days
        ):
            break

        if (
            candidate_score
            < support_floor
        ):
            break

        left_index = (
            candidate_index
        )

    right_index = (
        peak_index
    )

    while (
        right_index
        < len(
            snapshots
        )
        - 1
    ):

        candidate_index = (
            right_index
            + 1
        )

        candidate = (
            snapshots[
                candidate_index
            ]
        )

        candidate_moment = (
            datetime.fromisoformat(
                str(
                    candidate[
                        "moment"
                    ]
                )
            )
        )

        distance_days = (
            candidate_moment
            - peak_moment
        ).days

        candidate_score = (
            _safe_float(
                candidate.get(
                    "combined_score"
                )
            )
        )

        if (
            distance_days
            > max_radius_days
        ):
            break

        if (
            candidate_score
            < support_floor
        ):
            break

        right_index = (
            candidate_index
        )

    group = (
        snapshots[
            left_index:
            right_index + 1
        ]
    )

    combined_scores = [
        _safe_float(
            item.get(
                "combined_score"
            )
        )
        for item in group
    ]

    transit_scores = [
        _safe_float(
            item.get(
                "transit_score"
            )
        )
        for item in group
    ]

    challenge_scores = [
        _safe_float(
            item.get(
                "challenge_score"
            )
        )
        for item in group
    ]

    average_score = (
        sum(
            combined_scores
        )
        / len(
            combined_scores
        )
    )

    average_transit = (
        sum(
            transit_scores
        )
        / len(
            transit_scores
        )
    )

    average_challenge = (
        sum(
            challenge_scores
        )
        / len(
            challenge_scores
        )
    )

    start_moment = (
        datetime.fromisoformat(
            str(
                group[
                    0
                ][
                    "moment"
                ]
            )
        )
    )

    last_moment = (
        datetime.fromisoformat(
            str(
                group[
                    -1
                ][
                    "moment"
                ]
            )
        )
    )

    end_moment = (
        last_moment
        + timedelta(
            days=step_days,
        )
    )

    peak_transit = _safe_dict(
        peak_snapshot.get(
            "transit"
        )
    )

    return {
        "event": (
            "spouse_meeting"
        ),

        "start": (
            start_moment.date().isoformat()
        ),

        "end": (
            end_moment.date().isoformat()
        ),

        "strength": (
            _classify_score(
                average_score
            )
        ),

        "average_score": round(
            average_score,
            3,
        ),

        "average_transit_score": round(
            average_transit,
            3,
        ),

        "average_challenge_score": round(
            average_challenge,
            3,
        ),

        "peak": {
            "date": (
                peak_moment.date().isoformat()
            ),

            "period": (
                peak_snapshot.get(
                    "period"
                )
            ),

            "score": round(
                _safe_float(
                    peak_snapshot.get(
                        "combined_score"
                    )
                ),
                3,
            ),

            "strength": (
                _classify_score(
                    _safe_float(
                        peak_snapshot.get(
                            "combined_score"
                        )
                    )
                )
            ),

            "confirmation": (
                peak_snapshot.get(
                    "confirmation"
                )
            ),

            "dasha_score": (
                peak_snapshot.get(
                    "dasha_score"
                )
            ),

            "transit_score": (
                peak_snapshot.get(
                    "transit_score"
                )
            ),

            "challenge_score": (
                peak_snapshot.get(
                    "challenge_score"
                )
            ),

            "houses": (
                peak_transit.get(
                    "houses",
                    {},
                )
            ),
        },

        "snapshot_count": (
            len(
                group
            )
        ),
    }


# =========================================================
# DUPLICATE WINDOW REMOVAL
# =========================================================

def _remove_duplicate_windows(
    windows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Local peaks close to one another can produce almost
    identical expanded windows. Retain only the strongest
    representative.
    """

    ranked = sorted(
        windows,
        key=lambda item: (
            _safe_float(
                _safe_dict(
                    item.get(
                        "peak"
                    )
                ).get(
                    "score"
                )
            ),
            _safe_float(
                item.get(
                    "average_score"
                )
            ),
        ),
        reverse=True,
    )

    accepted = []

    for window in ranked:

        peak = _safe_dict(
            window.get(
                "peak"
            )
        )

        peak_date_raw = (
            peak.get(
                "date"
            )
        )

        if not isinstance(
            peak_date_raw,
            str,
        ):
            continue

        peak_date = datetime.fromisoformat(
            peak_date_raw
        )

        too_close = False

        for existing in accepted:

            existing_peak = (
                _safe_dict(
                    existing.get(
                        "peak"
                    )
                )
            )

            existing_date_raw = (
                existing_peak.get(
                    "date"
                )
            )

            if not isinstance(
                existing_date_raw,
                str,
            ):
                continue

            existing_date = (
                datetime.fromisoformat(
                    existing_date_raw
                )
            )

            separation_days = abs(
                (
                    peak_date
                    - existing_date
                ).days
            )

            # Peaks within six weeks represent the same
            # broad activation cluster.

            if separation_days <= 42:

                too_close = True

                break

        if not too_close:

            accepted.append(
                window
            )

    return accepted


# =========================================================
# WINDOW BUILDER
# =========================================================

def _build_peak_windows(
    snapshots: list[dict[str, Any]],
    step_days: int,
) -> list[dict[str, Any]]:

    peak_indexes = (
        _find_local_peaks(
            snapshots
        )
    )

    windows = [
        _expand_peak_window(
            snapshots,
            peak_index,
            step_days,
        )
        for peak_index
        in peak_indexes
    ]

    return (
        _remove_duplicate_windows(
            windows
        )
    )


# =========================================================
# MAIN FORECAST
# =========================================================

def scan_spouse_meeting_forecast_v2(
    chart: dict[str, Any],
    start: datetime,
    end: datetime,
    step_days: int = 7,
) -> dict[str, Any]:

    if not isinstance(
        chart,
        dict,
    ):
        raise ValueError(
            "chart must be a dictionary."
        )

    if not isinstance(
        start,
        datetime,
    ):
        raise ValueError(
            "start must be a datetime."
        )

    if not isinstance(
        end,
        datetime,
    ):
        raise ValueError(
            "end must be a datetime."
        )

    _require_timezone(
        start,
        "start",
    )

    _require_timezone(
        end,
        "end",
    )

    if end <= start:

        raise ValueError(
            "end must be later than start."
        )

    if step_days < 1:

        raise ValueError(
            "step_days must be at least 1."
        )

    if step_days > 31:

        raise ValueError(
            "step_days must not exceed 31."
        )

    snapshots = []

    moment = (
        start
    )

    while moment <= end:

        snapshots.append(
            score_spouse_meeting_moment(
                chart,
                moment,
            )
        )

        moment = (
            moment
            + timedelta(
                days=step_days,
            )
        )

    windows = (
        _build_peak_windows(
            snapshots,
            step_days,
        )
    )

    if not windows:

        return {
            "available": True,

            "event": (
                "spouse_meeting"
            ),

            "forecast_available": (
                False
            ),

            "outlook": (
                "no_strong_window"
            ),

            "confidence": (
                0.4
            ),

            "summary": (
                "No sufficiently strong spouse-meeting "
                "window was identified in the scanned "
                "period."
            ),

            "primary_window": {},

            "secondary_windows": [],

            "forecast_period": {
                "start": (
                    start.isoformat()
                ),

                "end": (
                    end.isoformat()
                ),

                "step_days": (
                    step_days
                ),

                "snapshot_count": (
                    len(
                        snapshots
                    )
                ),
            },

            "snapshots": (
                snapshots
            ),
        }

    primary = (
        windows[
            0
        ]
    )

    peak = _safe_dict(
        primary.get(
            "peak"
        )
    )

    peak_score = _safe_float(
        peak.get(
            "score"
        )
    )

    if peak_score >= 0.82:

        confidence = 0.92

    elif peak_score >= 0.72:

        confidence = 0.88

    elif peak_score >= 0.62:

        confidence = 0.78

    else:

        confidence = 0.65

    return {
        "available": True,

        "event": (
            "spouse_meeting"
        ),

        "forecast_available": (
            True
        ),

        "outlook": (
            primary.get(
                "strength"
            )
        ),

        "confidence": (
            confidence
        ),

        "summary": (
            "The strongest spouse-meeting opportunity "
            f"runs from {primary.get('start')} to "
            f"{primary.get('end')}, with peak activation "
            f"around {peak.get('date')}."
        ),

        "primary_window": (
            primary
        ),

        "secondary_windows": (
            windows[
                1:4
            ]
        ),

        "forecast_period": {
            "start": (
                start.isoformat()
            ),

            "end": (
                end.isoformat()
            ),

            "step_days": (
                step_days
            ),

            "snapshot_count": (
                len(
                    snapshots
                )
            ),
        },

        "snapshots": (
            snapshots
        ),
    }
