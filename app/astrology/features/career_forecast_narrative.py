from typing import Any


EVENT_LABELS = {
    "job_change": "Job Change / Professional Transition",
    "promotion_recognition": "Promotion / Recognition",
    "income_gains": "Income / Professional Gains",
    "foreign_international_opportunity": (
        "Foreign / International Opportunity"
    ),
    "career_pressure_challenge": (
        "Career Pressure / Challenge"
    ),
}


STRENGTH_CONFIDENCE = {
    "very_strong": 0.90,
    "strong": 0.80,
    "moderate": 0.65,
    "weak": 0.45,
}


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


def _strength_confidence(
    strength: str,
    snapshot_count: int,
) -> float:
    """
    Convert window strength and persistence into
    a conservative forecast confidence score.

    Confidence represents confidence in the
    identified symbolic window, not certainty
    that the event itself will occur.
    """

    base = STRENGTH_CONFIDENCE.get(
        strength,
        0.50,
    )

    persistence_bonus = min(
        max(
            snapshot_count - 1,
            0,
        )
        * 0.01,
        0.05,
    )

    return round(
        min(
            base
            + persistence_bonus,
            0.95,
        ),
        2,
    )


def _readable_strength(
    strength: str,
) -> str:
    mapping = {
        "very_strong": "very strong",
        "strong": "strong",
        "moderate": "moderate",
        "weak": "weak",
    }

    return mapping.get(
        strength,
        strength.replace(
            "_",
            " ",
        ),
    )


def _format_window_summary(
    event_name: str,
    event_data: dict[str, Any],
) -> dict[str, Any]:

    label = EVENT_LABELS.get(
        event_name,
        event_name,
    )

    available = bool(
        event_data.get(
            "available"
        )
    )

    if not available:
        return {
            "available": False,
            "label": label,
            "outlook": "no_strong_window",
            "confidence": 0.40,
            "summary": (
                f"No sufficiently strong {label.lower()} "
                "window was identified in the scanned period."
            ),
            "window": {},
        }

    window = _safe_dict(
        event_data.get(
            "primary_window"
        )
    )

    strength = str(
        window.get(
            "strength",
            "moderate",
        )
    )

    snapshot_count = int(
        window.get(
            "snapshot_count",
            0,
        )
    )

    confidence = (
        _strength_confidence(
            strength,
            snapshot_count,
        )
    )

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak = _safe_dict(
        window.get(
            "peak"
        )
    )

    peak_date = peak.get(
        "date"
    )

    period = peak.get(
        "period"
    )

    confirmation = peak.get(
        "confirmation"
    )

    readable_strength = (
        _readable_strength(
            strength
        )
    )

    # -----------------------------------------------------
    # JOB CHANGE
    # -----------------------------------------------------

    if event_name == "job_change":

        summary = (
            f"A {readable_strength} professional-transition "
            f"window is identified from {start} to {end}, "
            f"with the strongest activation around {peak_date}. "
        )

        if confirmation == (
            "strong_confirmation"
        ):
            summary += (
                f"The {period} Dasha and transit pattern "
                "are both reinforcing the job-change theme."
            )

        elif confirmation == "confirmed":
            summary += (
                f"The {period} Dasha is supported by "
                "event-specific transit activation."
            )

        else:
            summary += (
                f"The broader {period} period remains "
                "professionally active."
            )

    # -----------------------------------------------------
    # PROMOTION
    # -----------------------------------------------------

    elif event_name == (
        "promotion_recognition"
    ):

        summary = (
            f"A {readable_strength} promotion or recognition "
            f"window is identified from {start} to {end}, "
            f"with peak activation around {peak_date}. "
        )

        if confirmation in {
            "strong_confirmation",
            "confirmed",
        }:
            summary += (
                "This period has both Dasha support and "
                "specific transit reinforcement for professional "
                "visibility or recognition."
            )

        else:
            summary += (
                "The period shows professional activation, "
                "although recognition-specific confirmation "
                "is more limited."
            )

    # -----------------------------------------------------
    # INCOME
    # -----------------------------------------------------

    elif event_name == "income_gains":

        summary = (
            f"A {readable_strength} income or professional-gains "
            f"window is identified from {start} to {end}, "
            f"with the strongest signal around {peak_date}."
        )

    # -----------------------------------------------------
    # FOREIGN
    # -----------------------------------------------------

    elif event_name == (
        "foreign_international_opportunity"
    ):

        summary = (
            f"A {readable_strength} foreign or international "
            f"career theme is active from {start} to {end}, "
            f"with peak activation around {peak_date}. "
        )

        if confirmation in {
            "strong_confirmation",
            "confirmed",
        }:
            summary += (
                "The transit pattern specifically reinforces "
                "international, relocation or foreign-environment themes."
            )

        elif confirmation == "dasha_only":
            summary += (
                "The Dasha supports the theme, but the current "
                "transits do not yet provide strong foreign-specific "
                "confirmation."
            )

        else:
            summary += (
                "The signal should be treated as contextual rather "
                "than as a definite indication of relocation or "
                "foreign employment."
            )

    # -----------------------------------------------------
    # PRESSURE
    # -----------------------------------------------------

    elif event_name == (
        "career_pressure_challenge"
    ):

        summary = (
            f"A {readable_strength} career-pressure phase is "
            f"identified from {start} to {end}. "
            f"The pressure signal is strongest around {peak_date}. "
        )

        if confirmation == (
            "strong_confirmation"
        ):
            summary += (
                "Both Dasha and transit factors indicate increased "
                "responsibility, workload, restructuring or the need "
                "for sustained professional effort."
            )

        else:
            summary += (
                "This represents an elevated workload or responsibility "
                "signal rather than necessarily a negative career outcome."
            )

    else:
        summary = (
            f"A {readable_strength} window is identified "
            f"from {start} to {end}, with peak activation "
            f"around {peak_date}."
        )

    return {
        "available": True,
        "label": label,
        "outlook": strength,
        "confidence": confidence,
        "summary": summary,
        "window": {
            "start": start,
            "end": end,
            "start_month": (
                window.get(
                    "start_month"
                )
            ),
            "end_month": (
                window.get(
                    "end_month"
                )
            ),
            "strength": strength,
            "peak_date": peak_date,
            "period": period,
            "confirmation": confirmation,
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
            "snapshot_count": (
                snapshot_count
            ),
        },
    }


