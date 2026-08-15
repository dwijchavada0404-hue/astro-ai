from datetime import datetime, timedelta
from typing import Any

from app.astrology.transits import (
    calculate_transits,
)

from app.astrology.features.transit_house_mapping import (
    map_transits_to_natal_houses,
)

from app.astrology.features.dasha_marriage_reasoning import (
    analyze_current_dasha_for_marriage,
)

from app.astrology.features.marriage_timing import (
    analyze_marriage_timing,
)

from app.astrology.features.marriage_transits_v2 import (
    analyze_marriage_transits_v2,
)


# =========================================================
# EVENT LABELS
# =========================================================

EVENT_LABELS = {
    "marriage_timing": (
        "Marriage Timing"
    ),
    "relationship_commitment": (
        "Relationship / Commitment"
    ),
    "marriage_delay_challenge": (
        "Marriage Delay / Challenge"
    ),
}


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


def _safe_list(
    value: Any,
) -> list[Any]:

    if isinstance(
        value,
        list,
    ):
        return value

    return []


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


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


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
# DASHA PERIOD LOOKUP
# =========================================================

def _find_dasha_period_for_moment(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:

    _require_timezone(
        moment,
        "moment",
    )

    dashas = _safe_dict(
        chart.get(
            "dashas"
        )
    )

    mahadashas = _safe_list(
        dashas.get(
            "mahadashas"
        )
    )

    for md_raw in mahadashas:

        md = _safe_dict(
            md_raw
        )

        md_start_raw = md.get(
            "start"
        )

        md_end_raw = md.get(
            "end"
        )

        if not isinstance(
            md_start_raw,
            str,
        ):
            continue

        if not isinstance(
            md_end_raw,
            str,
        ):
            continue

        md_start = datetime.fromisoformat(
            md_start_raw
        )

        md_end = datetime.fromisoformat(
            md_end_raw
        )

        if not (
            md_start
            <= moment
            < md_end
        ):
            continue

        antardashas = _safe_list(
            md.get(
                "antardashas"
            )
        )

        for ad_raw in antardashas:

            ad = _safe_dict(
                ad_raw
            )

            ad_start_raw = ad.get(
                "start"
            )

            ad_end_raw = ad.get(
                "end"
            )

            if not isinstance(
                ad_start_raw,
                str,
            ):
                continue

            if not isinstance(
                ad_end_raw,
                str,
            ):
                continue

            ad_start = datetime.fromisoformat(
                ad_start_raw
            )

            ad_end = datetime.fromisoformat(
                ad_end_raw
            )

            if (
                ad_start
                <= moment
                < ad_end
            ):
                return {
                    "mahadasha": (
                        md.get(
                            "planet"
                        )
                    ),

                    "mahadasha_start": (
                        md_start_raw
                    ),

                    "mahadasha_end": (
                        md_end_raw
                    ),

                    "antardasha": (
                        ad.get(
                            "planet"
                        )
                    ),

                    "antardasha_start": (
                        ad_start_raw
                    ),

                    "antardasha_end": (
                        ad_end_raw
                    ),
                }

    raise ValueError(
        "No Vimshottari Dasha period was found "
        "for the requested moment."
    )


# =========================================================
# CHART FOR REQUESTED MOMENT
# =========================================================

def _chart_for_moment(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:

    copied = dict(
        chart
    )

    dashas = dict(
        _safe_dict(
            chart.get(
                "dashas"
            )
        )
    )

    dashas[
        "current_period"
    ] = (
        _find_dasha_period_for_moment(
            chart,
            moment,
        )
    )

    copied[
        "dashas"
    ] = dashas

    return copied


# =========================================================
# TIMING PERIOD MATCH
# =========================================================

def _find_matching_timing_period(
    timing: dict[str, Any],
    maha: str,
    antar: str,
    moment: datetime,
) -> dict[str, Any]:

    periods = _safe_list(
        timing.get(
            "periods"
        )
    )

    if not periods:

        periods = _safe_list(
            timing.get(
                "top_periods"
            )
        )

    fallback_matches = []

    for raw_item in periods:

        item = _safe_dict(
            raw_item
        )

        item_maha = str(
            item.get(
                "mahadasha",
                item.get(
                    "major",
                    "",
                ),
            )
        )

        item_antar = str(
            item.get(
                "antardasha",
                item.get(
                    "sub",
                    "",
                ),
            )
        )

        if not (
            item_maha == maha
            and item_antar == antar
        ):
            continue

        fallback_matches.append(
            item
        )

        start_raw = item.get(
            "start"
        )

        end_raw = item.get(
            "end"
        )

        if not (
            isinstance(
                start_raw,
                str,
            )
            and isinstance(
                end_raw,
                str,
            )
        ):
            continue

        try:

            period_start = (
                datetime.fromisoformat(
                    start_raw
                )
            )

            period_end = (
                datetime.fromisoformat(
                    end_raw
                )
            )

        except ValueError:
            continue

        if (
            period_start
            <= moment
            < period_end
        ):
            return item

    if fallback_matches:

        return fallback_matches[
            0
        ]

    return {}


# =========================================================
# OUTLOOK SUPPORT
# =========================================================

def _outlook_support_score(
    value: Any,
) -> float:

    mapping = {
        "strongly_supportive": 1.0,
        "very_strong": 1.0,
        "strong": 0.85,
        "supportive": 0.70,
        "moderate": 0.55,
        "mixed": 0.45,
        "neutral": 0.35,
        "weak": 0.20,
        "challenging": 0.10,
    }

    return mapping.get(
        str(
            value
            or ""
        ).lower(),
        0.0,
    )


# =========================================================
# DASHA EVIDENCE
# =========================================================

def _extract_dasha_evidence(
    current_dasha: dict[str, Any],
) -> dict[str, float]:

    scores = _safe_dict(
        current_dasha.get(
            "scores"
        )
    )

    positive_score = _safe_float(
        scores.get(
            "positive_score",
            scores.get(
                "positive",
                0.0,
            ),
        )
    )

    theme_score = _safe_float(
        scores.get(
            "theme_score",
            scores.get(
                "supportive_theme",
                0.0,
            ),
        )
    )

    challenge_score = _safe_float(
        scores.get(
            "challenge_score",
            scores.get(
                "challenge",
                0.0,
            ),
        )
    )

    confidence = _safe_float(
        current_dasha.get(
            "confidence",
            0.0,
        )
    )

    outlook_support = (
        _outlook_support_score(
            current_dasha.get(
                "outlook"
            )
        )
    )

    return {
        "positive_score": (
            positive_score
        ),

        "theme_score": (
            theme_score
        ),

        "challenge_score": (
            challenge_score
        ),

        "confidence": (
            confidence
        ),

        "outlook_support": (
            outlook_support
        ),
    }


# =========================================================
# TIMING EVIDENCE
# =========================================================

def _extract_timing_evidence(
    timing_period: dict[str, Any],
) -> dict[str, float]:

    raw_score = _safe_float(
        timing_period.get(
            "score",
            timing_period.get(
                "strength_score",
                0.0,
            ),
        )
    )

    normalized_score = _clamp(
        raw_score
        / 2.0
    )

    outlook_support = (
        _outlook_support_score(
            timing_period.get(
                "outlook"
            )
        )
    )

    return {
        "raw_score": (
            raw_score
        ),

        "normalized_score": (
            normalized_score
        ),

        "outlook_support": (
            outlook_support
        ),
    }


# =========================================================
# PLANETARY PERIOD CONTEXT
# =========================================================

def _period_relevance(
    maha: str,
    antar: str,
    seventh_lord: str | None,
) -> dict[str, float]:

    supportive_planets = {
        "Venus": 1.0,
        "Jupiter": 0.80,
        "Moon": 0.60,
        "Mercury": 0.45,
    }

    challenge_planets = {
        "Saturn": 0.55,
        "Rahu": 0.65,
        "Ketu": 0.65,
        "Mars": 0.55,
    }

    support_values = [
        supportive_planets.get(
            maha,
            0.0,
        ),

        supportive_planets.get(
            antar,
            0.0,
        ),
    ]

    challenge_values = [
        challenge_planets.get(
            maha,
            0.0,
        ),

        challenge_planets.get(
            antar,
            0.0,
        ),
    ]

    if seventh_lord:

        if maha == seventh_lord:

            support_values[
                0
            ] = max(
                support_values[
                    0
                ],
                0.90,
            )

        if antar == seventh_lord:

            support_values[
                1
            ] = max(
                support_values[
                    1
                ],
                0.90,
            )

    return {
        "support": round(
            sum(
                support_values
            )
            / 2.0,
            3,
        ),

        "challenge": round(
            sum(
                challenge_values
            )
            / 2.0,
            3,
        ),
    }


# =========================================================
# DASHA-ONLY SCORES
# =========================================================

def _score_dasha_layer(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:

    dated_chart = (
        _chart_for_moment(
            chart,
            moment,
        )
    )

    current_dasha = (
        analyze_current_dasha_for_marriage(
            dated_chart
        )
    )

    timing = (
        analyze_marriage_timing(
            dated_chart
        )
    )

    current_period = _safe_dict(
        _safe_dict(
            dated_chart.get(
                "dashas"
            )
        ).get(
            "current_period"
        )
    )

    maha = str(
        current_period.get(
            "mahadasha",
            "",
        )
    )

    antar = str(
        current_period.get(
            "antardasha",
            "",
        )
    )

    period_name = (
        f"{maha}/{antar}"
        if maha or antar
        else None
    )

    seventh_lord = (
        current_dasha.get(
            "seventh_lord"
        )
    )

    if not seventh_lord:

        seventh_lord = (
            timing.get(
                "seventh_lord"
            )
        )

    matching_period = (
        _find_matching_timing_period(
            timing,
            maha,
            antar,
            moment,
        )
    )

    timing_evidence = (
        _extract_timing_evidence(
            matching_period
        )
    )

    dasha_evidence = (
        _extract_dasha_evidence(
            current_dasha
        )
    )

    period_context = (
        _period_relevance(
            maha,
            antar,
            (
                str(
                    seventh_lord
                )
                if seventh_lord
                else None
            ),
        )
    )

    timing_support = (
        timing_evidence[
            "normalized_score"
        ]
    )

    timing_outlook = (
        timing_evidence[
            "outlook_support"
        ]
    )

    positive = _clamp(
        dasha_evidence[
            "positive_score"
        ]
    )

    theme = _clamp(
        dasha_evidence[
            "theme_score"
        ]
    )

    challenge = _clamp(
        dasha_evidence[
            "challenge_score"
        ]
    )

    confidence = _clamp(
        dasha_evidence[
            "confidence"
        ]
    )

    dasha_outlook = (
        dasha_evidence[
            "outlook_support"
        ]
    )

    period_support = (
        period_context[
            "support"
        ]
    )

    period_challenge = (
        period_context[
            "challenge"
        ]
    )

    marriage_score = (
        timing_support
        * 0.40
        + positive
        * 0.25
        + dasha_outlook
        * 0.15
        + timing_outlook
        * 0.10
        + confidence
        * 0.05
        + period_support
        * 0.05
    )

    marriage_score = _clamp(
        marriage_score
    )

    commitment_score = (
        marriage_score
        * 0.70
        + positive
        * 0.10
        + theme
        * 0.10
        + period_support
        * 0.10
    )

    commitment_score = _clamp(
        commitment_score
    )

    challenge_score = (
        challenge
        * 0.70
        + period_challenge
        * 0.20
        + (
            1.0
            - marriage_score
        )
        * 0.10
    )

    challenge_score = _clamp(
        challenge_score
    )

    return {
        "period": (
            period_name
        ),

        "seventh_lord": (
            seventh_lord
        ),

        "current_dasha": (
            current_dasha
        ),

        "matching_timing_period": (
            matching_period
        ),

        "evidence": {
            "timing": (
                timing_evidence
            ),

            "dasha": (
                dasha_evidence
            ),

            "period_context": (
                period_context
            ),
        },

        "event_scores": {
            "marriage_timing": round(
                marriage_score,
                3,
            ),

            "relationship_commitment": round(
                commitment_score,
                3,
            ),

            "marriage_delay_challenge": round(
                challenge_score,
                3,
            ),
        },
    }


# =========================================================
# TRANSIT LAYER
# =========================================================

def _score_transit_layer(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:

    transits = calculate_transits(
        moment
    )

    mapped_transits = (
        map_transits_to_natal_houses(
            chart,
            transits,
        )
    )

    marriage_transits = (
        analyze_marriage_transits_v2(
            mapped_transits
        )
    )

    return {
        "raw_transits": (
            transits
        ),

        "mapped_transits": (
            mapped_transits
        ),

        "analysis": (
            marriage_transits
        ),
    }


# =========================================================
# CONFIRMATION
# =========================================================

def _combined_confirmation(
    dasha_score: float,
    transit_score: float,
    challenge_score: float,
) -> str:

    if (
        dasha_score >= 0.75
        and transit_score >= 0.65
        and challenge_score < 0.50
    ):
        return "strong_confirmation"

    if (
        dasha_score >= 0.70
        and transit_score >= 0.55
    ):
        return "confirmed"

    if (
        dasha_score >= 0.70
        and transit_score < 0.55
    ):
        return "dasha_supported"

    if (
        transit_score >= 0.60
        and dasha_score < 0.70
    ):
        return "transit_supported"

    if challenge_score >= 0.70:
        return "challenging_confirmation"

    return "mixed_confirmation"


# =========================================================
# DELAY / CHALLENGE INTELLIGENCE
# =========================================================

def _calculate_obstructive_challenge(
    transit_challenge: float,
    transit_marriage: float,
    transit_commitment: float,
    dasha_challenge: float,
) -> float:
    """
    Distinguish actual obstruction from intense
    relationship activation.

    A difficult transit is not automatically a delay.

    Example:

        Rahu in 7th
        +
        strong Venus/Jupiter activation

    may describe unusual, intense or complicated
    relationship developments rather than denial.

    Real delay/challenge therefore requires:

        meaningful challenge
        +
        weak positive transit activation
    """

    strongest_positive = max(
        transit_marriage,
        transit_commitment,
    )

    lack_of_positive_activation = (
        1.0
        - strongest_positive
    )

    obstructive_transit = (
        transit_challenge
        * (
            0.35
            + (
                lack_of_positive_activation
                * 0.65
            )
        )
    )

    result = (
        obstructive_transit
        * 0.85
        + dasha_challenge
        * 0.15
    )

    return _clamp(
        result
    )


# =========================================================
# COMBINED SNAPSHOT
# =========================================================

def _score_marriage_snapshot(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:

    dasha_layer = (
        _score_dasha_layer(
            chart,
            moment,
        )
    )

    transit_layer = (
        _score_transit_layer(
            chart,
            moment,
        )
    )

    transit_analysis = _safe_dict(
        transit_layer.get(
            "analysis"
        )
    )

    transit_scores = _safe_dict(
        transit_analysis.get(
            "event_scores"
        )
    )

    dasha_scores = _safe_dict(
        dasha_layer.get(
            "event_scores"
        )
    )

    dasha_marriage = _safe_float(
        dasha_scores.get(
            "marriage_timing"
        )
    )

    dasha_commitment = _safe_float(
        dasha_scores.get(
            "relationship_commitment"
        )
    )

    dasha_challenge = _safe_float(
        dasha_scores.get(
            "marriage_delay_challenge"
        )
    )

    transit_marriage = _safe_float(
        transit_scores.get(
            "marriage_timing"
        )
    )

    transit_commitment = _safe_float(
        transit_scores.get(
            "relationship_commitment"
        )
    )

    transit_challenge = _safe_float(
        transit_scores.get(
            "marriage_delay_challenge"
        )
    )

    # -----------------------------------------------------
    # POSITIVE EVENT SCORES
    # -----------------------------------------------------

    marriage_score = (
        dasha_marriage
        * 0.55
        + transit_marriage
        * 0.45
        - transit_challenge
        * 0.25
    )

    marriage_score = _clamp(
        marriage_score
    )

    commitment_score = (
        dasha_commitment
        * 0.50
        + transit_commitment
        * 0.50
        - transit_challenge
        * 0.22
    )

    commitment_score = _clamp(
        commitment_score
    )

    # -----------------------------------------------------
    # REAL OBSTRUCTIVE CHALLENGE
    # -----------------------------------------------------

    delay_challenge_score = (
        _calculate_obstructive_challenge(
            transit_challenge,
            transit_marriage,
            transit_commitment,
            dasha_challenge,
        )
    )

    marriage_confirmation = (
        _combined_confirmation(
            dasha_marriage,
            transit_marriage,
            transit_challenge,
        )
    )

    commitment_confirmation = (
        _combined_confirmation(
            dasha_commitment,
            transit_commitment,
            transit_challenge,
        )
    )

    if delay_challenge_score >= 0.70:

        challenge_confirmation = (
            "strong_obstructive_challenge"
        )

    elif delay_challenge_score >= 0.55:

        challenge_confirmation = (
            "moderate_obstructive_challenge"
        )

    elif delay_challenge_score >= 0.40:

        challenge_confirmation = (
            "mild_obstructive_challenge"
        )

    else:

        challenge_confirmation = (
            "weak_obstructive_challenge"
        )

    return {
        "moment": (
            moment.isoformat()
        ),

        "period": (
            dasha_layer.get(
                "period"
            )
        ),

        "seventh_lord": (
            dasha_layer.get(
                "seventh_lord"
            )
        ),

        "dasha_scores": {
            "marriage_timing": round(
                dasha_marriage,
                3,
            ),

            "relationship_commitment": round(
                dasha_commitment,
                3,
            ),

            "marriage_delay_challenge": round(
                dasha_challenge,
                3,
            ),
        },

        "transit_scores": {
            "marriage_timing": round(
                transit_marriage,
                3,
            ),

            "relationship_commitment": round(
                transit_commitment,
                3,
            ),

            "marriage_delay_challenge": round(
                transit_challenge,
                3,
            ),
        },

        "combined_scores": {
            "marriage_timing": round(
                marriage_score,
                3,
            ),

            "relationship_commitment": round(
                commitment_score,
                3,
            ),

            "marriage_delay_challenge": round(
                delay_challenge_score,
                3,
            ),
        },

        "confirmations": {
            "marriage_timing": (
                marriage_confirmation
            ),

            "relationship_commitment": (
                commitment_confirmation
            ),

            "marriage_delay_challenge": (
                challenge_confirmation
            ),
        },

        "challenge_interpretation": {
            "raw_transit_challenge": round(
                transit_challenge,
                3,
            ),

            "positive_transit_activation": round(
                max(
                    transit_marriage,
                    transit_commitment,
                ),
                3,
            ),

            "obstructive_challenge": round(
                delay_challenge_score,
                3,
            ),
        },

        "dasha_layer": (
            dasha_layer
        ),

        "transit_layer": (
            transit_analysis
        ),
    }


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

    if score >= 0.58:
        return "moderate"

    if score >= 0.45:
        return "supportive"

    return "weak"


# =========================================================
# WINDOW THRESHOLDS
# =========================================================

def _window_threshold(
    event_name: str,
) -> float:

    thresholds = {
        "marriage_timing": 0.58,
        "relationship_commitment": 0.55,
        "marriage_delay_challenge": 0.50,
    }

    return thresholds.get(
        event_name,
        0.58,
    )


# =========================================================
# WINDOW CANDIDATES
# =========================================================

def _build_candidates(
    snapshots: list[dict[str, Any]],
    event_name: str,
) -> list[dict[str, Any]]:

    threshold = (
        _window_threshold(
            event_name
        )
    )

    candidates = []

    for snapshot in snapshots:

        scores = _safe_dict(
            snapshot.get(
                "combined_scores"
            )
        )

        score = _safe_float(
            scores.get(
                event_name
            )
        )

        if score < threshold:
            continue

        confirmations = _safe_dict(
            snapshot.get(
                "confirmations"
            )
        )

        candidates.append(
            {
                "moment": (
                    snapshot.get(
                        "moment"
                    )
                ),

                "period": (
                    snapshot.get(
                        "period"
                    )
                ),

                "score": (
                    score
                ),

                "strength": (
                    _classify_score(
                        score
                    )
                ),

                "confirmation": (
                    confirmations.get(
                        event_name
                    )
                ),

                "dasha_score": (
                    _safe_dict(
                        snapshot.get(
                            "dasha_scores"
                        )
                    ).get(
                        event_name
                    )
                ),

                "transit_score": (
                    _safe_dict(
                        snapshot.get(
                            "transit_scores"
                        )
                    ).get(
                        event_name
                    )
                ),

                "raw_transit_challenge": (
                    _safe_dict(
                        snapshot.get(
                            "transit_scores"
                        )
                    ).get(
                        "marriage_delay_challenge"
                    )
                ),
            }
        )

    return candidates


# =========================================================
# GROUP CANDIDATES
# =========================================================

def _group_candidates(
    candidates: list[dict[str, Any]],
    step_days: int,
) -> list[list[dict[str, Any]]]:

    if not candidates:
        return []

    groups = [
        [
            candidates[
                0
            ]
        ]
    ]

    maximum_gap = (
        step_days
        * 2
    )

    for item in candidates[
        1:
    ]:

        current_group = (
            groups[
                -1
            ]
        )

        previous = (
            current_group[
                -1
            ]
        )

        previous_dt = (
            datetime.fromisoformat(
                str(
                    previous[
                        "moment"
                    ]
                )
            )
        )

        current_dt = (
            datetime.fromisoformat(
                str(
                    item[
                        "moment"
                    ]
                )
            )
        )

        gap_days = (
            current_dt
            - previous_dt
        ).days

        if gap_days <= maximum_gap:

            current_group.append(
                item
            )

        else:

            groups.append(
                [
                    item
                ]
            )

    return groups


# =========================================================
# BUILD WINDOWS
# =========================================================

def _build_windows(
    snapshots: list[dict[str, Any]],
    event_name: str,
    step_days: int,
) -> list[dict[str, Any]]:

    candidates = (
        _build_candidates(
            snapshots,
            event_name,
        )
    )

    groups = (
        _group_candidates(
            candidates,
            step_days,
        )
    )

    windows = []

    for group in groups:

        peak = max(
            group,
            key=lambda item: (
                item[
                    "score"
                ]
            ),
        )

        average_score = (
            sum(
                _safe_float(
                    item.get(
                        "score"
                    )
                )
                for item in group
            )
            / len(
                group
            )
        )

        average_transit_score = (
            sum(
                _safe_float(
                    item.get(
                        "transit_score"
                    )
                )
                for item in group
            )
            / len(
                group
            )
        )

        average_raw_challenge = (
            sum(
                _safe_float(
                    item.get(
                        "raw_transit_challenge"
                    )
                )
                for item in group
            )
            / len(
                group
            )
        )

        start_dt = (
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

        final_dt = (
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

        end_dt = (
            final_dt
            + timedelta(
                days=step_days
            )
        )

        peak_dt = (
            datetime.fromisoformat(
                str(
                    peak[
                        "moment"
                    ]
                )
            )
        )

        windows.append(
            {
                "event": (
                    event_name
                ),

                "start": (
                    start_dt.date().isoformat()
                ),

                "end": (
                    end_dt.date().isoformat()
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
                    average_transit_score,
                    3,
                ),

                "average_raw_challenge": round(
                    average_raw_challenge,
                    3,
                ),

                "peak": {
                    "date": (
                        peak_dt.date().isoformat()
                    ),

                    "period": (
                        peak.get(
                            "period"
                        )
                    ),

                    "score": round(
                        _safe_float(
                            peak.get(
                                "score"
                            )
                        ),
                        3,
                    ),

                    "strength": (
                        peak.get(
                            "strength"
                        )
                    ),

                    "confirmation": (
                        peak.get(
                            "confirmation"
                        )
                    ),

                    "dasha_score": (
                        peak.get(
                            "dasha_score"
                        )
                    ),

                    "transit_score": (
                        peak.get(
                            "transit_score"
                        )
                    ),

                    "raw_transit_challenge": (
                        peak.get(
                            "raw_transit_challenge"
                        )
                    ),
                },

                "snapshot_count": (
                    len(
                        group
                    )
                ),
            }
        )

    windows.sort(
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

    return windows


# =========================================================
# EVENT SUMMARY
# =========================================================

def _event_summary(
    event_name: str,
    windows: list[dict[str, Any]],
) -> dict[str, Any]:

    label = (
        EVENT_LABELS[
            event_name
        ]
    )

    if not windows:

        return {
            "available": False,

            "event": (
                event_name
            ),

            "label": (
                label
            ),

            "outlook": (
                "no_strong_window"
            ),

            "confidence": 0.4,

            "summary": (
                f"No sufficiently strong "
                f"{label.lower()} window was identified "
                "in the scanned period."
            ),

            "primary_window": {},

            "secondary_windows": [],
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

    confirmation = (
        peak.get(
            "confirmation"
        )
    )

    if (
        peak_score >= 0.82
        and confirmation
        == "strong_confirmation"
    ):
        confidence = 0.95

    elif peak_score >= 0.70:
        confidence = 0.88

    elif peak_score >= 0.58:
        confidence = 0.75

    else:
        confidence = 0.62

    if event_name == (
        "marriage_delay_challenge"
    ):

        summary = (
            f"The strongest obstructive marriage / "
            f"relationship phase runs from "
            f"{primary.get('start')} to "
            f"{primary.get('end')}, with peak "
            f"challenge around {peak.get('date')}."
        )

    else:

        summary = (
            f"The strongest {label.lower()} window "
            f"runs from {primary.get('start')} to "
            f"{primary.get('end')}, with peak activation "
            f"around {peak.get('date')}."
        )

    return {
        "available": True,

        "event": (
            event_name
        ),

        "label": (
            label
        ),

        "outlook": (
            primary.get(
                "strength"
            )
        ),

        "confidence": (
            confidence
        ),

        "confirmation": (
            confirmation
        ),

        "summary": (
            summary
        ),

        "primary_window": (
            primary
        ),

        "secondary_windows": (
            windows[
                1:4
            ]
        ),
    }


# =========================================================
# STRONGEST POSITIVE EVENT
# =========================================================

def _find_strongest_event(
    events: dict[str, Any],
) -> str | None:

    strongest_event = None
    strongest_score = -1.0

    for event_name in (
        "marriage_timing",
        "relationship_commitment",
    ):

        event_data = _safe_dict(
            events.get(
                event_name
            )
        )

        if not event_data.get(
            "available"
        ):
            continue

        primary = _safe_dict(
            event_data.get(
                "primary_window"
            )
        )

        peak = _safe_dict(
            primary.get(
                "peak"
            )
        )

        score = _safe_float(
            peak.get(
                "score"
            )
        )

        if score > strongest_score:

            strongest_score = (
                score
            )

            strongest_event = (
                event_name
            )

    return strongest_event


# =========================================================
# MAIN FORECAST SCANNER
# =========================================================

def scan_marriage_forecast_v2(
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

    if (
        end
        - start
    ).days > 3650:

        raise ValueError(
            "Marriage forecast range must not exceed "
            "10 years."
        )

    snapshots = []

    moment = start

    while moment <= end:

        snapshots.append(
            _score_marriage_snapshot(
                chart,
                moment,
            )
        )

        moment = (
            moment
            + timedelta(
                days=step_days
            )
        )

    events = {}

    for event_name in EVENT_LABELS:

        windows = (
            _build_windows(
                snapshots,
                event_name,
                step_days,
            )
        )

        events[
            event_name
        ] = (
            _event_summary(
                event_name,
                windows,
            )
        )

    strongest_event = (
        _find_strongest_event(
            events
        )
    )

    return {
        "available": True,

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

        "strongest_event": (
            strongest_event
        ),

        "events": (
            events
        ),

        "snapshots": (
            snapshots
        ),
    }