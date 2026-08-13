from typing import Any


def _safe_list(value: Any) -> list[dict[str, Any]]:
    """Return only dictionary items from a list."""
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
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _format_date(value: Any) -> str | None:
    """
    Convert an ISO datetime string into a simple YYYY-MM-DD date.

    The original value is left untouched elsewhere in the engine.
    """

    if not isinstance(value, str):
        return None

    if len(value) < 10:
        return value

    return value[:10]


def _extract_interpretations(
    indicators: Any,
    limit: int = 5,
) -> list[str]:
    """Extract unique human-readable interpretations."""

    results: list[str] = []

    for indicator in _safe_list(indicators):

        interpretation = indicator.get(
            "interpretation"
        )

        if not isinstance(interpretation, str):
            continue

        interpretation = interpretation.strip()

        if (
            interpretation
            and interpretation not in results
        ):
            results.append(interpretation)

        if len(results) >= limit:
            break

    return results


def _build_period_summary(
    period: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert one ranked marriage-timing period into a
    compact user-facing structure.
    """

    mahadasha = period.get("mahadasha")
    antardasha = period.get("antardasha")

    if mahadasha and antardasha:
        period_name = (
            f"{mahadasha}/{antardasha}"
        )
    else:
        period_name = "Unknown period"

    return {
        "period": period_name,
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "start": _format_date(
            period.get("start")
        ),
        "end": _format_date(
            period.get("end")
        ),
        "score": _safe_float(
            period.get("score")
        ),
        "outlook": period.get("outlook"),
        "reasons": _extract_interpretations(
            period.get("indicators"),
            limit=4,
        ),
    }


def _select_future_periods(
    marriage_timing: dict[str, Any],
    current_dasha: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Select the strongest relevant periods from the timing engine.

    We prioritise the engine's ranked top periods.

    Periods that have already fully ended before the current
    Antardasha are excluded when possible.
    """

    periods = _safe_list(
        marriage_timing.get("periods")
    )

    if not periods:
        periods = _safe_list(
            marriage_timing.get("top_periods")
        )

    current_start = current_dasha.get(
        "antardasha_start"
    )

    future_periods: list[dict[str, Any]] = []

    for period in periods:

        end = period.get("end")

        if (
            isinstance(current_start, str)
            and isinstance(end, str)
            and end < current_start
        ):
            continue

        future_periods.append(period)

    if not future_periods:
        future_periods = periods

    future_periods = sorted(
        future_periods,
        key=lambda item: (
            -_safe_float(
                item.get("score")
            ),
            str(
                item.get("start", "")
            ),
        ),
    )

    return future_periods


def _build_overall_outlook(
    marriage_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """Build the high-level marriage outlook section."""

    if not marriage_synthesis.get("available"):
        return {
            "available": False,
            "summary": (
                "Overall marriage analysis is unavailable."
            ),
        }

    outlook = marriage_synthesis.get(
        "outlook",
        "unknown",
    )

    confidence = _safe_float(
        marriage_synthesis.get(
            "confidence"
        )
    )

    positive_factors = _extract_interpretations(
        marriage_synthesis.get(
            "positive_factors"
        ),
        limit=4,
    )

    challenges = _extract_interpretations(
        marriage_synthesis.get(
            "challenges"
        ),
        limit=3,
    )

    if outlook == "favourable":
        summary = (
            "The overall natal marriage indicators are favourable. "
            "The chart contains meaningful support for partnership "
            "and marriage, although the exact timing depends on "
            "activation through planetary periods."
        )

    elif outlook == "mixed":
        summary = (
            "The natal marriage indicators are mixed, showing both "
            "supportive and challenging influences."
        )

    else:
        summary = (
            "The natal chart is generally supportive of marriage, "
            "while also showing some themes that may shape how "
            "relationships develop."
        )

    return {
        "available": True,
        "outlook": outlook,
        "confidence": confidence,
        "summary": summary,
        "supporting_factors": positive_factors,
        "challenges": challenges,
    }


def _build_relationship_profile(
    seventh_house_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build relationship/spouse characteristics directly from
    the existing 7th-house reasoning.
    """

    if not seventh_house_analysis.get(
        "available"
    ):
        return {
            "available": False,
        }

    seventh_house = seventh_house_analysis.get(
        "seventh_house",
        {},
    )

    seventh_lord = seventh_house_analysis.get(
        "seventh_lord",
        {},
    )

    sign_attributes = (
        seventh_house_analysis.get(
            "sign_attributes",
            {},
        )
    )

    indicators = _extract_interpretations(
        seventh_house_analysis.get(
            "indicators"
        ),
        limit=5,
    )

    return {
        "available": True,
        "seventh_house_sign": (
            seventh_house.get("sign")
            if isinstance(
                seventh_house,
                dict,
            )
            else None
        ),
        "seventh_lord": (
            seventh_lord.get("planet")
            if isinstance(
                seventh_lord,
                dict,
            )
            else None
        ),
        "element": (
            sign_attributes.get("element")
            if isinstance(
                sign_attributes,
                dict,
            )
            else None
        ),
        "modality": (
            sign_attributes.get("modality")
            if isinstance(
                sign_attributes,
                dict,
            )
            else None
        ),
        "themes": indicators,
    }


def _build_meeting_theme(
    marriage_planet_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build evidence-backed indications about social context
    through which relationships may develop.
    """

    if not marriage_planet_analysis.get(
        "available"
    ):
        return {
            "available": False,
        }

    planets = marriage_planet_analysis.get(
        "planets",
        {},
    )

    venus = (
        planets.get("Venus", {})
        if isinstance(planets, dict)
        else {}
    )

    venus_house = (
        venus.get("house")
        if isinstance(venus, dict)
        else None
    )

    indicators = _safe_list(
        marriage_planet_analysis.get(
            "indicators"
        )
    )

    relevant: list[str] = []

    for indicator in indicators:

        factor = indicator.get("factor")

        if factor in {
            "venus_house",
            "venus_dignity",
        }:

            interpretation = indicator.get(
                "interpretation"
            )

            if (
                isinstance(
                    interpretation,
                    str,
                )
                and interpretation
                not in relevant
            ):
                relevant.append(
                    interpretation
                )

    if venus_house == 11:
        summary = (
            "The chart supports relationship developments through "
            "friendships, social circles, professional networks, "
            "communities or mutual connections."
        )

    else:
        summary = (
            "The current evidence does not support a specific "
            "meeting context strongly enough for a directional "
            "statement."
        )

    return {
        "available": True,
        "venus_house": venus_house,
        "summary": summary,
        "evidence": relevant,
    }


def _build_distance_theme(
    marriage_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Summarise distance, relocation, foreign or privacy themes
    only when those themes already exist in the synthesis layer.
    """

    themes = _safe_list(
        marriage_synthesis.get(
            "themes"
        )
    )

    relevant: list[str] = []

    relevant_factors = {
        "seventh_lord_twelfth_house",
        "mars_twelfth_house",
    }

    for theme in themes:

        factor = theme.get("factor")

        if factor not in relevant_factors:
            continue

        interpretation = theme.get(
            "interpretation"
        )

        if (
            isinstance(
                interpretation,
                str,
            )
            and interpretation
            not in relevant
        ):
            relevant.append(
                interpretation
            )

    if relevant:
        summary = (
            "Distance, relocation, privacy or foreign-environment "
            "themes may play a meaningful role in relationship "
            "development. This does not necessarily mean a foreign "
            "spouse; it can also describe living away from the "
            "birthplace, long-distance circumstances or relocation."
        )

    else:
        summary = (
            "No strong distance or relocation theme was identified "
            "from the current marriage synthesis."
        )

    return {
        "active": bool(relevant),
        "summary": summary,
        "evidence": relevant,
    }


def _build_current_period(
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    """Build the current Dasha interpretation."""

    if not current_dasha.get("available"):
        return {
            "available": False,
        }

    mahadasha = current_dasha.get(
        "mahadasha"
    )

    antardasha = current_dasha.get(
        "antardasha"
    )

    outlook = current_dasha.get(
        "outlook"
    )

    confidence = _safe_float(
        current_dasha.get(
            "confidence"
        )
    )

    if outlook in {
        "strongly_supportive",
        "supportive",
        "moderately_supportive",
    }:
        summary = (
            f"The current {mahadasha}/{antardasha} period "
            "contains active support for marriage-related "
            "developments."
        )

    elif outlook == "mixed":
        summary = (
            f"The current {mahadasha}/{antardasha} period "
            "is mixed for marriage timing. Relationship themes "
            "may be active, but the period does not currently "
            "show the strongest direct marriage activation."
        )

    else:
        summary = (
            f"The current {mahadasha}/{antardasha} period "
            "does not appear to be among the strongest "
            "marriage-timing periods identified by the engine."
        )

    return {
        "available": True,
        "period": (
            f"{mahadasha}/{antardasha}"
            if mahadasha and antardasha
            else None
        ),
        "start": _format_date(
            current_dasha.get(
                "antardasha_start"
            )
        ),
        "end": _format_date(
            current_dasha.get(
                "antardasha_end"
            )
        ),
        "outlook": outlook,
        "confidence": confidence,
        "summary": summary,
        "evidence": _extract_interpretations(
            current_dasha.get(
                "indicators"
            ),
            limit=4,
        ),
    }


def generate_marriage_narrative(
    seventh_house_analysis: dict[str, Any],
    marriage_planet_analysis: dict[str, Any],
    marriage_synthesis: dict[str, Any],
    marriage_timing: dict[str, Any],
    current_dasha: dict[str, Any],
    timing_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert structured marriage-analysis evidence into a
    clean user-facing narrative.

    This function does not calculate new astrology.

    Every directional statement must be supported by an
    existing analysis layer.
    """

    if not marriage_synthesis.get("available"):
        return {
            "available": False,
            "reason": (
                "Marriage synthesis is unavailable."
            ),
        }

    ranked_periods = _select_future_periods(
        marriage_timing,
        current_dasha,
    )

    strong_periods = [
        period
        for period in ranked_periods
        if period.get("outlook")
        in {
            "strongly_supportive",
            "supportive",
        }
    ]

    primary_period = (
        _build_period_summary(
            strong_periods[0]
        )
        if strong_periods
        else {}
    )

    secondary_periods = [
        _build_period_summary(period)
        for period in strong_periods[1:4]
    ]

    overall = _build_overall_outlook(
        marriage_synthesis
    )

    relationship_profile = (
        _build_relationship_profile(
            seventh_house_analysis
        )
    )

    meeting_theme = _build_meeting_theme(
        marriage_planet_analysis
    )

    distance_theme = (
        _build_distance_theme(
            marriage_synthesis
        )
    )

    current_period = _build_current_period(
        current_dasha
    )

    if primary_period:

        primary_name = primary_period.get(
            "period"
        )

        primary_start = primary_period.get(
            "start"
        )

        primary_end = primary_period.get(
            "end"
        )

        timing_summary = (
            f"The strongest marriage-supportive period currently "
            f"identified by the timing engine is {primary_name}, "
            f"from {primary_start} to {primary_end}. "
            "This should be treated as a high-support window rather "
            "than a guaranteed event date."
        )

    else:

        timing_summary = (
            "The timing engine does not currently identify a "
            "sufficiently strong future marriage window."
        )

    overall_confidence = max(
        _safe_float(
            marriage_synthesis.get(
                "confidence"
            )
        ),
        _safe_float(
            timing_synthesis.get(
                "confidence"
            )
        ),
    )

    return {
        "available": True,
        "overall_outlook": overall,
        "marriage_timing": {
            "summary": timing_summary,
            "primary_window": primary_period,
            "secondary_windows": secondary_periods,
        },
        "current_period": current_period,
        "relationship_profile": relationship_profile,
        "meeting_context": meeting_theme,
        "distance_relocation_theme": distance_theme,
        "confidence": round(
            overall_confidence,
            2,
        ),
        "disclaimer": (
            "Astrological timing represents interpretive periods "
            "of stronger or weaker symbolic support and should not "
            "be treated as a guaranteed prediction of an event."
        ),
    }