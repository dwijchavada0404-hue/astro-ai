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


def _format_date(value: Any) -> str | None:
    """
    Convert an ISO datetime into YYYY-MM-DD.
    """

    if not isinstance(value, str):
        return None

    if len(value) >= 10:
        return value[:10]

    return value


def _extract_interpretations(
    indicators: Any,
    limit: int = 5,
) -> list[str]:
    """
    Extract unique human-readable interpretations.
    """

    results: list[str] = []

    for indicator in _safe_list(indicators):

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
            and interpretation not in results
        ):
            results.append(
                interpretation
            )

        if len(results) >= limit:
            break

    return results


def _clean_window(
    window: Any,
) -> dict[str, Any]:
    """
    Convert a timing-synthesis window into a compact
    user-facing structure.
    """

    window = _safe_dict(window)

    if not window:
        return {}

    return {
        "period": window.get(
            "period"
        ),
        "mahadasha": window.get(
            "mahadasha"
        ),
        "antardasha": window.get(
            "antardasha"
        ),
        "start": _format_date(
            window.get("start")
        ),
        "end": _format_date(
            window.get("end")
        ),
        "outlook": window.get(
            "outlook"
        ),
        "priority": window.get(
            "priority"
        ),
        "base_score": _safe_float(
            window.get(
                "base_score"
            )
        ),
        "career_adjusted_score": _safe_float(
            window.get(
                "career_adjusted_score"
            )
        ),
        "direct_tenth_lord_activation": (
            bool(
                window.get(
                    "direct_tenth_lord_activation"
                )
            )
        ),
        "direct_tenth_house_activation": (
            bool(
                window.get(
                    "direct_tenth_house_activation"
                )
            )
        ),
        "reasons": [
            reason
            for reason in window.get(
                "reasons",
                [],
            )
            if isinstance(
                reason,
                str,
            )
        ][:5],
    }


