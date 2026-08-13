from typing import Any

from fastapi import FastAPI, HTTPException

from app.models.chart import BirthChart, BirthInput
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
from app.astrology.features.marriage_narrative import (
    generate_marriage_narrative,
)


app = FastAPI(
    title="Astro AI",
    version="0.4.0",
    description=(
        "Vedic astrology birth-chart calculation, "
        "prediction and marriage-analysis API."
    ),
)


def _build_marriage_package(
    payload: BirthInput,
) -> dict[str, Any]:
    """
    Build the complete internal marriage-analysis package.

    This helper is shared by:
    - /api/v1/marriage
    - /api/v1/marriage-reading

    It prevents duplicate calculation logic across endpoints.
    """

    # -------------------------------------------------
    # Birth chart
    # -------------------------------------------------

    chart = build_chart(payload)

    # -------------------------------------------------
    # General prediction engine
    # -------------------------------------------------

    predictions = generate_predictions(chart)

    marriage_predictions = [
        prediction
        for prediction in predictions
        if prediction.get("feature") == "marriage"
    ]

    # -------------------------------------------------
    # 7th-house analysis
    # -------------------------------------------------

    seventh_house_analysis = analyze_seventh_house(
        chart
    )

    # -------------------------------------------------
    # Marriage planetary analysis
    # -------------------------------------------------

    marriage_planet_analysis = (
        analyze_marriage_planets(
            chart
        )
    )

    # -------------------------------------------------
    # Natal marriage synthesis
    # -------------------------------------------------

    marriage_synthesis = synthesize_marriage(
        seventh_house_analysis,
        marriage_planet_analysis,
    )

    # -------------------------------------------------
    # Current Vimshottari Dasha
    # -------------------------------------------------

    current_dasha = (
        analyze_current_dasha_for_marriage(
            chart
        )
    )

    # -------------------------------------------------
    # Marriage timing
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
    # User-facing narrative
    # -------------------------------------------------

    reading = generate_marriage_narrative(
        seventh_house_analysis,
        marriage_planet_analysis,
        marriage_synthesis,
        marriage_timing,
        current_dasha,
        timing_synthesis,
    )

    return {
        "chart": chart,
        "marriage_predictions": marriage_predictions,
        "seventh_house_analysis": seventh_house_analysis,
        "marriage_planet_analysis": marriage_planet_analysis,
        "marriage_synthesis": marriage_synthesis,
        "current_dasha": current_dasha,
        "marriage_timing": marriage_timing,
        "timing_synthesis": timing_synthesis,
        "reading": reading,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "astro-ai",
        "version": "0.4.0",
    }


@app.post(
    "/api/v1/chart",
    response_model=BirthChart,
)
def create_chart(
    payload: BirthInput,
):
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
            detail=(
                f"Chart calculation failed: {exc}"
            ),
        ) from exc


@app.post("/api/v1/predictions")
def create_predictions(
    payload: BirthInput,
):
    """
    Generate astrology predictions from the chart.
    """

    try:
        chart = build_chart(payload)

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
                "Prediction generation failed: "
                f"{exc}"
            ),
        ) from exc


@app.post("/api/v1/marriage")
def create_marriage_analysis(
    payload: BirthInput,
):
    """
    Generate the complete technical marriage-analysis package.

    Intended for:
    - debugging
    - internal evidence inspection
    - developer use
    """

    try:
        result = _build_marriage_package(
            payload
        )

        chart = result["chart"]
        marriage_timing = result[
            "marriage_timing"
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
                "reading": result[
                    "reading"
                ],
                "predictions": result[
                    "marriage_predictions"
                ],
                "seventh_house_analysis": result[
                    "seventh_house_analysis"
                ],
                "planetary_analysis": result[
                    "marriage_planet_analysis"
                ],
                "synthesis": result[
                    "marriage_synthesis"
                ],
                "current_dasha": result[
                    "current_dasha"
                ],
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
                    "synthesis": result[
                        "timing_synthesis"
                    ],
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
                "Marriage analysis failed: "
                f"{exc}"
            ),
        ) from exc


@app.post("/api/v1/marriage-reading")
def create_marriage_reading(
    payload: BirthInput,
):
    """
    Generate the user-facing AstroAI marriage reading.

    Unlike /api/v1/marriage, this endpoint intentionally
    excludes large technical evidence objects.
    """

    try:
        result = _build_marriage_package(
            payload
        )

        chart = result["chart"]
        reading = result["reading"]

        return {
            "birth": {
                "date": chart.get(
                    "birth",
                    {},
                ).get("date"),
                "time": chart.get(
                    "birth",
                    {},
                ).get("time"),
                "place": chart.get(
                    "birth",
                    {},
                ).get(
                    "resolved_place"
                ),
            },
            "reading": reading,
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
                "Marriage reading generation "
                f"failed: {exc}"
            ),
        ) from exc