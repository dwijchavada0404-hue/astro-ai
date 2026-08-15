from typing import Any


EVENT_KEYS = (
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


def _current_event_result(
    event_timing_synthesis: dict[str, Any],
    event_name: str,
) -> dict[str, Any]:
    events = _safe_dict(
        event_timing_synthesis.get(
            "events"
        )
    )

    event = _safe_dict(
        events.get(
            event_name
        )
    )

    return _safe_dict(
        event.get(
            "current_period"
        )
    )


def _transit_scores(
    career_transits: dict[str, Any],
) -> dict[str, float]:
    scores = _safe_dict(
        career_transits.get(
            "scores"
        )
    )

    return {
        "career_activation": _safe_float(
            scores.get(
                "career_activation"
            )
        ),
        "growth": _safe_float(
            scores.get(
                "growth"
            )
        ),
        "transition": _safe_float(
            scores.get(
                "transition"
            )
        ),
        "recognition": _safe_float(
            scores.get(
                "recognition"
            )
        ),
        "pressure": _safe_float(
            scores.get(
                "pressure"
            )
        ),
        "foreign": _safe_float(
            scores.get(
                "foreign"
            )
        ),
    }


def _event_transit_score(
    event_name: str,
    transit_scores: dict[str, float],
) -> float:
    """
    Convert general career-transit signals into
    an event-specific transit score.

    General career activity receives less weight than
    an event-specific signal such as recognition,
    foreign activation or pressure.
    """

    career_activation = (
        transit_scores[
            "career_activation"
        ]
    )

    growth = (
        transit_scores[
            "growth"
        ]
    )

    transition = (
        transit_scores[
            "transition"
        ]
    )

    recognition = (
        transit_scores[
            "recognition"
        ]
    )

    pressure = (
        transit_scores[
            "pressure"
        ]
    )

    foreign = (
        transit_scores[
            "foreign"
        ]
    )

    if event_name == "job_change":

        score = (
            transition * 1.0
            + career_activation * 0.45
            + growth * 0.20
        )

    elif event_name == (
        "promotion_recognition"
    ):

        score = (
            recognition * 1.0
            + growth * 0.45
            + career_activation * 0.20
        )

    elif event_name == "income_gains":

        score = (
            growth * 0.80
            + recognition * 0.60
            + career_activation * 0.15
        )

    elif event_name == (
        "foreign_international_opportunity"
    ):

        score = (
            foreign * 1.0
            + transition * 0.25
            + career_activation * 0.10
        )

    elif event_name == (
        "career_pressure_challenge"
    ):

        score = (
            pressure * 1.0
            + transition * 0.35
        )

    else:
        score = 0.0

    return round(
        score,
        2,
    )


def _has_specific_transit_confirmation(
    event_name: str,
    transit_scores: dict[str, float],
) -> bool:
    """
    Require an event-specific transit anchor before
    describing transits as confirmation.

    This prevents generic career activity from being
    mislabelled as confirmation of promotion, foreign
    opportunity or another specific event.
    """

    if event_name == "job_change":

        return (
            transit_scores[
                "transition"
            ]
            >= 0.5
        )

    if event_name == (
        "promotion_recognition"
    ):

        return (
            transit_scores[
                "recognition"
            ]
            >= 0.3
        )

    if event_name == "income_gains":

        return (
            transit_scores[
                "growth"
            ]
            >= 0.75
            or transit_scores[
                "recognition"
            ]
            >= 0.4
        )

    if event_name == (
        "foreign_international_opportunity"
    ):

        return (
            transit_scores[
                "foreign"
            ]
            >= 0.5
        )

    if event_name == (
        "career_pressure_challenge"
    ):

        return (
            transit_scores[
                "pressure"
            ]
            >= 0.5
        )

    return False


def _combined_score(
    dasha_score: float,
    transit_score: float,
) -> float:
    """
    Dasha remains the primary timing layer.

    Transit works as a secondary confirmation layer.
    """

    combined = (
        dasha_score * 0.70
        + transit_score * 0.30
    )

    return round(
        combined,
        2,
    )


def _classify_confirmation(
    event_name: str,
    dasha_score: float,
    transit_score: float,
    combined_score: float,
    has_specific_anchor: bool,
) -> str:
    """
    Determine whether the current transit pattern genuinely
    confirms the same event indicated by the Dasha.
    """

    if event_name == (
        "career_pressure_challenge"
    ):

        if (
            dasha_score >= 1.5
            and has_specific_anchor
            and transit_score >= 0.5
        ):
            return (
                "strong_confirmation"
            )

        if (
            dasha_score >= 0.8
            and has_specific_anchor
        ):
            return "confirmed"

        if dasha_score > 0:
            return "dasha_only"

        if has_specific_anchor:
            return "transit_only"

        return "weak"

    if (
        dasha_score >= 1.3
        and has_specific_anchor
        and transit_score >= 1.0
    ):
        return "strong_confirmation"

    if (
        dasha_score >= 0.6
        and has_specific_anchor
        and transit_score >= 0.5
    ):
        return "confirmed"

    if dasha_score >= 0.6:
        return "dasha_only"

    if (
        has_specific_anchor
        and transit_score >= 0.8
    ):
        return "transit_only"

    if combined_score >= 0.8:
        return "general_activation"

    return "weak"


def _build_summary(
    event_name: str,
    confirmation: str,
    period: str | None,
) -> str:
    event_labels = {
        "job_change": (
            "job change or professional transition"
        ),
        "promotion_recognition": (
            "promotion or professional recognition"
        ),
        "income_gains": (
            "income or professional gains"
        ),
        "foreign_international_opportunity": (
            "foreign or international professional opportunity"
        ),
        "career_pressure_challenge": (
            "career pressure or demanding professional responsibilities"
        ),
    }

    label = event_labels.get(
        event_name,
        event_name,
    )

    period_name = (
        period
        if period
        else "current Dasha period"
    )

    if confirmation == (
        "strong_confirmation"
    ):

        return (
            f"The current {period_name} strongly activates "
            f"{label}, and the current transit pattern provides "
            "specific confirmation of the same theme."
        )

    if confirmation == "confirmed":

        return (
            f"The current {period_name} supports {label}, "
            "with an event-specific transit signal providing "
            "additional confirmation."
        )

    if confirmation == "dasha_only":

        return (
            f"The current {period_name} activates {label}, "
            "but the present transit pattern does not yet show "
            "a sufficiently strong event-specific confirmation."
        )

    if confirmation == "transit_only":

        return (
            f"Current transits specifically activate themes related "
            f"to {label}, but the present Dasha does not strongly "
            "support the same event."
        )

    if confirmation == (
        "general_activation"
    ):

        return (
            f"The broader career environment is active during "
            f"{period_name}, but the transit pattern does not "
            f"specifically confirm {label}."
        )

    return (
        f"The current Dasha and transit combination does not "
        f"show a strong joint signal for {label}."
    )


def synthesize_career_dasha_transits(
    career_event_timing_synthesis: dict[str, Any],
    career_transits: dict[str, Any],
) -> dict[str, Any]:
    """
    Combine current Dasha event activation with
    current career transit activation.

    Hierarchy:

        natal promise
            ->
        Dasha activation
            ->
        event-specific transit confirmation

    Transits do not create an event prediction by themselves.
    """

    if not career_event_timing_synthesis.get(
        "available"
    ):

        return {
            "available": False,
            "reason": (
                "Career event timing synthesis is unavailable."
            ),
        }

    if not career_transits.get(
        "available"
    ):

        return {
            "available": False,
            "reason": (
                "Career transit reasoning is unavailable."
            ),
        }

    transit_scores = (
        _transit_scores(
            career_transits
        )
    )

    results: dict[
        str,
        dict[str, Any],
    ] = {}

    for event_name in EVENT_KEYS:

        current_event = (
            _current_event_result(
                career_event_timing_synthesis,
                event_name,
            )
        )

        dasha_score = (
            _safe_float(
                current_event.get(
                    "score"
                )
            )
        )

        transit_score = (
            _event_transit_score(
                event_name,
                transit_scores,
            )
        )

        specific_anchor = (
            _has_specific_transit_confirmation(
                event_name,
                transit_scores,
            )
        )

        combined = (
            _combined_score(
                dasha_score,
                transit_score,
            )
        )

        confirmation = (
            _classify_confirmation(
                event_name,
                dasha_score,
                transit_score,
                combined,
                specific_anchor,
            )
        )

        period = current_event.get(
            "period"
        )

        results[event_name] = {
            "period": period,

            "dasha_outlook": (
                current_event.get(
                    "outlook"
                )
            ),

            "dasha_score": round(
                dasha_score,
                2,
            ),

            "transit_score": (
                transit_score
            ),

            "specific_transit_confirmation": (
                specific_anchor
            ),

            "combined_score": (
                combined
            ),

            "confirmation": (
                confirmation
            ),

            "summary": (
                _build_summary(
                    event_name,
                    confirmation,
                    period,
                )
            ),
        }

    return {
        "available": True,

        "transit_moment": (
            career_transits.get(
                "moment"
            )
        ),

        "transit_outlook": (
            career_transits.get(
                "outlook"
            )
        ),

        "transit_scores": (
            transit_scores
        ),

        "events": results,
    }