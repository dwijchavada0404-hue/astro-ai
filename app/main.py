from fastapi import FastAPI, HTTPException

from app.models.chart import BirthInput, BirthChart
from app.services.chart_service import build_chart
from app.services.prediction_service import generate_predictions

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


app = FastAPI(
    title="Astro AI - Milestone 1",
    version="0.2.1",
    description=(
        "Vedic astrology birth-chart calculation and "
        "marriage prediction API."
    ),
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "astro-ai-milestone1",
        "version": "0.2.1",
    }


@app.post(
    "/api/v1/chart",
    response_model=BirthChart,
)
def create_chart(payload: BirthInput):
    """
    Generate the complete Vedic birth chart.
    """

    try:
        return build_chart(payload)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chart calculation failed: {exc}",
        ) from exc


@app.post("/api/v1/predictions")
def create_predictions(payload: BirthInput):
    """
    Generate astrology predictions from the calculated chart.
    """

    try:
        chart = build_chart(payload)

        predictions = generate_predictions(chart)

        return {
            "birth": chart.get("birth", {}),
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
            detail=f"Prediction generation failed: {exc}",
        ) from exc


@app.post("/api/v1/marriage")
def create_marriage_analysis(payload: BirthInput):
    """
    Generate the complete marriage-analysis package.

    Includes:
    - birth chart
    - marriage predictions
    - 7th-house reasoning
    - marriage planetary analysis
    - marriage synthesis
    - current Dasha marriage analysis
    - ranked marriage timing periods
    - marriage timing synthesis
    """

    try:
        # -------------------------------------------------
        # Build birth chart
        # -------------------------------------------------

        chart = build_chart(payload)

        # -------------------------------------------------
        # General marriage predictions
        # -------------------------------------------------

        predictions = generate_predictions(chart)

        marriage_predictions = [
            prediction
            for prediction in predictions
            if prediction.get("feature") == "marriage"
        ]

        # -------------------------------------------------
        # 7th-house reasoning
        # -------------------------------------------------

        seventh_house_analysis = analyze_seventh_house(
            chart
        )

        # -------------------------------------------------
        # Marriage planetary analysis
        # -------------------------------------------------

        marriage_planet_analysis = analyze_marriage_planets(
            chart
        )

        # -------------------------------------------------
        # Overall marriage synthesis
        # -------------------------------------------------

        marriage_synthesis = synthesize_marriage(
            seventh_house_analysis,
            marriage_planet_analysis,
        )

        # -------------------------------------------------
        # Current Dasha marriage reasoning
        # -------------------------------------------------

        current_dasha = analyze_current_dasha_for_marriage(
            chart
        )

        # -------------------------------------------------
        # Rank all marriage timing periods
        # -------------------------------------------------

        marriage_timing = analyze_marriage_timing(
            chart
        )

        # -------------------------------------------------
        # Timing synthesis
        # -------------------------------------------------

        timing_synthesis = synthesize_marriage_timing(
            marriage_timing,
            current_dasha,
        )

        # -------------------------------------------------
        # Final API response
        # -------------------------------------------------

        return {
            "birth": chart.get("birth", {}),
            "ascendant": chart.get("ascendant", {}),
            "marriage": {
                "predictions": marriage_predictions,
                "seventh_house_analysis": seventh_house_analysis,
                "planetary_analysis": marriage_planet_analysis,
                "synthesis": marriage_synthesis,
                "current_dasha": current_dasha,
                "timing": {
                    "seventh_lord": marriage_timing.get(
                        "seventh_lord"
                    ),
                    "total_periods": marriage_timing.get(
                        "total_periods"
                    ),
                    "top_periods": marriage_timing.get(
                        "top_periods",
                        [],
                    ),
                    "synthesis": timing_synthesis,
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
            detail=f"Marriage analysis failed: {exc}",
        ) from exc