def _build_overall_summary(
    forecasts: dict[str, Any],
) -> dict[str, Any]:

    job = _safe_dict(
        forecasts.get(
            "job_change"
        )
    )

    promotion = _safe_dict(
        forecasts.get(
            "promotion_recognition"
        )
    )

    income = _safe_dict(
        forecasts.get(
            "income_gains"
        )
    )

    foreign = _safe_dict(
        forecasts.get(
            "foreign_international_opportunity"
        )
    )

    pressure = _safe_dict(
        forecasts.get(
            "career_pressure_challenge"
        )
    )

    strongest_event = None
    strongest_score = -1.0

    for event_name, data in (
        forecasts.items()
    ):

        if not isinstance(
            data,
            dict,
        ):
            continue

        if not data.get(
            "available"
        ):
            continue

        confidence = _safe_float(
            data.get(
                "confidence"
            )
        )

        strength_bonus = {
            "very_strong": 0.20,
            "strong": 0.10,
            "moderate": 0.05,
            "weak": 0.0,
        }.get(
            data.get(
                "outlook"
            ),
            0.0,
        )

        score = (
            confidence
            + strength_bonus
        )

        if score > strongest_score:
            strongest_score = score
            strongest_event = event_name

    parts: list[str] = []

    if job.get(
        "available"
    ):
        window = _safe_dict(
            job.get(
                "window"
            )
        )

        parts.append(
            "The strongest near-term career signal is "
            "professional transition or job change, with "
            f"the main window running from {window.get('start')} "
            f"to {window.get('end')} and peak activation "
            f"around {window.get('peak_date')}."
        )

    if pressure.get(
        "available"
    ):
        window = _safe_dict(
            pressure.get(
                "window"
            )
        )

        parts.append(
            "The same broader period also carries elevated "
            "career-pressure and responsibility themes, especially "
            f"between {window.get('start')} and {window.get('end')}."
        )

    if promotion.get(
        "available"
    ):
        window = _safe_dict(
            promotion.get(
                "window"
            )
        )

        parts.append(
            "A separate recognition or promotion signal appears "
            f"around {window.get('peak_date')}."
        )

    if foreign.get(
        "available"
    ):
        window = _safe_dict(
            foreign.get(
                "window"
            )
        )

        if window.get(
            "confirmation"
        ) == "dasha_only":
            parts.append(
                "Foreign or international career themes are present "
                "in the background, but they are not yet strongly "
                "confirmed by event-specific transits."
            )

    if not income.get(
        "available"
    ):
        parts.append(
            "No separate strong income-gains window was identified "
            "within the scanned period."
        )

    if not parts:
        summary = (
            "No major career event window was identified "
            "within the scanned period."
        )

        outlook = "quiet"

        confidence = 0.45

    else:
        summary = " ".join(
            parts
        )

        if strongest_event == "job_change":
            outlook = (
                "professional_transition_emphasised"
            )

        elif strongest_event == (
            "promotion_recognition"
        ):
            outlook = (
                "recognition_emphasised"
            )

        elif strongest_event == (
            "career_pressure_challenge"
        ):
            outlook = (
                "pressure_emphasised"
            )

        else:
            outlook = (
                "career_activity_emphasised"
            )

        confidence = round(
            min(
                strongest_score,
                0.95,
            ),
            2,
        )

    return {
        "outlook": outlook,
        "confidence": confidence,
        "strongest_event": strongest_event,
        "summary": summary,
    }


def generate_career_forecast_narrative(
    forecast_windows: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert technical career forecast windows into
    a user-facing forecast.

    This layer does not perform new astrological
    calculations. It only synthesises the outputs of
    the forecast scanner and window-merging engine.
    """

    if not forecast_windows.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career forecast windows are unavailable."
            ),
        }

    raw_events = _safe_dict(
        forecast_windows.get(
            "events"
        )
    )

    forecasts: dict[
        str,
        dict[str, Any],
    ] = {}

    for event_name in EVENT_LABELS:

        event_data = _safe_dict(
            raw_events.get(
                event_name
            )
        )

        forecasts[
            event_name
        ] = (
            _format_window_summary(
                event_name,
                event_data,
            )
        )

    overall = (
        _build_overall_summary(
            forecasts
        )
    )

    return {
        "available": True,

        "forecast_period": {
            "start": (
                forecast_windows.get(
                    "scan_start"
                )
            ),
            "end": (
                forecast_windows.get(
                    "scan_end"
                )
            ),
            "resolution_days": (
                forecast_windows.get(
                    "step_days"
                )
            ),
        },

        "overall": overall,

        "events": forecasts,

        "disclaimer": (
            "Astrological forecasts describe symbolic periods of "
            "stronger or weaker support. The identified windows should "
            "not be treated as guaranteed dates for employment, "
            "promotion, relocation, income or other professional events."
        ),
    }