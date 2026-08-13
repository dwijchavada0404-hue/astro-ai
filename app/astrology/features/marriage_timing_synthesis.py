from typing import Any


def _safe_list(value: Any) -> list[dict[str, Any]]:
    """Return a list containing only dictionary items."""
    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_timing_result(
    marriage_timing: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract the timing result from the existing marriage timing engine.

    This intentionally supports a few possible output structures so
    the synthesis layer does not tightly couple itself to one format.
    """

    if not isinstance(marriage_timing, dict):
        return {}

    result = marriage_timing.get("result")

    if isinstance(result, dict):
        return result

    return marriage_timing


def _get_dasha_result(
    dasha_result: dict[str, Any],
) -> dict[str, Any]:
    """Safely return the current Dasha marriage reasoning."""
    if not isinstance(dasha_result, dict):
        return {}

    return dasha_result


def _classify_timing(
    positive_score: float,
    challenge_score: float,
    theme_score: float,
) -> str:
    """
    Convert evidence scores into a high-level timing outlook.
    """

    net_score = (
        positive_score
        - challenge_score
    )

    if (
        positive_score >= 1.5
        and net_score >= 1.0
    ):
        return "strongly_supportive"

    if (
        positive_score >= 0.8
        and net_score >= 0.4
    ):
        return "supportive"

    if challenge_score >= 1.5:
        return "challenging"

    if (
        challenge_score > positive_score
        and challenge_score >= 0.8
    ):
        return "less_supportive"

    if theme_score > 0:
        return "mixed"

    return "neutral"


def _build_summary(
    outlook: str,
    dasha_result: dict[str, Any],
) -> str:
    """
    Create a concise human-readable synthesis.

    This is intentionally conservative: it describes the strength
    of the period rather than claiming a guaranteed marriage event.
    """

    mahadasha = dasha_result.get(
        "mahadasha"
    )

    antardasha = dasha_result.get(
        "antardasha"
    )

    if mahadasha and antardasha:

        period = (
            f"{mahadasha}/{antardasha}"
        )

    else:
        period = "current Dasha period"

    summaries = {
        "strongly_supportive": (
            f"The current {period} period shows "
            "strong marriage-supportive indications."
        ),
        "supportive": (
            f"The current {period} period shows "
            "supportive indications for marriage-related "
            "developments."
        ),
        "mixed": (
            f"The current {period} period shows mixed "
            "marriage indications, with supportive factors "
            "combined with themes that may introduce delay, "
            "distance or uncertainty."
        ),
        "less_supportive": (
            f"The current {period} period appears less "
            "supportive for immediate marriage-related "
            "developments."
        ),
        "challenging": (
            f"The current {period} period contains stronger "
            "challenging indications for marriage timing."
        ),
        "neutral": (
            f"The current {period} period does not show "
            "a strong timing signal by itself."
        ),
    }

    return summaries.get(
        outlook,
        summaries["neutral"],
    )


def synthesize_marriage_timing(
    marriage_timing: dict[str, Any],
    dasha_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Combine marriage timing evidence with current Dasha reasoning.

    This is a synthesis layer only.

    Existing feature engines remain responsible for:
        - generating individual indicators
        - calculating Dasha periods
        - identifying marriage-related placements
        - identifying timing windows

    This function combines those outputs into one structured result.
    """

    marriage_timing = (
        _get_timing_result(marriage_timing)
    )

    dasha_result = _get_dasha_result(
        dasha_result
    )

    # ---------------------------------------------------------
    # Collect timing indicators
    # ---------------------------------------------------------

    timing_indicators = _safe_list(
        marriage_timing.get("indicators")
    )

    dasha_indicators = _safe_list(
        dasha_result.get("indicators")
    )

    all_indicators = (
        timing_indicators
        + dasha_indicators
    )

    # ---------------------------------------------------------
    # Calculate evidence scores
    # ---------------------------------------------------------

    positive_score = 0.0
    challenge_score = 0.0
    theme_score = 0.0

    for indicator in all_indicators:

        strength = _safe_float(
            indicator.get("strength")
        )

        indicator_type = (
            indicator.get("type")
        )

        if indicator_type == "positive":
            positive_score += strength

        elif indicator_type in {
            "negative",
            "challenge",
            "challenging",
        }:
            challenge_score += strength

        elif indicator_type == "theme":
            theme_score += strength

    # ---------------------------------------------------------
    # Include existing Dasha scores when available
    # ---------------------------------------------------------

    existing_scores = dasha_result.get(
        "scores"
    )

    if isinstance(existing_scores, dict):

        positive_score = max(
            positive_score,
            _safe_float(
                existing_scores.get(
                    "positive_score"
                )
            ),
        )

        challenge_score = max(
            challenge_score,
            _safe_float(
                existing_scores.get(
                    "challenge_score"
                )
            ),
        )

        theme_score = max(
            theme_score,
            _safe_float(
                existing_scores.get(
                    "theme_score"
                )
            ),
        )

    # ---------------------------------------------------------
    # Determine timing outlook
    # ---------------------------------------------------------

    outlook = _classify_timing(
        positive_score,
        challenge_score,
        theme_score,
    )

    # ---------------------------------------------------------
    # Confidence
    # ---------------------------------------------------------

    total_signal = (
        positive_score
        + challenge_score
        + theme_score
    )

    if total_signal >= 2.0:
        confidence = 0.85

    elif total_signal >= 1.0:
        confidence = 0.75

    elif total_signal > 0:
        confidence = 0.65

    else:
        confidence = 0.5

    # Preserve stronger confidence already generated
    # by the Dasha engine where available.

    dasha_confidence = _safe_float(
        dasha_result.get(
            "confidence"
        )
    )

    if dasha_confidence > 0:
        confidence = max(
            confidence,
            dasha_confidence,
        )

    # ---------------------------------------------------------
    # Timing window
    # ---------------------------------------------------------

    timing_window = {}

    for key in (
        "timing_window",
        "window",
        "period",
    ):

        value = marriage_timing.get(
            key
        )

        if isinstance(value, dict):
            timing_window = value
            break

    # ---------------------------------------------------------
    # Build final synthesis
    # ---------------------------------------------------------

    return {
        "available": True,
        "outlook": outlook,
        "confidence": round(
            confidence,
            2,
        ),
        "scores": {
            "positive_score": round(
                positive_score,
                2,
            ),
            "theme_score": round(
                theme_score,
                2,
            ),
            "challenge_score": round(
                challenge_score,
                2,
            ),
        },
        "summary": _build_summary(
            outlook,
            dasha_result,
        ),
        "current_dasha": {
            "mahadasha": dasha_result.get(
                "mahadasha"
            ),
            "antardasha": dasha_result.get(
                "antardasha"
            ),
            "mahadasha_start": dasha_result.get(
                "mahadasha_start"
            ),
            "mahadasha_end": dasha_result.get(
                "mahadasha_end"
            ),
            "antardasha_start": dasha_result.get(
                "antardasha_start"
            ),
            "antardasha_end": dasha_result.get(
                "antardasha_end"
            ),
        },
        "timing_window": timing_window,
        "indicators": all_indicators,
        "source_results": {
            "marriage_timing": marriage_timing,
            "dasha_marriage_reasoning": dasha_result,
        },
    }