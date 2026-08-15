from fastapi import FastAPI, HTTPException

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


app = FastAPI(
    title="Astro AI - Milestone 1",
    version="0.5.0",
    description=(
        "Vedic astrology birth-chart calculation, "
        "marriage analysis and career analysis API."
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

        predictions = generate_predictions(
            chart
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

        # -------------------------------------------------
        # BUILD CHART
        # -------------------------------------------------

        chart = build_chart(
            payload
        )

        # -------------------------------------------------
        # CORE CAREER REASONING
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CURRENT DASHA
        # -------------------------------------------------

        current_dasha = (
            analyze_current_dasha_for_career(
                chart
            )
        )

        # -------------------------------------------------
        # GENERAL CAREER TIMING
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CAREER NARRATIVE
        # -------------------------------------------------

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

        # -------------------------------------------------
        # NATAL CAREER EVENTS
        # -------------------------------------------------

        career_events = (
            analyze_career_events(
                chart
            )
        )

        # -------------------------------------------------
        # CAREER EVENT TIMING
        # -------------------------------------------------

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

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

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