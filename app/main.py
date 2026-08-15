from calendar import monthrange
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
# MARRIAGE QUESTION V2 MODULES
# ---------------------------------------------------------

from app.astrology.features.marriage_question_intelligence_v2 import (
    analyze_marriage_question_v2,
)

from app.astrology.features.marriage_forecast_router_v2 import (
    route_marriage_question_v2,
)


# ---------------------------------------------------------
# MARRIAGE QUESTION V3 MODULES
# ---------------------------------------------------------

from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)

from app.astrology.features.marriage_forecast_router_v3 import (
    route_marriage_question_v3,
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


# ---------------------------------------------------------
# CAREER FORECAST MODULES
# ---------------------------------------------------------

from app.astrology.features.career_forecast_scanner import (
    scan_career_forecast,
)

from app.astrology.features.career_forecast_windows import (
    build_career_forecast_windows,
)

from app.astrology.features.career_forecast_narrative import (
    generate_career_forecast_narrative,
)


# ---------------------------------------------------------
# CAREER QUESTION V2 MODULES
# ---------------------------------------------------------

from app.astrology.features.career_question_parser import (
    parse_career_question,
)

from app.astrology.features.career_answer_intelligence_v2 import (
    generate_career_question_answer_v2,
)


# ---------------------------------------------------------
# CAREER QUESTION V3 MODULES
# ---------------------------------------------------------

from app.astrology.features.career_question_intelligence_v3 import (
    analyze_career_question_v3,
)

from app.astrology.features.career_forecast_router_v3 import (
    route_career_question_v3,
)


# =========================================================
# API REQUEST MODELS
# =========================================================

class MarriageQuestionV2Request(BaseModel):
    """
    Natural-language Marriage Question V2 request.
    """

    birth: BirthInput
    question: str
    reference_moment: datetime


class MarriageQuestionV3Request(BaseModel):
    """
    Natural-language Marriage Question V3 request.

    previous_context is optional and is used for
    conversational follow-up questions.
    """

    birth: BirthInput
    question: str
    reference_moment: datetime
    previous_context: dict[str, Any] | None = None


class CareerTransitRequest(BaseModel):
    """
    Request body for career transit analysis.
    """

    birth: BirthInput
    transit_moment: datetime


class CareerForecastRequest(BaseModel):
    """
    Request body for career forecast analysis.
    """

    birth: BirthInput
    start: datetime
    end: datetime
    step_days: int = 7


class CareerQuestionRequest(BaseModel):
    """
    Natural-language Career Question V2 request.
    """

    birth: BirthInput
    question: str
    reference_moment: datetime


class CareerQuestionV3Request(BaseModel):
    """
    Natural-language Career Question V3 request.

    previous_context is optional and is used for
    conversational follow-up questions.
    """

    birth: BirthInput
    question: str
    reference_moment: datetime
    previous_context: dict[str, Any] | None = None


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Astro AI - Milestone 1",
    version="0.6.0",
    description=(
        "Vedic astrology birth-chart calculation, "
        "marriage analysis, marriage forecasting, "
        "natural-language marriage questions, "
        "career analysis, Dasha-transit career timing, "
        "career forecasting and natural-language "
        "career-question APIs."
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
        "version": "0.6.0",
    }


# =========================================================
# GENERIC HELPERS
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
# DATE RANGE HELPERS
# =========================================================

def _add_months(
    value: datetime,
    months: int,
) -> datetime:
    if months < 0:
        raise ValueError(
            "months must not be negative."
        )

    zero_based_month = (
        value.month
        - 1
        + months
    )

    year = (
        value.year
        + zero_based_month // 12
    )

    month = (
        zero_based_month
        % 12
    ) + 1

    final_day = min(
        value.day,
        monthrange(
            year,
            month,
        )[1],
    )

    return value.replace(
        year=year,
        month=month,
        day=final_day,
    )


def _build_question_date_range(
    parsed_question: dict[str, Any],
    reference_moment: datetime,
) -> tuple[
    datetime,
    datetime,
    int,
]:
    horizon = _safe_dict(
        parsed_question.get(
            "forecast_horizon"
        )
    )

    horizon_type = horizon.get(
        "type"
    )

    step_days = int(
        parsed_question.get(
            "recommended_step_days",
            7,
        )
    )

    if horizon_type == "months":
        months = int(
            horizon.get(
                "value",
                12,
            )
        )

        if months < 1:
            raise ValueError(
                "Forecast month horizon must be at least 1."
            )

        start = reference_moment

        end = _add_months(
            reference_moment,
            months,
        )

        return (
            start,
            end,
            step_days,
        )

    if horizon_type == "years":
        years = int(
            horizon.get(
                "value",
                1,
            )
        )

        if years < 1:
            raise ValueError(
                "Forecast year horizon must be at least 1."
            )

        start = reference_moment

        end = _add_months(
            reference_moment,
            years * 12,
        )

        return (
            start,
            end,
            step_days,
        )

    if horizon_type == "calendar_year":
        year = int(
            horizon.get(
                "year"
            )
        )

        tzinfo = reference_moment.tzinfo

        start = datetime(
            year,
            1,
            1,
            tzinfo=tzinfo,
        )

        end = datetime(
            year + 1,
            1,
            1,
            tzinfo=tzinfo,
        )

        return (
            start,
            end,
            step_days,
        )

    raise ValueError(
        "Unsupported career-question forecast horizon."
    )


# =========================================================
# INTERNAL DASHA HELPERS
# =========================================================

def _find_dasha_period_for_moment(
    dashas: dict[str, Any],
    moment: datetime,
) -> dict[str, Any] | None:
    _require_timezone(
        moment,
        "transit_moment",
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
                    "mahadasha": md.get(
                        "planet"
                    ),
                    "mahadasha_start": (
                        md_start_raw
                    ),
                    "mahadasha_end": (
                        md_end_raw
                    ),
                    "antardasha": ad.get(
                        "planet"
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
# CAREER QUESTION EVENT HELPER
# =========================================================

def _question_event_data(
    forecast: dict[str, Any],
    event_name: str,
) -> dict[str, Any]:
    events = _safe_dict(
        forecast.get(
            "events"
        )
    )

    return _safe_dict(
        events.get(
            event_name
        )
    )


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

@app.post(
    "/api/v1/predictions"
)
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
        )
        == "marriage"
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

@app.post(
    "/api/v1/marriage"
)
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
                "reading": result[
                    "reading"
                ],
                "predictions": result[
                    "predictions"
                ],
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
                "synthesis": result[
                    "synthesis"
                ],
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
            "reading": result[
                "reading"
            ],
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
# NATURAL-LANGUAGE MARRIAGE QUESTION V2
# =========================================================

@app.post(
    "/api/v1/marriage-question-v2"
)
def answer_marriage_question_v2(
    payload: MarriageQuestionV2Request,
):
    """
    Natural-language Marriage Question Intelligence V2.
    """

    try:
        reference_moment = (
            payload.reference_moment
        )

        _require_timezone(
            reference_moment,
            "reference_moment",
        )

        question = (
            payload.question.strip()
        )

        if not question:
            raise ValueError(
                "question must not be empty."
            )

        chart = build_chart(
            payload.birth
        )

        question_analysis = (
            analyze_marriage_question_v2(
                question
            )
        )

        route_result = (
            route_marriage_question_v2(
                chart,
                question_analysis,
                reference_moment,
            )
        )

        conversation_context = {
            "question_analysis": (
                question_analysis
            ),
            "route_result": (
                route_result
            ),
        }

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "question": (
                question
            ),
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "understanding": (
                question_analysis
            ),
            "result": (
                route_result
            ),
            "conversation_context": (
                conversation_context
            ),
            "disclaimer": (
                "Astrological forecasts describe symbolic "
                "patterns and periods of stronger or weaker "
                "relationship support. The results should "
                "not be treated as guaranteed predictions "
                "of marriage, relationship formation, "
                "separation or other personal outcomes."
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(
                exc
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Marriage Question V2 analysis failed: "
                f"{exc}"
            ),
        ) from exc


# =========================================================
# NATURAL-LANGUAGE MARRIAGE QUESTION V3
# =========================================================

@app.post(
    "/api/v1/marriage-question-v3"
)
def answer_marriage_question_v3(
    payload: MarriageQuestionV3Request,
):
    """
    Marriage Question Intelligence V3.

    Supported routes currently include:

        single-event marriage timing
        relationship commitment / challenge
        spouse-meeting timing proxy
        calendar-year comparisons
        conversational follow-ups

    Other specialist marriage events may be parsed
    correctly but remain intentionally unsupported until
    dedicated evidence engines are implemented.
    """

    try:
        reference_moment = (
            payload.reference_moment
        )

        _require_timezone(
            reference_moment,
            "reference_moment",
        )

        question = (
            payload.question.strip()
        )

        if not question:
            raise ValueError(
                "question must not be empty."
            )

        # ---------------------------------------------
        # BUILD NATAL CHART
        # ---------------------------------------------

        chart = build_chart(
            payload.birth
        )

        # ---------------------------------------------
        # QUESTION INTELLIGENCE V3
        # ---------------------------------------------

        question_analysis = (
            analyze_marriage_question_v3(
                question
            )
        )

        # ---------------------------------------------
        # ROUTE QUESTION
        # ---------------------------------------------

        route_result = (
            route_marriage_question_v3(
                chart,
                question_analysis,
                reference_moment,
                previous_context=(
                    payload.previous_context
                ),
            )
        )

        # ---------------------------------------------
        # SAVE CONTEXT FOR NEXT FOLLOW-UP
        # ---------------------------------------------

        conversation_context = {
            "question_analysis": (
                question_analysis
            ),
            "route_result": (
                route_result
            ),
        }

        return {
            "birth": chart.get(
                "birth",
                {},
            ),

            "question": (
                question
            ),

            "reference_moment": (
                reference_moment.isoformat()
            ),

            "understanding": (
                question_analysis
            ),

            "result": (
                route_result
            ),

            "conversation_context": (
                conversation_context
            ),

            "disclaimer": (
                "Astrological forecasts describe symbolic "
                "patterns and periods of stronger or weaker "
                "relationship support. The results should "
                "not be treated as guaranteed predictions "
                "of marriage, spouse meeting, relationship "
                "formation, separation or other personal "
                "outcomes."
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(
                exc
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Marriage Question V3 analysis failed: "
                f"{exc}"
            ),
        ) from exc


# =========================================================
# CAREER ANALYSIS
# =========================================================

@app.post(
    "/api/v1/career"
)
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
                "reading": reading,
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
# CAREER TRANSIT ANALYSIS
# =========================================================

@app.post(
    "/api/v1/career-transits"
)
def create_career_transit_analysis(
    payload: CareerTransitRequest,
):
    try:
        chart = build_chart(
            payload.birth
        )

        transit_moment = (
            payload.transit_moment
        )

        _require_timezone(
            transit_moment,
            "transit_moment",
        )

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

        confirmation = (
            synthesize_career_dasha_transits(
                event_timing_synthesis,
                career_transits,
            )
        )

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
                "positions": transits,
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


# =========================================================
# CAREER FORECAST
# =========================================================

@app.post(
    "/api/v1/career-forecast"
)
def create_career_forecast(
    payload: CareerForecastRequest,
):
    try:
        start = payload.start
        end = payload.end
        step_days = payload.step_days

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

        forecast_span_days = (
            end - start
        ).days

        if forecast_span_days > 3650:
            raise ValueError(
                "Career forecast range must not exceed "
                "10 years."
            )

        chart = build_chart(
            payload.birth
        )

        scan = scan_career_forecast(
            chart,
            start,
            end,
            step_days=step_days,
        )

        windows = (
            build_career_forecast_windows(
                scan
            )
        )

        forecast = (
            generate_career_forecast_narrative(
                windows
            )
        )

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "request": {
                "start": (
                    start.isoformat()
                ),
                "end": (
                    end.isoformat()
                ),
                "step_days": step_days,
            },
            "forecast": forecast,
            "windows": windows,
            "scan_metadata": {
                "available": scan.get(
                    "available"
                ),
                "start": scan.get(
                    "start"
                ),
                "end": scan.get(
                    "end"
                ),
                "step_days": scan.get(
                    "step_days"
                ),
                "snapshot_count": scan.get(
                    "snapshot_count"
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
                "Career forecast generation failed: "
                f"{exc}"
            ),
        ) from exc


# =========================================================
# NATURAL-LANGUAGE CAREER QUESTION V2
# =========================================================

@app.post(
    "/api/v1/career-question"
)
def answer_career_question(
    payload: CareerQuestionRequest,
):
    try:
        reference_moment = (
            payload.reference_moment
        )

        _require_timezone(
            reference_moment,
            "reference_moment",
        )

        parsed_question = (
            parse_career_question(
                payload.question
            )
        )

        (
            start,
            end,
            step_days,
        ) = _build_question_date_range(
            parsed_question,
            reference_moment,
        )

        if end <= start:
            raise ValueError(
                "Resolved career-question forecast "
                "end must be later than start."
            )

        if step_days < 1:
            raise ValueError(
                "Resolved career-question step_days "
                "must be at least 1."
            )

        if step_days > 31:
            raise ValueError(
                "Resolved career-question step_days "
                "must not exceed 31."
            )

        forecast_span_days = (
            end - start
        ).days

        if forecast_span_days > 3650:
            raise ValueError(
                "Resolved career-question forecast range "
                "must not exceed 10 years."
            )

        chart = build_chart(
            payload.birth
        )

        scan = scan_career_forecast(
            chart,
            start,
            end,
            step_days=step_days,
        )

        windows = (
            build_career_forecast_windows(
                scan
            )
        )

        forecast = (
            generate_career_forecast_narrative(
                windows
            )
        )

        answer = (
            generate_career_question_answer_v2(
                parsed_question,
                forecast,
            )
        )

        intent = _safe_dict(
            parsed_question.get(
                "intent"
            )
        )

        target_event = str(
            intent.get(
                "event",
                "general_career",
            )
        )

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "question": (
                payload.question
            ),
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "understanding": (
                parsed_question
            ),
            "resolved_forecast_request": {
                "start": (
                    start.isoformat()
                ),
                "end": (
                    end.isoformat()
                ),
                "step_days": step_days,
            },
            "answer": answer,
            "forecast_context": {
                "overall": (
                    forecast.get(
                        "overall"
                    )
                ),
                "target_event": (
                    _question_event_data(
                        forecast,
                        target_event,
                    )
                ),
            },
            "scan_metadata": {
                "available": scan.get(
                    "available"
                ),
                "start": scan.get(
                    "start"
                ),
                "end": scan.get(
                    "end"
                ),
                "step_days": scan.get(
                    "step_days"
                ),
                "snapshot_count": scan.get(
                    "snapshot_count"
                ),
            },
            "disclaimer": (
                "Astrological forecasts describe symbolic "
                "patterns and periods of stronger or weaker "
                "support. They should not be treated as "
                "guaranteed predictions of employment, "
                "promotion, income, relocation or other "
                "professional outcomes."
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
                "Career question analysis failed: "
                f"{exc}"
            ),
        ) from exc


# =========================================================
# NATURAL-LANGUAGE CAREER QUESTION V3
# =========================================================

@app.post(
    "/api/v1/career-question-v3"
)
def answer_career_question_v3(
    payload: CareerQuestionV3Request,
):
    """
    Career Question Intelligence V3.

    Supported modes:

        single_event
        comparison
        multi_event
        risk
        follow_up
    """

    try:
        reference_moment = (
            payload.reference_moment
        )

        _require_timezone(
            reference_moment,
            "reference_moment",
        )

        question = (
            payload.question.strip()
        )

        if not question:
            raise ValueError(
                "question must not be empty."
            )

        chart = build_chart(
            payload.birth
        )

        question_analysis = (
            analyze_career_question_v3(
                question
            )
        )

        route_result = (
            route_career_question_v3(
                chart,
                question_analysis,
                reference_moment,
                previous_context=(
                    payload.previous_context
                ),
            )
        )

        conversation_context = {
            "question_analysis": (
                question_analysis
            ),
            "route_result": (
                route_result
            ),
        }

        return {
            "birth": chart.get(
                "birth",
                {},
            ),
            "question": (
                question
            ),
            "reference_moment": (
                reference_moment.isoformat()
            ),
            "understanding": (
                question_analysis
            ),
            "result": (
                route_result
            ),
            "conversation_context": (
                conversation_context
            ),
            "disclaimer": (
                "Astrological forecasts describe symbolic "
                "patterns and periods of stronger or weaker "
                "support. The results should not be treated "
                "as guaranteed predictions of employment, "
                "promotion, termination, income, relocation "
                "or other professional outcomes."
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
                "Career Question V3 analysis failed: "
                f"{exc}"
            ),
        ) from exc
