from datetime import datetime
from typing import Any


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> list[dict[str, Any]]:
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


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _contains_factor(
    indicators: Any,
    factor_fragment: str,
) -> bool:
    for indicator in _safe_list(indicators):

        factor = indicator.get("factor")

        if (
            isinstance(factor, str)
            and factor_fragment in factor
        ):
            return True

    return False


def _career_specific_bonus(
    period: dict[str, Any],
) -> float:
    """
    Add extra weight for direct career activation.

    Highest priority:
    - 10th lord activation
    - planet placed in the 10th house
    """

    indicators = period.get(
        "indicators"
    )

    bonus = 0.0

    if _contains_factor(
        indicators,
        "tenth_lord",
    ):
        bonus += 0.8

    if _contains_factor(
        indicators,
        "tenth_house",
    ):
        bonus += 0.7

    return bonus


def _adjusted_period_score(
    period: dict[str, Any],
) -> float:
    base_score = _safe_float(
        period.get("score")
    )

    bonus = _career_specific_bonus(
        period
    )

    return round(
        base_score + bonus,
        2,
    )


def _current_reference_date(
    current_dasha: dict[str, Any],
) -> datetime | None:
    """
    Use the start of the current Antardasha as the reference
    point for filtering past periods.

    We deliberately use the Dasha engine's own dates instead
    of independently calculating current planetary time.
    """

    return _parse_datetime(
        current_dasha.get(
            "antardasha_start"
        )
    )


def _is_future_or_current(
    period: dict[str, Any],
    current_dasha: dict[str, Any],
) -> bool:
    period_end = _parse_datetime(
        period.get("end")
    )

    reference = _current_reference_date(
        current_dasha
    )

    if (
        period_end is None
        or reference is None
    ):
        return True

    return period_end >= reference


def _period_start_datetime(
    period: dict[str, Any],
) -> datetime | None:
    return _parse_datetime(
        period.get("start")
    )


def _extract_reasons(
    period: dict[str, Any],
    limit: int = 5,
) -> list[str]:
    reasons: list[str] = []

    for indicator in _safe_list(
        period.get("indicators")
    ):

        interpretation = indicator.get(
            "interpretation"
        )

        if not isinstance(
            interpretation,
            str,
        ):
            continue

        interpretation = interpretation.strip()

        if (
            interpretation
            and interpretation not in reasons
        ):
            reasons.append(
                interpretation
            )

        if len(reasons) >= limit:
            break

    return reasons


def _classify_window(
    period: dict[str, Any],
) -> str:
    adjusted = _adjusted_period_score(
        period
    )

    direct_lord = _contains_factor(
        period.get("indicators"),
        "tenth_lord",
    )

    direct_house = _contains_factor(
        period.get("indicators"),
        "tenth_house",
    )

    if (
        adjusted >= 3.0
        and (
            direct_lord
            or direct_house
        )
    ):
        return "high_priority"

    if adjusted >= 2.2:
        return "strong"

    if adjusted >= 1.4:
        return "supportive"

    if adjusted >= 0.7:
        return "mixed"

    return "secondary"


def _build_period_summary(
    period: dict[str, Any],
) -> dict[str, Any]:
    mahadasha = period.get(
        "mahadasha"
    )

    antardasha = period.get(
        "antardasha"
    )

    period_name = (
        f"{mahadasha}/{antardasha}"
        if mahadasha and antardasha
        else None
    )

    indicators = _safe_list(
        period.get("indicators")
    )

    return {
        "period": period_name,
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "start": period.get(
            "start"
        ),
        "end": period.get(
            "end"
        ),
        "base_score": _safe_float(
            period.get("score")
        ),
        "career_adjusted_score": (
            _adjusted_period_score(
                period
            )
        ),
        "outlook": period.get(
            "outlook"
        ),
        "priority": _classify_window(
            period
        ),
        "direct_tenth_lord_activation": (
            _contains_factor(
                indicators,
                "tenth_lord",
            )
        ),
        "direct_tenth_house_activation": (
            _contains_factor(
                indicators,
                "tenth_house",
            )
        ),
        "scores": _safe_dict(
            period.get("scores")
        ),
        "reasons": _extract_reasons(
            period
        ),
    }