def _build_overall_outlook(
    career_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build high-level natal career outlook.
    """

    if not career_synthesis.get(
        "available"
    ):
        return {
            "available": False,
        }

    return {
        "available": True,
        "outlook": career_synthesis.get(
            "outlook"
        ),
        "confidence": _safe_float(
            career_synthesis.get(
                "confidence"
            )
        ),
        "summary": career_synthesis.get(
            "summary"
        ),
        "strengths": [
            item
            for item in career_synthesis.get(
                "strengths",
                [],
            )
            if isinstance(
                item,
                str,
            )
        ][:5],
        "challenges": [
            item
            for item in career_synthesis.get(
                "challenges",
                [],
            )
            if isinstance(
                item,
                str,
            )
        ][:4],
    }


def _build_professional_direction(
    career_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the user-facing professional direction section
    from the career synthesis layer.
    """

    function = _safe_dict(
        career_synthesis.get(
            "core_professional_function"
        )
    )

    themes = _safe_list(
        function.get(
            "themes"
        )
    )

    theme_names: list[str] = []

    for theme in themes:

        name = theme.get(
            "theme"
        )

        if (
            isinstance(name, str)
            and name not in theme_names
        ):
            theme_names.append(
                name
            )

    return {
        "summary": career_synthesis.get(
            "professional_direction"
        ),
        "core_function": function.get(
            "summary"
        ),
        "dominant_function_groups": (
            theme_names[:4]
        ),
    }


def _build_work_environment(
    career_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build likely professional environment without
    converting it into an unsupported occupation claim.
    """

    environment = _safe_dict(
        career_synthesis.get(
            "work_environment"
        )
    )

    return {
        "active": bool(
            environment.get(
                "active"
            )
        ),
        "summary": environment.get(
            "summary"
        ),
        "themes": [
            theme
            for theme in environment.get(
                "themes",
                [],
            )
            if isinstance(
                theme,
                str,
            )
        ],
    }


def _build_current_period(
    current_dasha: dict[str, Any],
    timing_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Explain the current career period.

    Important distinction:

    - direct activation describes how strongly career matters
      are activated;
    - outlook describes how easy or difficult the period may be.

    A period can therefore be strongly career-active while
    still producing mixed results.
    """

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

    period = (
        f"{mahadasha}/{antardasha}"
        if mahadasha and antardasha
        else None
    )

    scores = _safe_dict(
        current_dasha.get(
            "scores"
        )
    )

    positive_score = _safe_float(
        scores.get(
            "positive_score"
        )
    )

    challenge_score = _safe_float(
        scores.get(
            "challenge_score"
        )
    )

    theme_score = _safe_float(
        scores.get(
            "theme_score"
        )
    )

    timing_current = _safe_dict(
        timing_synthesis.get(
            "current_period"
        )
    )

    direct_windows = _safe_list(
        timing_synthesis.get(
            "direct_career_activation_windows"
        )
    )

    direct_lord = False
    direct_house = False

    for window in direct_windows:

        if (
            window.get("mahadasha")
            == mahadasha
            and window.get("antardasha")
            == antardasha
        ):
            direct_lord = bool(
                window.get(
                    "direct_tenth_lord_activation"
                )
            )

            direct_house = bool(
                window.get(
                    "direct_tenth_house_activation"
                )
            )

            break

    if direct_lord and direct_house:
        activation = "very_strong"

    elif direct_lord or direct_house:
        activation = "direct"

    elif positive_score > 0:
        activation = "active"

    else:
        activation = "background"

    outlook = current_dasha.get(
        "outlook"
    )

    if (
        direct_lord
        and challenge_score > 0
    ):
        summary = (
            f"The current {period} period directly activates "
            "career because the active period involves the "
            "10th lord. However, the same period also contains "
            "challenging factors, so professional matters may "
            "be important and active without necessarily being "
            "effortless. Progress may require patience, "
            "responsibility and adjustment."
        )

    elif direct_house and challenge_score > 0:
        summary = (
            f"The current {period} period directly activates "
            "career through a planet connected with the 10th "
            "house, although challenging factors suggest that "
            "results may require additional effort or adjustment."
        )

    elif direct_lord or direct_house:
        summary = (
            f"The current {period} period contains direct "
            "career activation and may bring professional "
            "developments, decisions or increased focus on work."
        )

    elif outlook in {
        "strongly_supportive",
        "supportive",
    }:
        summary = (
            f"The current {period} period is supportive for "
            "professional development, although it is not among "
            "the strongest direct career-activation periods."
        )

    elif outlook == "mixed":
        summary = (
            f"The current {period} period is mixed for career. "
            "Professional themes are active, but supportive and "
            "challenging influences operate together."
        )

    else:
        summary = (
            f"The current {period} period does not show one of "
            "the strongest career signals identified by the engine."
        )

    return {
        "available": True,
        "period": period,
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
        "activation_strength": activation,
        "direct_tenth_lord_activation": (
            direct_lord
        ),
        "direct_tenth_house_activation": (
            direct_house
        ),
        "confidence": max(
            _safe_float(
                current_dasha.get(
                    "confidence"
                )
            ),
            _safe_float(
                timing_current.get(
                    "confidence"
                )
            ),
        ),
        "scores": {
            "positive_score": (
                positive_score
            ),
            "challenge_score": (
                challenge_score
            ),
            "theme_score": (
                theme_score
            ),
        },
        "summary": summary,
        "evidence": _extract_interpretations(
            current_dasha.get(
                "indicators"
            ),
            limit=5,
        ),
    }


def _build_near_term_progression(
    timing_synthesis: dict[str, Any],
    current_dasha: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a chronological near-term career progression.

    Current period is excluded because it already has its
    own section.
    """

    upcoming = _safe_list(
        timing_synthesis.get(
            "upcoming_windows"
        )
    )

    current_md = current_dasha.get(
        "mahadasha"
    )

    current_ad = current_dasha.get(
        "antardasha"
    )

    future: list[dict[str, Any]] = []

    for window in upcoming:

        if (
            window.get("mahadasha")
            == current_md
            and window.get("antardasha")
            == current_ad
        ):
            continue

        future.append(
            _clean_window(
                window
            )
        )

    future = future[:4]

    if future:

        first = future[0]

        summary = (
            f"After the current period, the next relevant "
            f"career phase identified is "
            f"{first.get('period')}, beginning "
            f"{first.get('start')}."
        )

    else:

        summary = (
            "No additional near-term career periods were "
            "available in the timing synthesis."
        )

    return {
        "summary": summary,
        "windows": future,
    }


def _build_timing_outlook(
    timing_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Separate practical near-term timing from the absolute
    strongest long-term timing score.
    """

    nearest = _clean_window(
        timing_synthesis.get(
            "nearest_strong_window"
        )
    )

    strongest = _clean_window(
        timing_synthesis.get(
            "strongest_long_term_window"
        )
    )

    if nearest:

        nearest_summary = (
            f"The nearest strong career-supportive window "
            f"is {nearest.get('period')}, from "
            f"{nearest.get('start')} to "
            f"{nearest.get('end')}."
        )

    else:

        nearest_summary = (
            "No strong nearby career window was identified."
        )

    if strongest:

        strongest_summary = (
            f"The highest-scoring long-term career window "
            f"is {strongest.get('period')}, from "
            f"{strongest.get('start')} to "
            f"{strongest.get('end')}."
        )

    else:

        strongest_summary = (
            "No separate long-term career window was identified."
        )

    return {
        "nearest_strong_window": nearest,
        "nearest_window_summary": (
            nearest_summary
        ),
        "strongest_long_term_window": (
            strongest
        ),
        "long_term_summary": (
            strongest_summary
        ),
    }


def _build_direct_activation(
    timing_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a compact list of periods directly involving
    the 10th lord or planets occupying the 10th house.
    """

    windows = _safe_list(
        timing_synthesis.get(
            "direct_career_activation_windows"
        )
    )

    cleaned = [
        _clean_window(window)
        for window in windows[:5]
    ]

    if cleaned:

        summary = (
            "These periods directly activate the 10th lord "
            "or planets placed in the 10th house. They are "
            "especially relevant for career developments, "
            "although direct activation does not automatically "
            "mean easy or positive results."
        )

    else:

        summary = (
            "No direct 10th-house or 10th-lord activation "
            "windows were identified."
        )

    return {
        "summary": summary,
        "windows": cleaned,
    }


def generate_career_narrative(
    career_reasoning: dict[str, Any],
    career_interpretation: dict[str, Any],
    career_planet_analysis: dict[str, Any],
    career_synthesis: dict[str, Any],
    current_dasha: dict[str, Any],
    career_timing: dict[str, Any],
    timing_synthesis: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert structured career evidence into a clean
    user-facing career reading.

    This layer does not calculate new astrology.

    It only organises and explains evidence generated by:
    - natal career reasoning
    - career interpretation
    - planetary career analysis
    - career synthesis
    - current Dasha reasoning
    - career timing
    - career timing synthesis
    """

    if not career_synthesis.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Career synthesis is unavailable."
            ),
        }

    overall = _build_overall_outlook(
        career_synthesis
    )

    professional_direction = (
        _build_professional_direction(
            career_synthesis
        )
    )

    work_environment = (
        _build_work_environment(
            career_synthesis
        )
    )

    current_period = (
        _build_current_period(
            current_dasha,
            timing_synthesis,
        )
    )

    near_term = (
        _build_near_term_progression(
            timing_synthesis,
            current_dasha,
        )
    )

    timing_outlook = (
        _build_timing_outlook(
            timing_synthesis
        )
    )

    direct_activation = (
        _build_direct_activation(
            timing_synthesis
        )
    )

    confidence = max(
        _safe_float(
            career_synthesis.get(
                "confidence"
            )
        ),
        _safe_float(
            current_dasha.get(
                "confidence"
            )
        ),
    )

    tenth_house = _safe_dict(
        career_synthesis.get(
            "tenth_house"
        )
    )

    tenth_lord = _safe_dict(
        career_synthesis.get(
            "tenth_lord"
        )
    )

    return {
        "available": True,

        "overall_outlook": overall,

        "career_foundation": {
            "tenth_house_sign": (
                tenth_house.get(
                    "sign"
                )
            ),
            "tenth_lord": (
                tenth_house.get(
                    "lord"
                )
            ),
            "tenth_house_occupants": (
                tenth_house.get(
                    "occupants",
                    [],
                )
            ),
            "tenth_lord_house": (
                tenth_lord.get(
                    "house"
                )
            ),
            "tenth_lord_sign": (
                tenth_lord.get(
                    "sign"
                )
            ),
        },

        "professional_direction": (
            professional_direction
        ),

        "work_environment": (
            work_environment
        ),

        "current_period": (
            current_period
        ),

        "near_term_progression": (
            near_term
        ),

        "career_timing": (
            timing_outlook
        ),

        "direct_career_activation": (
            direct_activation
        ),

        "confidence": round(
            confidence,
            2,
        ),

        "disclaimer": (
            "Astrological career analysis describes symbolic "
            "patterns and periods of stronger or weaker support. "
            "It should not be treated as a guaranteed prediction "
            "of employment, promotion, income or other "
            "professional outcomes."
        ),
    }