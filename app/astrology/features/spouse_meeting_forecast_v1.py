from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.transits import (
    calculate_transits,
)

from app.astrology.features.transit_house_mapping import (
    map_transits_to_natal_houses,
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
# DASHA LOOKUP
# =========================================================

def _find_dasha_period(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:

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

                    "antardasha": (
                        ad.get(
                            "planet"
                        )
                    ),

                    "mahadasha_start": (
                        md_start_raw
                    ),

                    "mahadasha_end": (
                        md_end_raw
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
# DASHA MEETING SCORE
# =========================================================

def _score_dasha_for_spouse_meeting(
    period: dict[str, Any],
) -> dict[str, Any]:

    maha = str(
        period.get(
            "mahadasha",
            "",
        )
        or ""
    )

    antar = str(
        period.get(
            "antardasha",
            "",
        )
        or ""
    )

    # -----------------------------------------------------
    # PLANET-SPECIFIC MEETING POTENTIAL
    # -----------------------------------------------------
    #
    # Venus:
    #     attraction / relationship initiation
    #
    # Jupiter:
    #     expansion / commitment / meaningful connection
    #
    # Moon:
    #     emotional receptivity / social bonding
    #
    # Mercury:
    #     communication / introductions / networking
    #
    # Rahu:
    #     unusual or sudden connections, but unstable
    #
    # -----------------------------------------------------

    support_weights = {
        "Venus": 1.00,
        "Jupiter": 0.82,
        "Moon": 0.68,
        "Mercury": 0.62,
        "Rahu": 0.42,
        "Mars": 0.28,
        "Saturn": 0.20,
        "Ketu": 0.12,
        "Sun": 0.22,
    }

    maha_support = (
        support_weights.get(
            maha,
            0.20,
        )
    )

    antar_support = (
        support_weights.get(
            antar,
            0.20,
        )
    )

    score = (
        maha_support * 0.45
        + antar_support * 0.55
    )

    # Venus double activation is particularly relevant
    # for attraction and relationship-opening periods.

    if (
        maha == "Venus"
        and antar == "Venus"
    ):
        score += 0.10

    # Jupiter/Venus combinations are also relationship
    # supportive.

    if {
        maha,
        antar,
    } == {
        "Venus",
        "Jupiter",
    }:
        score += 0.08

    # Rahu can increase sudden meeting probability but
    # should not be treated as purely beneficial.

    unusual_connection = (
        maha == "Rahu"
        or antar == "Rahu"
    )

    return {
        "period": (
            f"{maha}/{antar}"
        ),

        "mahadasha": (
            maha
        ),

        "antardasha": (
            antar
        ),

        "score": round(
            _clamp(
                score
            ),
            3,
        ),

        "unusual_connection": (
            unusual_connection
        ),
    }


# =========================================================
# TRANSIT PLANET HOUSE
# =========================================================

def _planet_house(
    mapped_transits: dict[str, Any],
    planet: str,
) -> int | None:

    planets = _safe_dict(
        mapped_transits.get(
            "planets"
        )
    )

    data = _safe_dict(
        planets.get(
            planet
        )
    )

    house = data.get(
        "natal_house"
    )

    if isinstance(
        house,
        int,
    ):
        return house

    return None


# =========================================================
# HOUSE SUPPORT
# =========================================================

def _house_support(
    house: int | None,
    weights: dict[int, float],
) -> float:

    if house is None:
        return 0.0

    return weights.get(
        house,
        0.0,
    )


# =========================================================
# TRANSIT MEETING SCORE
# =========================================================

def _score_transits_for_spouse_meeting(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:

    venus_house = (
        _planet_house(
            mapped_transits,
            "Venus",
        )
    )

    jupiter_house = (
        _planet_house(
            mapped_transits,
            "Jupiter",
        )
    )

    moon_house = (
        _planet_house(
            mapped_transits,
            "Moon",
        )
    )

    mercury_house = (
        _planet_house(
            mapped_transits,
            "Mercury",
        )
    )

    saturn_house = (
        _planet_house(
            mapped_transits,
            "Saturn",
        )
    )

    rahu_house = (
        _planet_house(
            mapped_transits,
            "Rahu",
        )
    )

    ketu_house = (
        _planet_house(
            mapped_transits,
            "Ketu",
        )
    )

    mars_house = (
        _planet_house(
            mapped_transits,
            "Mars",
        )
    )

    # -----------------------------------------------------
    # SUPPORTIVE HOUSES FOR MEETING / CONNECTION
    # -----------------------------------------------------
    #
    # 1  = visibility / new phase
    # 3  = communication / social movement
    # 5  = romance
    # 7  = partnership
    # 9  = travel / broader social environment
    # 10 = work / public interactions
    # 11 = networks / friends / social circles
    # -----------------------------------------------------

    venus_support = (
        _house_support(
            venus_house,
            {
                1: 0.55,
                3: 0.50,
                5: 1.00,
                7: 1.00,
                9: 0.60,
                10: 0.45,
                11: 0.90,
            },
        )
    )

    jupiter_support = (
        _house_support(
            jupiter_house,
            {
                1: 0.75,
                5: 0.85,
                7: 1.00,
                9: 0.65,
                11: 0.80,
            },
        )
    )

    moon_support = (
        _house_support(
            moon_house,
            {
                1: 0.45,
                3: 0.55,
                5: 0.80,
                7: 0.90,
                9: 0.45,
                11: 0.70,
            },
        )
    )

    mercury_support = (
        _house_support(
            mercury_house,
            {
                1: 0.40,
                3: 0.90,
                5: 0.55,
                7: 0.65,
                10: 0.50,
                11: 0.85,
            },
        )
    )

    support_score = (
        venus_support * 0.34
        + jupiter_support * 0.28
        + moon_support * 0.18
        + mercury_support * 0.20
    )

    # -----------------------------------------------------
    # CHALLENGE PRESSURE
    # -----------------------------------------------------

    challenge_weights = {
        1: 0.35,
        5: 0.55,
        7: 1.00,
        8: 0.70,
        12: 0.55,
    }

    saturn_challenge = (
        _house_support(
            saturn_house,
            challenge_weights,
        )
        * 0.75
    )

    rahu_challenge = (
        _house_support(
            rahu_house,
            challenge_weights,
        )
        * 0.85
    )

    ketu_challenge = (
        _house_support(
            ketu_house,
            challenge_weights,
        )
        * 0.70
    )

    mars_challenge = (
        _house_support(
            mars_house,
            challenge_weights,
        )
        * 0.65
    )

    challenge_score = (
        saturn_challenge * 0.28
        + rahu_challenge * 0.30
        + ketu_challenge * 0.20
        + mars_challenge * 0.22
    )

    # -----------------------------------------------------
    # RAHU SPECIAL CASE
    # -----------------------------------------------------
    #
    # Rahu in the 5th / 7th / 11th may simultaneously
    # increase the probability of unusual or sudden
    # encounters while increasing uncertainty.
    # -----------------------------------------------------

    unusual_connection_bonus = 0.0

    if rahu_house in (
        5,
        7,
        11,
    ):
        unusual_connection_bonus = 0.10

    meeting_score = (
        support_score
        + unusual_connection_bonus
        - challenge_score * 0.30
    )

    return {
        "score": round(
            _clamp(
                meeting_score
            ),
            3,
        ),

        "support_score": round(
            _clamp(
                support_score
            ),
            3,
        ),

        "challenge_score": round(
            _clamp(
                challenge_score
            ),
            3,
        ),

        "unusual_connection_bonus": round(
            unusual_connection_bonus,
            3,
        ),

        "houses": {
            "Venus": venus_house,
            "Jupiter": jupiter_house,
            "Moon": moon_house,
            "Mercury": mercury_house,
            "Saturn": saturn_house,
            "Rahu": rahu_house,
            "Ketu": ketu_house,
            "Mars": mars_house,
        },

        "components": {
            "venus_support": round(
                venus_support,
                3,
            ),

            "jupiter_support": round(
                jupiter_support,
                3,
            ),

            "moon_support": round(
                moon_support,
                3,
            ),

            "mercury_support": round(
                mercury_support,
                3,
            ),
        },
    }


# =========================================================
# SINGLE SNAPSHOT
# =========================================================

def score_spouse_meeting_moment(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:

    if not isinstance(
        chart,
        dict,
    ):
        raise ValueError(
            "chart must be a dictionary."
        )

    if not isinstance(
        moment,
        datetime,
    ):
        raise ValueError(
            "moment must be a datetime."
        )

    _require_timezone(
        moment,
        "moment",
    )

    period = (
        _find_dasha_period(
            chart,
            moment,
        )
    )

    dasha = (
        _score_dasha_for_spouse_meeting(
            period
        )
    )

    transits = (
        calculate_transits(
            moment
        )
    )

    mapped = (
        map_transits_to_natal_houses(
            chart,
            transits,
        )
    )

    transit = (
        _score_transits_for_spouse_meeting(
            mapped
        )
    )

    dasha_score = _safe_float(
        dasha.get(
            "score"
        )
    )

    transit_score = _safe_float(
        transit.get(
            "score"
        )
    )

    challenge = _safe_float(
        transit.get(
            "challenge_score"
        )
    )

    # Meeting timing should be more transit-sensitive than
    # marriage completion timing because actual encounters
    # can be triggered by shorter-term social movement.

    combined_score = (
        dasha_score * 0.42
        + transit_score * 0.58
    )

    combined_score -= (
        challenge * 0.08
    )

    combined_score = (
        _clamp(
            combined_score
        )
    )

    if combined_score >= 0.72:

        confirmation = (
            "strong_meeting_signal"
        )

    elif combined_score >= 0.60:

        confirmation = (
            "meeting_supported"
        )

    elif combined_score >= 0.50:

        confirmation = (
            "possible_meeting_window"
        )

    else:

        confirmation = (
            "weak_meeting_signal"
        )

    return {
        "moment": (
            moment.isoformat()
        ),

        "period": (
            dasha.get(
                "period"
            )
        ),

        "dasha_score": round(
            dasha_score,
            3,
        ),

        "transit_score": round(
            transit_score,
            3,
        ),

        "challenge_score": round(
            challenge,
            3,
        ),

        "combined_score": round(
            combined_score,
            3,
        ),

        "confirmation": (
            confirmation
        ),

        "dasha": (
            dasha
        ),

        "transit": (
            transit
        ),
    }


# =========================================================
# SCORE CLASSIFICATION
# =========================================================

def _classify_score(
    score: float,
) -> str:

    if score >= 0.78:
        return "very_strong"

    if score >= 0.68:
        return "strong"

    if score >= 0.58:
        return "moderate"

    if score >= 0.50:
        return "supportive"

    return "weak"


# =========================================================
# WINDOW BUILDING
# =========================================================

def _build_windows(
    snapshots: list[dict[str, Any]],
    step_days: int,
) -> list[dict[str, Any]]:

    candidates = [
        snapshot
        for snapshot in snapshots
        if _safe_float(
            snapshot.get(
                "combined_score"
            )
        )
        >= 0.52
    ]

    if not candidates:
        return []

    groups = [
        [
            candidates[
                0
            ]
        ]
    ]

    max_gap = (
        step_days
        * 2
    )

    for snapshot in candidates[
        1:
    ]:

        previous = (
            groups[
                -1
            ][
                -1
            ]
        )

        previous_date = (
            datetime.fromisoformat(
                str(
                    previous[
                        "moment"
                    ]
                )
            )
        )

        current_date = (
            datetime.fromisoformat(
                str(
                    snapshot[
                        "moment"
                    ]
                )
            )
        )

        gap_days = (
            current_date
            - previous_date
        ).days

        if gap_days <= max_gap:

            groups[
                -1
            ].append(
                snapshot
            )

        else:

            groups.append(
                [
                    snapshot
                ]
            )

    windows = []

    for group in groups:

        peak = max(
            group,
            key=lambda item: (
                _safe_float(
                    item.get(
                        "combined_score"
                    )
                )
            ),
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

        last_dt = (
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
            last_dt
            + timedelta(
                days=step_days,
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
                    "spouse_meeting"
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
                    average_transit,
                    3,
                ),

                "average_challenge_score": round(
                    average_challenge,
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
                                "combined_score"
                            )
                        ),
                        3,
                    ),

                    "strength": (
                        _classify_score(
                            _safe_float(
                                peak.get(
                                    "combined_score"
                                )
                            )
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

                    "challenge_score": (
                        peak.get(
                            "challenge_score"
                        )
                    ),

                    "houses": (
                        _safe_dict(
                            peak.get(
                                "transit"
                            )
                        ).get(
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
            _safe_float(
                item.get(
                    "average_transit_score"
                )
            ),
        ),
        reverse=True,
    )

    return windows


# =========================================================
# MAIN FORECAST
# =========================================================

def scan_spouse_meeting_forecast_v1(
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

    moment = start

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
        _build_windows(
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

    if peak_score >= 0.75:

        confidence = 0.90

    elif peak_score >= 0.65:

        confidence = 0.82

    elif peak_score >= 0.55:

        confidence = 0.70

    else:

        confidence = 0.58

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
