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
# CAREER QUESTION MODULE
# ---------------------------------------------------------

from app.astrology.features.career_question_parser import (
    parse_career_question,
)


# =========================================================
# API REQUEST MODELS
# =========================================================

class CareerTransitRequest(BaseModel):
    """
    Request body for career transit analysis.
    """

    birth: BirthInput
    transit_moment: datetime


class CareerForecastRequest(BaseModel):
    """
    Request body for a career forecast across
    an explicitly supplied date range.
    """

    birth: BirthInput
    start: datetime
    end: datetime
    step_days: int = 7


class CareerQuestionRequest(BaseModel):
    """
    Natural-language career question.

    reference_moment establishes what "now",
    "next 6 months", "next year", etc. mean.

    Example:

        {
            "birth": {...},
            "question":
                "Will I change my job in the next 6 months?",
            "reference_moment":
                "2026-08-15T12:00:00+05:30"
        }
    """

    birth: BirthInput
    question: str
    reference_moment: datetime


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Astro AI - Milestone 1",
    version="0.6.0",
    description=(
        "Vedic astrology birth-chart calculation, "
        "marriage analysis, career analysis, "
        "Dasha-transit career timing, "
        "career forecasting and natural-language "
        "career-question API."
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
    """
    Ensure an API datetime includes an explicit
    timezone or UTC offset.
    """

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
    """
    Add calendar months without requiring an
    additional external dependency.

    Example:

        2026-08-31 + 1 month
            ->
        2026-09-30
    """

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
        + (
            zero_based_month
            // 12
        )
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
) -> tuple[datetime, datetime, int]:
    """
    Convert the parsed natural-language horizon into
    an actual forecast start/end range.
    """

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

    if horizon_type == (
        "calendar_year"
    ):

        year = int(
            horizon.get(
                "year"
            )
        )

        tzinfo = (
            reference_moment.tzinfo
        )

        start = datetime(
            year,
            1,
            1,
            0,
            0,
            0,
            tzinfo=tzinfo,
        )

        end = datetime(
            year + 1,
            1,
            1,
            0,
            0,
            0,
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
    """
    Find the Vimshottari Mahadasha / Antardasha
    containing an explicitly requested moment.
    """

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
    dashas.current_period corresponds to the
    requested date.
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
# CAREER QUESTION ANSWER HELPERS
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


def _build_specific_event_answer(
    parsed_question: dict[str, Any],
    forecast: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert the broad forecast into an answer
    specifically targeted to the user's question.

    This layer does not create new astrology scores.
    """

    intent = _safe_dict(
        parsed_question.get(
            "intent"
        )
    )

    event_name = str(
        intent.get(
            "event",
            "general_career",
        )
    )

    event_label = str(
        intent.get(
            "event_label",
            event_name,
        )
    )

    question_type = str(
        intent.get(
            "question_type",
            "general_outlook",
        )
    )

    direction = str(
        intent.get(
            "direction",
            "neutral",
        )
    )

    # -----------------------------------------------------
    # GENERAL CAREER QUESTION
    # -----------------------------------------------------

    if event_name == "general_career":

        overall = _safe_dict(
            forecast.get(
                "overall"
            )
        )

        return {
            "event": (
                event_name
            ),
            "event_label": (
                event_label
            ),
            "question_type": (
                question_type
            ),
            "direction": (
                direction
            ),
            "outcome": (
                overall.get(
                    "outlook"
                )
            ),
            "confidence": (
                overall.get(
                    "confidence"
                )
            ),
            "answer": (
                overall.get(
                    "summary",
                    (
                        "No clear general career forecast "
                        "was available for the requested period."
                    ),
                )
            ),
            "window": {},
        }

    event_data = (
        _question_event_data(
            forecast,
            event_name,
        )
    )

    available = bool(
        event_data.get(
            "available"
        )
    )

    window = _safe_dict(
        event_data.get(
            "window"
        )
    )

    strength = str(
        event_data.get(
            "outlook",
            "no_strong_window",
        )
    )

    confidence = (
        event_data.get(
            "confidence"
        )
    )

    start = window.get(
        "start"
    )

    end = window.get(
        "end"
    )

    peak_date = window.get(
        "peak_date"
    )

    period = window.get(
        "period"
    )

    # -----------------------------------------------------
    # NO STRONG WINDOW
    # -----------------------------------------------------

    if not available:

        if question_type == "timing":

            answer = (
                f"No sufficiently strong {event_label.lower()} "
                "window was identified in the requested period."
            )

        elif direction == "increase":

            answer = (
                f"The forecast does not identify a sufficiently "
                f"strong increase in {event_label.lower()} "
                "during the requested period."
            )

        elif direction == "decrease":

            answer = (
                f"The forecast does not identify a sufficiently "
                f"clear decrease in {event_label.lower()} "
                "during the requested period."
            )

        else:

            answer = (
                f"No sufficiently strong {event_label.lower()} "
                "signal was identified in the requested period."
            )

        return {
            "event": (
                event_name
            ),
            "event_label": (
                event_label
            ),
            "question_type": (
                question_type
            ),
            "direction": (
                direction
            ),
            "outcome": (
                "no_strong_window"
            ),
            "confidence": (
                confidence
            ),
            "answer": (
                answer
            ),
            "window": {},
        }

    # -----------------------------------------------------
    # CAREER PRESSURE + DECREASE QUESTION
    # -----------------------------------------------------

    if (
        event_name
        == "career_pressure_challenge"
        and direction == "decrease"
    ):

        answer = (
            f"A reduction in work pressure is not strongly "
            f"supported at the beginning of the forecast period. "
            f"Instead, a {strength.replace('_', ' ')} "
            f"career-pressure phase is identified from {start} "
            f"to {end}, with the strongest pressure around "
            f"{peak_date}. After this identified window ends, "
            "the specific elevated-pressure signal weakens "
            "within the scanned period."
        )

        return {
            "event": (
                event_name
            ),
            "event_label": (
                event_label
            ),
            "question_type": (
                question_type
            ),
            "direction": (
                direction
            ),
            "outcome": (
                "decrease_after_pressure_window"
            ),
            "confidence": (
                confidence
            ),
            "answer": (
                answer
            ),
            "window": (
                window
            ),
        }

    # -----------------------------------------------------
    # TIMING QUESTION
    # -----------------------------------------------------

    if question_type == "timing":

        answer = (
            f"The strongest {event_label.lower()} window "
            f"is identified from {start} to {end}, "
            f"with peak activation around {peak_date}."
        )

        if period:
            answer += (
                f" The peak falls during the "
                f"{period} period."
            )

        return {
            "event": (
                event_name
            ),
            "event_label": (
                event_label
            ),
            "question_type": (
                question_type
            ),
            "direction": (
                direction
            ),
            "outcome": (
                strength
            ),
            "confidence": (
                confidence
            ),
            "answer": (
                answer
            ),
            "window": (
                window
            ),
        }

    # -----------------------------------------------------
    # JOB CHANGE
    # -----------------------------------------------------

    if event_name == "job_change":

        answer = (
            f"The forecast shows a "
            f"{strength.replace('_', ' ')} "
            f"job-change or professional-transition signal. "
            f"The main window runs from {start} to {end}, "
            f"with the strongest activation around {peak_date}."
        )

    # -----------------------------------------------------
    # PROMOTION
    # -----------------------------------------------------

    elif event_name == (
        "promotion_recognition"
    ):

        answer = (
            f"The forecast shows a "
            f"{strength.replace('_', ' ')} "
            f"promotion or professional-recognition signal. "
            f"The identified window runs from {start} to {end}, "
            f"with peak activation around {peak_date}."
        )

    # -----------------------------------------------------
    # INCOME
    # -----------------------------------------------------

    elif event_name == "income_gains":

        answer = (
            f"The forecast shows a "
            f"{strength.replace('_', ' ')} "
            f"income or professional-gains signal. "
            f"The identified window runs from {start} to {end}, "
            f"with peak activation around {peak_date}."
        )

    # -----------------------------------------------------
    # FOREIGN
    # -----------------------------------------------------

    elif event_name == (
        "foreign_international_opportunity"
    ):

        answer = (
            f"The forecast shows a "
            f"{strength.replace('_', ' ')} "
            f"foreign or international-career theme. "
            f"The identified window runs from {start} to {end}, "
            f"with peak activation around {peak_date}."
        )

        confirmation = window.get(
            "confirmation"
        )

        if confirmation == "dasha_only":
            answer += (
                " The Dasha supports the theme, but "
                "event-specific transits do not yet provide "
                "strong confirmation."
            )

    # -----------------------------------------------------
    # PRESSURE
    # -----------------------------------------------------

    elif event_name == (
        "career_pressure_challenge"
    ):

        answer = (
            f"The forecast shows a "
            f"{strength.replace('_', ' ')} "
            f"career-pressure phase from {start} to {end}, "
            f"with the strongest activation around {peak_date}."
        )

    else:

        answer = (
            event_data.get(
                "summary",
                (
                    "A relevant career signal was identified "
                    "within the requested period."
                ),
            )
        )

    return {
        "event": (
            event_name
        ),
        "event_label": (
            event_label
        ),
        "question_type": (
            question_type
        ),
        "direction": (
            direction
        ),
        "outcome": (
            strength
        ),
        "confidence": (
            confidence
        ),
        "answer": (
            answer
        ),
        "window": (
            window
        ),
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
            "predictions": (
                predictions
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
        "chart": (
            chart
        ),
        "reading": (
            reading
        ),
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
                "reading": (
                    result[
                        "reading"
                    ]
                ),
                "predictions": (
                    result[
                        "predictions"
                    ]
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
                result[
                    "reading"
                ]
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
                "step_days": (
                    step_days
                ),
            },

            "forecast": (
                forecast
            ),

            "windows": (
                windows
            ),

            "scan_metadata": {
                "available": (
                    scan.get(
                        "available"
                    )
                ),
                "start": (
                    scan.get(
                        "start"
                    )
                ),
                "end": (
                    scan.get(
                        "end"
                    )
                ),
                "step_days": (
                    scan.get(
                        "step_days"
                    )
                ),
                "snapshot_count": (
                    scan.get(
                        "snapshot_count"
                    )
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
# NATURAL-LANGUAGE CAREER QUESTION
# =========================================================

@app.post(
    "/api/v1/career-question"
)
def answer_career_question(
    payload: CareerQuestionRequest,
):
    """
    Answer a natural-language career question.

    Pipeline:

        question
            ->
        deterministic intent parser
            ->
        event + question type + direction
            ->
        forecast horizon
            ->
        Dasha × transit forecast scan
            ->
        practical event windows
            ->
        user-facing forecast
            ->
        event-specific answer

    Example:

        "Will I change my job in the next 6 months?"

    becomes approximately:

        event:
            job_change

        direction:
            change

        forecast:
            6 months

        resolution:
            7 days
    """

    try:

        # -------------------------------------------------
        # VALIDATE REFERENCE MOMENT
        # -------------------------------------------------

        reference_moment = (
            payload.reference_moment
        )

        _require_timezone(
            reference_moment,
            "reference_moment",
        )

        # -------------------------------------------------
        # PARSE QUESTION
        # -------------------------------------------------

        parsed_question = (
            parse_career_question(
                payload.question
            )
        )

        # -------------------------------------------------
        # BUILD FORECAST RANGE
        # -------------------------------------------------

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

        forecast_span_days = (
            end - start
        ).days

        if forecast_span_days > 3650:
            raise ValueError(
                "Resolved career-question forecast range "
                "must not exceed 10 years."
            )

        # -------------------------------------------------
        # BUILD NATAL CHART
        # -------------------------------------------------

        chart = build_chart(
            payload.birth
        )

        # -------------------------------------------------
        # SCAN FORECAST
        # -------------------------------------------------

        scan = scan_career_forecast(
            chart,
            start,
            end,
            step_days=step_days,
        )

        # -------------------------------------------------
        # BUILD WINDOWS
        # -------------------------------------------------

        windows = (
            build_career_forecast_windows(
                scan
            )
        )

        # -------------------------------------------------
        # BUILD GENERAL FORECAST NARRATIVE
        # -------------------------------------------------

        forecast = (
            generate_career_forecast_narrative(
                windows
            )
        )

        # -------------------------------------------------
        # ANSWER THE SPECIFIC QUESTION
        # -------------------------------------------------

        answer = (
            _build_specific_event_answer(
                parsed_question,
                forecast,
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
                "step_days": (
                    step_days
                ),
            },

            "answer": (
                answer
            ),

            "forecast_context": {
                "overall": (
                    forecast.get(
                        "overall"
                    )
                ),

                "target_event": (
                    _question_event_data(
                        forecast,
                        str(
                            _safe_dict(
                                parsed_question.get(
                                    "intent"
                                )
                            ).get(
                                "event",
                                "general_career",
                            )
                        ),
                    )
                ),
            },

            "scan_metadata": {
                "available": (
                    scan.get(
                        "available"
                    )
                ),
                "start": (
                    scan.get(
                        "start"
                    )
                ),
                "end": (
                    scan.get(
                        "end"
                    )
                ),
                "step_days": (
                    scan.get(
                        "step_days"
                    )
                ),
                "snapshot_count": (
                    scan.get(
                        "snapshot_count"
                    )
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