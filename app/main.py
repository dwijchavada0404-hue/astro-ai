from copy import deepcopy
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.models.chart import BirthInput, BirthChart
from app.services.chart_service import build_chart
from app.services.prediction_service import generate_predictions

# ---------------------------------------------------------
# MARRIAGE MODULES
# ---------------------------------------------------------

from app.astrology.features.marriage_reasoning import (
    analyze_seventh_house,
)
from app.astrology.features.marriage_planets import (
    analyze_marriage_planets,
)
from app.astrology.features.marriage_synthesis import (
    synthesize_marriage,
)
from app.astrology.features.dasha_marriage_reasoning import (
    analyze_current_dasha_for_marriage,
)
from app.astrology.features.marriage_timing import (
    analyze_marriage_timing,
)
from app.astrology.features.marriage_timing_synthesis import (
    synthesize_marriage_timing,
)
from app.astrology.features.marriage_narrative import (
    generate_marriage_narrative,
)

# ---------------------------------------------------------
# CAREER MODULES
# ---------------------------------------------------------

from app.astrology.features.career_reasoning import (
    analyze_tenth_house,
)
from app.astrology.features.career_interpretation import (
    interpret_career,
)
from app.astrology.features.career_planets import (
    analyze_career_planets,
)
from app.astrology.features.career_synthesis import (
    synthesize_career,
)
from app.astrology.features.dasha_career_reasoning import (
    analyze_current_dasha_for_career,
)
from app.astrology.features.career_timing import (
    analyze_career_timing,
)
from app.astrology.features.career_timing_synthesis import (
    synthesize_career_timing,
)
from app.astrology.features.career_narrative import (
    generate_career_narrative,
)

# ---------------------------------------------------------
# CAREER EVENT MODULES
# ---------------------------------------------------------

from app.astrology.features.career_events import (
    analyze_career_events,
)
from app.astrology.features.career_event_timing import (
    analyze_career_event_timing,
)
from app.astrology.features.career_event_timing_synthesis import (
    synthesize_career_event_timing,
)

# ---------------------------------------------------------
# TRANSIT MODULES
# ---------------------------------------------------------

from app.astrology.transits import (
    calculate_transits,
)
from app.astrology.features.transit_house_mapping import (
    map_transits_to_natal_houses,
)
from app.astrology.features.career_transits import (
    analyze_career_transits,
)
from app.astrology.features.career_dasha_transit_synthesis import (
    synthesize_career_dasha_transits,
)


# =========================================================
# API REQUEST MODELS
# =========================================================

class CareerTransitRequest(BaseModel):
    """
    Request body for career transit analysis.

    Birth details are kept separate from the transit
    moment so we can analyse any requested date without
    changing the natal chart.
    """

    birth: BirthInput
    transit_moment: datetime


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Astro AI - Milestone 1",
    version="0.5.0",
    description=(
        "Vedic astrology birth-chart calculation, "
        "marriage analysis, career analysis and "
        "Dasha-transit career timing API."
    ),
)


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "astro-ai",
        "version": "0.5.0",
    }


# =========================================================
# INTERNAL DASHA HELPERS
# =========================================================

def _find_dasha_period_for_moment(
    dashas: dict[str, Any],
    moment: datetime,
) -> dict[str, Any] | None:
    """
    Find the Vimshottari Mahadasha/Antardasha containing
    an explicitly requested transit moment.

    We do this here so transit analysis uses the Dasha
    active on the transit date instead of relying on the
    chart's system-current period.
    """

    if moment.tzinfo is None:
        raise ValueError(
            "transit_moment must include a timezone offset."
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

            ad_start = (
                datetime.fromisoformat(
                    ad_start_raw
                )
            )

            ad_end = (
                datetime.fromisoformat(
                    ad_end_raw
                )
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

    return None


def _chart_for_requested_moment(
    chart: dict[str, Any],
    moment: datetime,
) -> dict[str, Any]:
    """
    Return a copy of the natal chart whose
    dashas.current_period corresponds to the requested
    transit date.

    The natal chart itself is never mutated.
    """

    chart_copy = deepcopy(
        chart
    )

    dashas = chart_copy.get(
        "dashas"
    )

    if not isinstance(
        dashas,
        dict,
    ):
        raise ValueError(
            "Dasha data is unavailable in the birth chart."
        )

    requested_period = (
        _find_dasha_period_for_moment(
            dashas,
            moment,
        )
    )

    if requested_period is None:
        raise ValueError(
            "No Vimshottari Dasha period was found "
            "for the requested transit moment."
        )

    dashas[
        "current_period"
    ] = requested_period

    return chart_copy


# =========================================================
# BIRTH CHART
# =========================================================

@app.post(
    "/api/v1/chart",
    response_model=BirthChart,
)
def create_chart(
    payload: BirthInput,
):
    try:
        return build_chart(
            payload
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Chart calculation failed: {exc}"
            ),
        ) from exc


# =========================================================
# GENERAL PREDICTIONS
# =========================================================

@app.post("/api/v1/predictions")
def create_predictions(
    payload: BirthInput,
):
    try:
        chart = build_chart(
            payload
        )

        predictions = (
            generate_predictions(
                chart
            )
        )

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "predictions": predictions,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Prediction generation failed: {exc}"
            ),
        ) from exc