def _build_current_period(
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    if not current_dasha.get(
        "available"
    ):
        return {
            "available": False,
        }

    mahadasha = current_dasha.get(
        "mahadasha"
    )

    antardasha = current_dasha.get(
        "antardasha"
    )

    return {
        "available": True,
        "period": (
            f"{mahadasha}/{antardasha}"
            if mahadasha and antardasha
            else None
        ),
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "start": current_dasha.get(
            "antardasha_start"
        ),
        "end": current_dasha.get(
            "antardasha_end"
        ),
        "outlook": current_dasha.get(
            "outlook"
        ),
        "confidence": _safe_float(
            current_dasha.get(
                "confidence"
            )
        ),
        "scores": _safe_dict(
            current_dasha.get(
                "scores"
            )
        ),
    }


def _select_nearest_strong_window(
    periods: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Select the nearest chronologically useful strong window.

    This prioritises practical proximity over absolute maximum score.
    """

    eligible = [
        period
        for period in periods
        if _classify_window(period)
        in {
            "high_priority",
            "strong",
        }
    ]

    if not eligible:
        eligible = [
            period
            for period in periods
            if _classify_window(period)
            == "supportive"
        ]

    if not eligible:
        return {}

    eligible.sort(
        key=lambda item: (
            _period_start_datetime(item)
            or datetime.max.replace(
                tzinfo=_current_reference_tz(
                    periods
                )
            ),
            -_adjusted_period_score(
                item
            ),
        )
    )

    return eligible[0]


def _current_reference_tz(
    periods: list[dict[str, Any]],
):
    """
    Return any available timezone from the timing periods.

    Used only to keep datetime comparisons timezone-compatible.
    """

    for period in periods:
        start = _period_start_datetime(
            period
        )

        if start is not None:
            return start.tzinfo

    return None


def _select_strongest_long_term_window(
    periods: list[dict[str, Any]],
) -> dict[str, Any]:
    if not periods:
        return {}

    ranked = sorted(
        periods,
        key=lambda item: (
            -_adjusted_period_score(
                item
            ),
            str(
                item.get(
                    "start",
                    "",
                )
            ),
        ),
    )

    return ranked[0]


def _select_direct_activation_windows(
    periods: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    direct = [
        period
        for period in periods
        if (
            _contains_factor(
                period.get("indicators"),
                "tenth_lord",
            )
            or _contains_factor(
                period.get("indicators"),
                "tenth_house",
            )
        )
    ]

    direct.sort(
        key=lambda item: (
            _period_start_datetime(item)
            or datetime.max.replace(
                tzinfo=_current_reference_tz(
                    periods
                )
            ),
            -_adjusted_period_score(
                item
            ),
        )
    )

    return direct[:limit]


def _select_upcoming_windows(
    periods: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Return a chronological set of useful upcoming windows.

    This is intentionally not sorted by score alone.
    """

    useful = [
        period
        for period in periods
        if _classify_window(period)
        in {
            "high_priority",
            "strong",
            "supportive",
        }
    ]

    useful.sort(
        key=lambda item: (
            _period_start_datetime(item)
            or datetime.max.replace(
                tzinfo=_current_reference_tz(
                    periods
                )
            ),
            -_adjusted_period_score(
                item
            ),
        )
    )

    return useful[:limit]


def synthesize_career_timing(
    career_timing: dict[str, Any],
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert raw career timing into practical user-facing windows.

    The synthesis separates:

    1. nearest strong window
       - useful for near-term planning

    2. strongest long-term window
       - highest astrological career score

    3. direct career activation windows
       - periods involving the 10th lord or 10th-house planets

    4. chronological upcoming windows
       - prevents far-future periods from crowding out
         nearer useful periods
    """

    if not career_timing.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career timing analysis is unavailable."
            ),
        }

    periods = _safe_list(
        career_timing.get(
            "periods"
        )
    )

    future_periods = [
        period
        for period in periods
        if _is_future_or_current(
            period,
            current_dasha,
        )
    ]

    nearest_raw = (
        _select_nearest_strong_window(
            future_periods
        )
    )

    strongest_raw = (
        _select_strongest_long_term_window(
            future_periods
        )
    )

    upcoming_raw = (
        _select_upcoming_windows(
            future_periods,
            limit=5,
        )
    )

    direct_raw = (
        _select_direct_activation_windows(
            future_periods,
            limit=5,
        )
    )

    nearest_window = (
        _build_period_summary(
            nearest_raw
        )
        if nearest_raw
        else {}
    )

    strongest_long_term_window = (
        _build_period_summary(
            strongest_raw
        )
        if strongest_raw
        else {}
    )

    upcoming_windows = [
        _build_period_summary(
            period
        )
        for period in upcoming_raw
    ]

    direct_activation_windows = [
        _build_period_summary(
            period
        )
        for period in direct_raw
    ]

    if nearest_window:

        summary = (
            "The nearest strong career-supportive period "
            f"identified is {nearest_window.get('period')}, "
            f"from {nearest_window.get('start')} "
            f"to {nearest_window.get('end')}. "
            "A separate long-term ranking is retained so that "
            "a much later high-scoring period does not replace "
            "a nearer practical career window."
        )

    else:

        summary = (
            "No sufficiently strong near-term career window "
            "was identified from the available Dasha periods."
        )

    return {
        "available": True,
        "tenth_lord": career_timing.get(
            "tenth_lord"
        ),
        "current_period": (
            _build_current_period(
                current_dasha
            )
        ),
        "summary": summary,
        "nearest_strong_window": (
            nearest_window
        ),
        "strongest_long_term_window": (
            strongest_long_term_window
        ),
        "upcoming_windows": (
            upcoming_windows
        ),
        "direct_career_activation_windows": (
            direct_activation_windows
        ),
        "future_period_count": len(
            future_periods
        ),
    }