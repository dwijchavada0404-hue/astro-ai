from datetime import datetime, timedelta
from typing import Any


EVENT_NAMES = (
    "job_change",
    "promotion_recognition",
    "income_gains",
    "foreign_international_opportunity",
    "career_pressure_challenge",
)


EVENT_THRESHOLDS = {
    "job_change": 1.50,
    "promotion_recognition": 0.65,
    "income_gains": 0.50,
    "foreign_international_opportunity": 0.80,
    "career_pressure_challenge": 1.20,
}


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _safe_list(
    value: Any,
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _parse_datetime(
    value: Any,
) -> datetime | None:
    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(
            value
        )

    except ValueError:
        return None


def _format_date(
    value: datetime | None,
) -> str | None:
    if value is None:
        return None

    return value.date().isoformat()


def _format_month(
    value: datetime | None,
) -> str | None:
    if value is None:
        return None

    return value.strftime(
        "%B %Y"
    )


def _confirmation_strength(
    value: Any,
) -> int:
    mapping = {
        "strong_confirmation": 4,
        "confirmed": 3,
        "dasha_only": 2,
        "transit_only": 2,
        "general_activation": 1,
        "weak": 0,
    }

    return mapping.get(
        str(value),
        0,
    )


def _qualifies(
    event_name: str,
    item: dict[str, Any],
) -> bool:
    threshold = EVENT_THRESHOLDS.get(
        event_name,
        0.0,
    )

    rank_value = _safe_float(
        item.get(
            "rank_value"
        )
    )

    confirmation = item.get(
        "confirmation"
    )

    confirmation_strength = (
        _confirmation_strength(
            confirmation
        )
    )

    if event_name == "job_change":
        return (
            rank_value >= threshold
            and confirmation_strength >= 3
        )

    if event_name == (
        "promotion_recognition"
    ):
        return (
            rank_value >= threshold
            and confirmation_strength >= 3
            and item.get(
                "specific_transit_confirmation"
            )
            is True
        )

    if event_name == "income_gains":
        return (
            rank_value >= threshold
            and confirmation_strength >= 2
        )

    if event_name == (
        "foreign_international_opportunity"
    ):
        return (
            rank_value >= threshold
            and confirmation_strength >= 2
        )

    if event_name == (
        "career_pressure_challenge"
    ):
        return (
            rank_value >= threshold
            and confirmation_strength >= 3
        )

    return False


def _chronological_candidates(
    event_name: str,
    values: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = [
        item
        for item in values
        if _qualifies(
            event_name,
            item,
        )
    ]

    candidates.sort(
        key=lambda item: (
            str(
                item.get(
                    "moment",
                    "",
                )
            )
        )
    )

    return candidates


def _cluster_candidates(
    candidates: list[dict[str, Any]],
    step_days: int,
    gap_multiplier: int = 3,
) -> list[list[dict[str, Any]]]:
    """
    Merge nearby strong snapshots.

    With weekly scanning and the default multiplier
    of 3, strong dates separated by up to 21 days
    are treated as part of the same practical window.
    """

    if not candidates:
        return []

    maximum_gap = timedelta(
        days=(
            step_days
            * gap_multiplier
        )
    )

    clusters: list[
        list[dict[str, Any]]
    ] = []

    current_cluster = [
        candidates[0]
    ]

    previous_date = _parse_datetime(
        candidates[0].get(
            "moment"
        )
    )

    for item in candidates[1:]:

        current_date = _parse_datetime(
            item.get(
                "moment"
            )
        )

        if (
            previous_date is None
            or current_date is None
        ):
            clusters.append(
                current_cluster
            )

            current_cluster = [
                item
            ]

            previous_date = (
                current_date
            )

            continue

        gap = (
            current_date
            - previous_date
        )

        if gap <= maximum_gap:
            current_cluster.append(
                item
            )

        else:
            clusters.append(
                current_cluster
            )

            current_cluster = [
                item
            ]

        previous_date = (
            current_date
        )

    clusters.append(
        current_cluster
    )

    return clusters


def _peak_item(
    cluster: list[dict[str, Any]],
) -> dict[str, Any]:
    if not cluster:
        return {}

    return max(
        cluster,
        key=lambda item: (
            _safe_float(
                item.get(
                    "rank_value"
                )
            ),
            _safe_float(
                item.get(
                    "combined_score"
                )
            ),
        ),
    )


def _average_score(
    cluster: list[dict[str, Any]],
    field: str,
) -> float:
    if not cluster:
        return 0.0

    values = [
        _safe_float(
            item.get(
                field
            )
        )
        for item in cluster
    ]

    return round(
        sum(values)
        / len(values),
        2,
    )


def _window_strength(
    event_name: str,
    cluster: list[dict[str, Any]],
) -> str:
    if not cluster:
        return "weak"

    peak = _peak_item(
        cluster
    )

    peak_rank = _safe_float(
        peak.get(
            "rank_value"
        )
    )

    confirmations = [
        _confirmation_strength(
            item.get(
                "confirmation"
            )
        )
        for item in cluster
    ]

    strong_count = sum(
        1
        for value in confirmations
        if value >= 4
    )

    if event_name == "job_change":

        if (
            peak_rank >= 2.0
            and strong_count >= 2
        ):
            return "very_strong"

        if peak_rank >= 1.6:
            return "strong"

        return "moderate"

    if event_name == (
        "career_pressure_challenge"
    ):

        if strong_count >= 3:
            return "very_strong"

        if peak_rank >= 1.3:
            return "strong"

        return "moderate"

    if event_name == (
        "promotion_recognition"
    ):

        if peak_rank >= 1.2:
            return "very_strong"

        if peak_rank >= 0.8:
            return "strong"

        return "moderate"

    if event_name == "income_gains":

        if peak_rank >= 1.0:
            return "strong"

        if peak_rank >= 0.6:
            return "moderate"

        return "weak"

    if event_name == (
        "foreign_international_opportunity"
    ):

        if peak_rank >= 1.3:
            return "strong"

        if peak_rank >= 0.8:
            return "moderate"

        return "weak"

    return "moderate"


def _build_window(
    event_name: str,
    cluster: list[dict[str, Any]],
    step_days: int,
) -> dict[str, Any]:
    first = cluster[0]
    last = cluster[-1]

    first_date = _parse_datetime(
        first.get(
            "moment"
        )
    )

    last_date = _parse_datetime(
        last.get(
            "moment"
        )
    )

    peak = _peak_item(
        cluster
    )

    peak_date = _parse_datetime(
        peak.get(
            "moment"
        )
    )

    window_end = (
        last_date
        + timedelta(
            days=step_days,
        )
        if last_date
        else None
    )

    confirmations = sorted(
        {
            str(
                item.get(
                    "confirmation"
                )
            )
            for item in cluster
        }
    )

    return {
        "event": event_name,

        "start": _format_date(
            first_date
        ),

        "end": _format_date(
            window_end
        ),

        "start_month": (
            _format_month(
                first_date
            )
        ),

        "end_month": (
            _format_month(
                window_end
            )
        ),

        "snapshot_count": len(
            cluster
        ),

        "strength": (
            _window_strength(
                event_name,
                cluster,
            )
        ),

        "average_rank_value": (
            _average_score(
                cluster,
                "rank_value",
            )
        ),

        "average_combined_score": (
            _average_score(
                cluster,
                "combined_score",
            )
        ),

        "peak": {
            "date": _format_date(
                peak_date
            ),

            "period": (
                peak.get(
                    "period"
                )
            ),

            "confirmation": (
                peak.get(
                    "confirmation"
                )
            ),

            "rank_value": (
                peak.get(
                    "rank_value"
                )
            ),

            "combined_score": (
                peak.get(
                    "combined_score"
                )
            ),

            "transit_score": (
                peak.get(
                    "transit_score"
                )
            ),
        },

        "confirmations": (
            confirmations
        ),

        "sample_dates": [
            (
                item.get(
                    "moment"
                )[:10]
                if isinstance(
                    item.get(
                        "moment"
                    ),
                    str,
                )
                else None
            )
            for item in cluster
        ],
    }


def _window_rank(
    window: dict[str, Any],
) -> float:
    strength_bonus = {
        "very_strong": 0.40,
        "strong": 0.25,
        "moderate": 0.10,
        "weak": 0.0,
    }

    strength = str(
        window.get(
            "strength",
            "weak",
        )
    )

    average = _safe_float(
        window.get(
            "average_rank_value"
        )
    )

    snapshots = int(
        window.get(
            "snapshot_count",
            0,
        )
    )

    persistence_bonus = min(
        snapshots * 0.03,
        0.24,
    )

    return round(
        average
        + strength_bonus.get(
            strength,
            0.0,
        )
        + persistence_bonus,
        3,
    )


def _build_event_summary(
    event_name: str,
    windows: list[dict[str, Any]],
) -> str:
    if not windows:

        labels = {
            "job_change": (
                "job-change or professional-transition"
            ),
            "promotion_recognition": (
                "promotion or recognition"
            ),
            "income_gains": (
                "income or professional-gains"
            ),
            "foreign_international_opportunity": (
                "foreign or international-opportunity"
            ),
            "career_pressure_challenge": (
                "career-pressure"
            ),
        }

        label = labels.get(
            event_name,
            event_name,
        )

        return (
            f"No sufficiently strong {label} "
            "window was identified in the scanned period."
        )

    primary = windows[0]

    start = primary.get(
        "start"
    )

    end = primary.get(
        "end"
    )

    peak = _safe_dict(
        primary.get(
            "peak"
        )
    )

    peak_date = peak.get(
        "date"
    )

    strength = primary.get(
        "strength"
    )

    labels = {
        "job_change": (
            "job-change or professional-transition"
        ),
        "promotion_recognition": (
            "promotion or recognition"
        ),
        "income_gains": (
            "income or professional-gains"
        ),
        "foreign_international_opportunity": (
            "foreign or international-opportunity"
        ),
        "career_pressure_challenge": (
            "career-pressure"
        ),
    }

    label = labels.get(
        event_name,
        event_name,
    )

    return (
        f"The strongest {label} window identified "
        f"in the scanned period runs from {start} "
        f"to {end}. The window is classified as "
        f"{strength}, with peak activation around "
        f"{peak_date}."
    )


def build_career_forecast_windows(
    scan_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert individual forecast snapshots into
    broader practical event windows.
    """

    if not scan_result.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career forecast scan is unavailable."
            ),
        }

    step_days = int(
        scan_result.get(
            "step_days",
            7,
        )
    )

    top_dates = _safe_dict(
        scan_result.get(
            "top_dates"
        )
    )

    event_results: dict[
        str,
        dict[str, Any],
    ] = {}

    for event_name in EVENT_NAMES:

        values = _safe_list(
            top_dates.get(
                event_name
            )
        )

        candidates = (
            _chronological_candidates(
                event_name,
                values,
            )
        )

        clusters = (
            _cluster_candidates(
                candidates,
                step_days,
            )
        )

        windows = [
            _build_window(
                event_name,
                cluster,
                step_days,
            )
            for cluster in clusters
            if cluster
        ]

        for window in windows:

            window[
                "window_rank"
            ] = _window_rank(
                window
            )

        windows.sort(
            key=lambda item: (
                -_safe_float(
                    item.get(
                        "window_rank"
                    )
                ),
                str(
                    item.get(
                        "start",
                        "",
                    )
                ),
            )
        )

        event_results[
            event_name
        ] = {
            "available": bool(
                windows
            ),

            "summary": (
                _build_event_summary(
                    event_name,
                    windows,
                )
            ),

            "primary_window": (
                windows[0]
                if windows
                else {}
            ),

            "secondary_windows": (
                windows[1:4]
                if len(windows) > 1
                else []
            ),

            "window_count": len(
                windows
            ),
        }

    return {
        "available": True,

        "scan_start": (
            scan_result.get(
                "start"
            )
        ),

        "scan_end": (
            scan_result.get(
                "end"
            )
        ),

        "step_days": (
            step_days
        ),

        "events": (
            event_results
        ),
    }