# =========================================================
# SHARED MARRIAGE PIPELINE
# =========================================================

def _build_marriage_package(
    payload: BirthInput,
) -> dict:

    chart = build_chart(
        payload
    )

    predictions = generate_predictions(
        chart
    )

    marriage_predictions = [
        prediction
        for prediction in predictions
        if prediction.get(
            "feature"
        ) == "marriage"
    ]

    seventh_house_analysis = (
        analyze_seventh_house(
            chart
        )
    )

    marriage_planet_analysis = (
        analyze_marriage_planets(
            chart
        )
    )

    marriage_synthesis = (
        synthesize_marriage(
            seventh_house_analysis,
            marriage_planet_analysis,
        )
    )

    current_dasha = (
        analyze_current_dasha_for_marriage(
            chart
        )
    )

    marriage_timing = (
        analyze_marriage_timing(
            chart
        )
    )

    timing_synthesis = (
        synthesize_marriage_timing(
            marriage_timing,
            current_dasha,
        )
    )

    reading = (
        generate_marriage_narrative(
            seventh_house_analysis,
            marriage_planet_analysis,
            marriage_synthesis,
            marriage_timing,
            current_dasha,
            timing_synthesis,
        )
    )

    return {
        "chart": chart,
        "reading": reading,
        "predictions": (
            marriage_predictions
        ),
        "seventh_house_analysis": (
            seventh_house_analysis
        ),
        "planetary_analysis": (
            marriage_planet_analysis
        ),
        "synthesis": (
            marriage_synthesis
        ),
        "current_dasha": (
            current_dasha
        ),
        "timing": (
            marriage_timing
        ),
        "timing_synthesis": (
            timing_synthesis
        ),
    }


# =========================================================
# MARRIAGE ANALYSIS
# =========================================================

@app.post("/api/v1/marriage")
def create_marriage_analysis(
    payload: BirthInput,
):
    try:

        result = (
            _build_marriage_package(
                payload
            )
        )

        chart = result[
            "chart"
        ]

        marriage_timing = result[
            "timing"
        ]

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "ascendant": chart.get(
                "ascendant",
                {},
            ),
            "marriage": {
                "reading": (
                    result["reading"]
                ),
                "predictions": (
                    result["predictions"]
                ),
                "seventh_house_analysis": (
                    result[
                        "seventh_house_analysis"
                    ]
                ),
                "planetary_analysis": (
                    result[
                        "planetary_analysis"
                    ]
                ),
                "synthesis": (
                    result[
                        "synthesis"
                    ]
                ),
                "current_dasha": (
                    result[
                        "current_dasha"
                    ]
                ),
                "timing": {
                    "seventh_lord": (
                        marriage_timing.get(
                            "seventh_lord"
                        )
                    ),
                    "total_periods": (
                        marriage_timing.get(
                            "total_periods"
                        )
                    ),
                    "top_periods": (
                        marriage_timing.get(
                            "top_periods",
                            [],
                        )
                    ),
                    "synthesis": (
                        result[
                            "timing_synthesis"
                        ]
                    ),
                },
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Marriage analysis failed: {exc}"
            ),
        ) from exc


# =========================================================
# MARRIAGE READING
# =========================================================

@app.post(
    "/api/v1/marriage-reading"
)
def create_marriage_reading(
    payload: BirthInput,
):
    try:

        result = (
            _build_marriage_package(
                payload
            )
        )

        chart = result[
            "chart"
        ]

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "reading": (
                result["reading"]
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Marriage reading failed: {exc}"
            ),
        ) from exc


# =========================================================
# CAREER ANALYSIS
# =========================================================

