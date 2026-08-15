from datetime import datetime, timedelta
from typing import Any

from app.astrology.transits import (
    calculate_transits,
)
from app.astrology.features.transit_house_mapping import (
    map_transits_to_natal_houses,
)
from app.astrology.features.career_transits import (
    analyze_career_transits,
)
from app.astrology.features.dasha_career_reasoning import (
    analyze_current_dasha_for_career,
)
from app.astrology.features.career_event_timing import (
    analyze_career_event_timing,
)
from app.astrology.features.career_event_timing_synthesis import (
    synthesize_career_event_timing,
)
from app.astrology.features.career_dasha_transit_synthesis import (
    synthesize_career_dasha_transits,
)


EVENT_NAMES = (
    "job_change",
    "promotion_recognition",
    "income_gains",
    "foreign_international_opportunity",
    "career_pressure_challenge",
)


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _period_contains(
    start_raw: Any,
    end_raw: Any,
    moment: datetime,
) -> bool:
    if not isinstance(
        start_raw,
        str,
    ):
        return False

    if not isinstance(
        end_raw,
        str,
    ):
        return False

    start = datetime.fromisoformat(
        start_raw
    )

    end = datetime.fromisoformat(
        end_raw
    )

    return (
        start
        <= moment
        < end
    )


def _find_period_for_moment(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any] | None:
    """
    Find the Mahadasha / Antardasha active
    for one forecast date.
    """

    dashas = _safe_dict(
        chart.get(
            "dashas"
        )
    )

    mahadashas = dashas.get(
        "mahadashas",
        [],
    )

    if not isinstance(
        mahadashas,
        list,
    ):
        return None

    for md in mahadashas:

        if not isinstance(
            md,
            dict,
        ):
            continue

        if not _period_contains(
            md.get("start"),
            md.get("end"),
            moment,
        ):
            continue

        antardashas = md.get(
            "antardashas",
            [],
        )

        if not isinstance(
            antardashas,
            list,
        ):
            continue

        for ad in antardashas:

            if not isinstance(
                ad,
                dict,
            ):
                continue

            if _period_contains(
                ad.get("start"),
                ad.get("end"),
                moment,
            ):

                return {
                    "mahadasha": (
                        md.get(
                            "planet"
                        )
                    ),
                    "mahadasha_start": (
                        md.get(
                            "start"
                        )
                    ),
                    "mahadasha_end": (
                        md.get(
                            "end"
                        )
                    ),
                    "antardasha": (
                        ad.get(
                            "planet"
                        )
                    ),
                    "antardasha_start": (
                        ad.get(
                            "start"
                        )
                    ),
                    "antardasha_end": (
                        ad.get(
                            "end"
                        )
                    ),
                }

    return None


def _chart_with_period(
    chart: dict[str, Any],
    period: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a shallow chart copy with the requested
    Dasha period injected as current_period.
    """

    result = dict(
        chart
    )

    original_dashas = _safe_dict(
        chart.get(
            "dashas"
        )
    )

    dashas = dict(
        original_dashas
    )

    dashas[
        "current_period"
    ] = dict(
        period
    )

    result[
        "dashas"
    ] = dashas

    return result


def _scan_one_date(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:
    period = _find_period_for_moment(
        chart,
        moment,
    )

    if period is None:
        return {
            "available": False,
            "moment": moment.isoformat(),
            "reason": (
                "No Dasha period found for forecast date."
            ),
        }

    dated_chart = _chart_with_period(
        chart,
        period,
    )

    current_dasha = (
        analyze_current_dasha_for_career(
            dated_chart
        )
    )

    event_timing = (
        analyze_career_event_timing(
            dated_chart
        )
    )

    event_timing_synthesis = (
        synthesize_career_event_timing(
            event_timing,
            current_dasha,
        )
    )

    transits = calculate_transits(
        moment
    )

    mapped = (
        map_transits_to_natal_houses(
            chart,
            transits,
        )
    )

    career_transits = (
        analyze_career_transits(
            mapped
        )
    )

    confirmation = (
        synthesize_career_dasha_transits(
            event_timing_synthesis,
            career_transits,
        )
    )

    return {
        "available": True,
        "moment": moment.isoformat(),
        "current_dasha": {
            "mahadasha": (
                current_dasha.get(
                    "mahadasha"
                )
            ),
            "antardasha": (
                current_dasha.get(
                    "antardasha"
                )
            ),
        },
        "events": _safe_dict(
            confirmation.get(
                "events"
            )
        ),
    }


def _event_rank_value(
    event: dict[str, Any],
) -> float:
    """
    Rank by combined Dasha × Transit score.

    A small bonus is added for explicit
    event-specific transit confirmation.
    """

    score = _safe_float(
        event.get(
            "combined_score"
        )
    )

    if event.get(
        "specific_transit_confirmation"
    ) is True:
        score += 0.15

    confirmation = event.get(
        "confirmation"
    )

    if confirmation == (
        "strong_confirmation"
    ):
        score += 0.20

    elif confirmation == "confirmed":
        score += 0.10

    return round(
        score,
        3,
    )


def scan_career_forecast(
    chart: dict[str, Any],
    start: datetime,
    end: datetime,
    step_days: int = 7,
) -> dict[str, Any]:
    """
    Scan Dasha × transit career signals across
    an explicitly supplied date range.

    Default resolution:
        7 days

    This is intentionally coarse for the first version.
    Later layers can refine a strong weekly region into
    daily or sub-period windows.
    """

    if start.tzinfo is None:
        raise ValueError(
            "start must be timezone-aware."
        )

    if end.tzinfo is None:
        raise ValueError(
            "end must be timezone-aware."
        )

    if end <= start:
        raise ValueError(
            "end must be later than start."
        )

    if step_days < 1:
        raise ValueError(
            "step_days must be at least 1."
        )

    snapshots: list[
        dict[str, Any]
    ] = []

    cursor = start

    while cursor <= end:

        snapshot = _scan_one_date(
            chart,
            cursor,
        )

        if snapshot.get(
            "available"
        ):
            snapshots.append(
                snapshot
            )

        cursor = (
            cursor
            + timedelta(
                days=step_days
            )
        )

    rankings: dict[
        str,
        list[dict[str, Any]],
    ] = {
        event_name: []
        for event_name in EVENT_NAMES
    }

    for snapshot in snapshots:

        events = _safe_dict(
            snapshot.get(
                "events"
            )
        )

        for event_name in EVENT_NAMES:

            event = _safe_dict(
                events.get(
                    event_name
                )
            )

            if not event:
                continue

            rankings[
                event_name
            ].append(
                {
                    "moment": (
                        snapshot.get(
                            "moment"
                        )
                    ),
                    "period": (
                        event.get(
                            "period"
                        )
                    ),
                    "confirmation": (
                        event.get(
                            "confirmation"
                        )
                    ),
                    "dasha_score": (
                        event.get(
                            "dasha_score"
                        )
                    ),
                    "transit_score": (
                        event.get(
                            "transit_score"
                        )
                    ),
                    "combined_score": (
                        event.get(
                            "combined_score"
                        )
                    ),
                    "specific_transit_confirmation": (
                        event.get(
                            "specific_transit_confirmation"
                        )
                    ),
                    "rank_value": (
                        _event_rank_value(
                            event
                        )
                    ),
                    "summary": (
                        event.get(
                            "summary"
                        )
                    ),
                }
            )

    for event_name in EVENT_NAMES:

        rankings[
            event_name
        ].sort(
            key=lambda item: (
                -_safe_float(
                    item.get(
                        "rank_value"
                    )
                ),
                str(
                    item.get(
                        "moment",
                        "",
                    )
                ),
            )
        )

    top_dates = {
        event_name: values[:10]
        for event_name, values in rankings.items()
    }

    return {
        "available": True,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "step_days": step_days,
        "snapshot_count": len(
            snapshots
        ),
        "top_dates": top_dates,
    }