@app.post("/api/v1/career")
def create_career_analysis(
    payload: BirthInput,
):
    try:

        chart = build_chart(
            payload
        )

        career_reasoning = (
            analyze_tenth_house(
                chart
            )
        )

        career_interpretation = (
            interpret_career(
                career_reasoning
            )
        )

        career_planet_analysis = (
            analyze_career_planets(
                chart
            )
        )

        career_synthesis = (
            synthesize_career(
                career_reasoning,
                career_interpretation,
                career_planet_analysis,
            )
        )

        current_dasha = (
            analyze_current_dasha_for_career(
                chart
            )
        )

        career_timing = (
            analyze_career_timing(
                chart
            )
        )

        timing_synthesis = (
            synthesize_career_timing(
                career_timing,
                current_dasha,
            )
        )

        reading = (
            generate_career_narrative(
                career_reasoning,
                career_interpretation,
                career_planet_analysis,
                career_synthesis,
                current_dasha,
                career_timing,
                timing_synthesis,
            )
        )

        career_events = (
            analyze_career_events(
                chart
            )
        )

        career_event_timing = (
            analyze_career_event_timing(
                chart
            )
        )

        career_event_timing_synthesis = (
            synthesize_career_event_timing(
                career_event_timing,
                current_dasha,
            )
        )

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "ascendant": chart.get(
                "ascendant",
                {},
            ),
            "career": {
                "reading": (
                    reading
                ),
                "reasoning": (
                    career_reasoning
                ),
                "interpretation": (
                    career_interpretation
                ),
                "planetary_analysis": (
                    career_planet_analysis
                ),
                "synthesis": (
                    career_synthesis
                ),
                "current_dasha": (
                    current_dasha
                ),
                "timing": {
                    "tenth_lord": (
                        career_timing.get(
                            "tenth_lord"
                        )
                    ),
                    "total_periods": (
                        career_timing.get(
                            "total_periods"
                        )
                    ),
                    "top_periods": (
                        career_timing.get(
                            "top_periods",
                            [],
                        )
                    ),
                    "synthesis": (
                        timing_synthesis
                    ),
                },
                "events": {
                    "natal_analysis": (
                        career_events
                    ),
                    "timing": (
                        career_event_timing_synthesis
                    ),
                },
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Career analysis failed: {exc}"
            ),
        ) from exc


# =========================================================
# CAREER DASHA × TRANSIT ANALYSIS
# =========================================================

@app.post(
    "/api/v1/career-transits"
)
def create_career_transit_analysis(
    payload: CareerTransitRequest,
):
    """
    Analyse career events for an explicitly supplied
    transit moment.

    Pipeline:

        natal chart
            ->
        Dasha active on requested date
            ->
        career-event Dasha analysis
            ->
        Lahiri sidereal transits
            ->
        transit-to-natal-house mapping
            ->
        career transit reasoning
            ->
        Dasha × transit confirmation

    The endpoint does not rely on the system clock.
    """

    try:

        # -------------------------------------------------
        # NATAL CHART
        # -------------------------------------------------

        chart = build_chart(
            payload.birth
        )

        transit_moment = (
            payload.transit_moment
        )

        if (
            transit_moment.tzinfo
            is None
            or transit_moment.utcoffset()
            is None
        ):
            raise ValueError(
                "transit_moment must include "
                "a timezone offset."
            )

        # -------------------------------------------------
        # ALIGN DASHA WITH REQUESTED TRANSIT DATE
        # -------------------------------------------------

        dated_chart = (
            _chart_for_requested_moment(
                chart,
                transit_moment,
            )
        )

        current_dasha = (
            analyze_current_dasha_for_career(
                dated_chart
            )
        )

        # -------------------------------------------------
        # DASHA EVENT TIMING
        # -------------------------------------------------

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

        # -------------------------------------------------
        # TRANSIT CALCULATION
        # -------------------------------------------------

        transits = calculate_transits(
            transit_moment
        )

        mapped_transits = (
            map_transits_to_natal_houses(
                chart,
                transits,
            )
        )

        career_transits = (
            analyze_career_transits(
                mapped_transits
            )
        )

        # -------------------------------------------------
        # DASHA × TRANSIT SYNTHESIS
        # -------------------------------------------------

        confirmation = (
            synthesize_career_dasha_transits(
                event_timing_synthesis,
                career_transits,
            )
        )

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return {
            "birth": chart.get(
                "birth",
                {},
            ),

            "transit_moment": (
                transit_moment.isoformat()
            ),

            "current_dasha": (
                current_dasha
            ),

            "transits": {
                "positions": (
                    transits
                ),
                "natal_house_mapping": (
                    mapped_transits
                ),
                "career_reasoning": (
                    career_transits
                ),
            },

            "career_events": {
                "dasha_timing": (
                    event_timing_synthesis
                ),
                "dasha_transit_confirmation": (
                    confirmation
                ),
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Career transit analysis failed: "
                f"{exc}"
            ),
        ) from exc