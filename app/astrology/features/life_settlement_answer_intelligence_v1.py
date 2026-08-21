from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.astrology.features.life_settlement_question_intelligence_v1 import analyze_life_settlement_question_v1
from app.astrology.features.life_settlement_synthesis_v1 import analyze_life_settlement_synthesis_v1
from app.astrology.features.life_settlement_timing_v1 import analyze_life_settlement_timing_v1


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _parse_dt(value: Any, tzinfo) -> datetime | None:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return None
    else:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    return dt


def _birth_date(chart: dict[str, Any]) -> date | None:
    birth = _safe_dict(chart.get("birth"))
    for key in ("local_datetime", "utc_datetime"):
        value = birth.get(key)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                pass
    value = birth.get("date")
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _age_on(day: date, born: date) -> int:
    return day.year - born.year - ((day.month, day.day) < (born.month, born.day))


def _age_range_for_window(window: dict[str, Any], chart: dict[str, Any], reference_moment: datetime) -> dict[str, int] | None:
    born = _birth_date(chart)
    if not born:
        return None
    start = _parse_dt(window.get("start"), reference_moment.tzinfo)
    end = _parse_dt(window.get("end"), reference_moment.tzinfo)
    if not start or not end:
        return None
    return {"start_age": _age_on(start.date(), born), "end_age": _age_on(end.date(), born)}


def _target_age_date(chart: dict[str, Any], age: int, reference_moment: datetime) -> datetime | None:
    born = _birth_date(chart)
    if not born:
        return None
    year = born.year + age
    try:
        target = date(year, born.month, born.day)
    except ValueError:
        target = date(year, 2, 28)
    return datetime(target.year, target.month, target.day, tzinfo=reference_moment.tzinfo)


def _window_contains(window: dict[str, Any], moment: datetime) -> bool:
    start = _parse_dt(window.get("start"), moment.tzinfo)
    end = _parse_dt(window.get("end"), moment.tzinfo)
    return bool(start and end and start <= moment <= end)


def answer_life_settlement_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    """Answer cross-domain settlement questions without manufacturing certainty."""
    understanding = analyze_life_settlement_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "event": "unknown",
            "route": "unsupported",
            "understanding": understanding,
            "reason": "The question was not identified as a Life Settlement question.",
        }

    synthesis = analyze_life_settlement_synthesis_v1(chart, reference_moment)
    intent = str(understanding.get("primary_intent") or "settlement_overview")
    timing = None
    if understanding.get("requires_timing_engine"):
        timing = analyze_life_settlement_timing_v1(chart, reference_moment)

    if intent in {"settlement_timing", "settlement_age"}:
        if not timing or not timing.get("strongest_convergence_window"):
            answer = (
                "The current domain engines do not provide enough overlapping date-bounded evidence to identify a meaningful "
                "cross-domain settlement window. I would not infer a settlement age or year from incomplete timing evidence."
            )
        else:
            window = _safe_dict(timing.get("strongest_convergence_window"))
            labels = window.get("domain_labels") or []
            answer = (
                f"The strongest symbolic cross-domain convergence currently falls between {window.get('start')} and {window.get('end')}, "
                f"with simultaneous support across {', '.join(labels)}."
            )
            age_range = _age_range_for_window(window, chart, reference_moment)
            if intent == "settlement_age" and age_range:
                start_age = age_range["start_age"]
                end_age = age_range["end_age"]
                age_text = str(start_age) if start_age == end_age else f"{start_age}–{end_age}"
                answer += f" Based on the recorded birth date, that corresponds approximately to age {age_text}."
            answer += " This is a convergence window, not a guaranteed date by which life will be settled."

    elif intent == "target_age_outlook":
        target_age = understanding.get("target_age")
        if not isinstance(target_age, int):
            answer = "A target age was not reliably identified from the question, so no age-specific settlement conclusion is produced."
        else:
            target_moment = _target_age_date(chart, target_age, reference_moment)
            windows = timing.get("ranked_convergence_windows", []) if isinstance(timing, dict) else []
            matching = next((window for window in windows if target_moment and _window_contains(window, target_moment)), None)
            if matching:
                answer = (
                    f"Around age {target_age}, the timing engine places the target date inside a symbolic cross-domain convergence "
                    f"window involving {', '.join(matching.get('domain_labels') or [])}. This suggests broader simultaneous support, "
                    "not that every milestone will already be completed."
                )
            else:
                answer = (
                    f"The current timing evidence does not place age {target_age} inside a sufficiently supported multi-domain convergence "
                    "window. That does not mean life will be unstable at that age; it means the astrology evidence is not strong enough "
                    "to make that cross-domain timing claim."
                )
    else:
        answer = synthesis.get("answer") if synthesis.get("available") else synthesis.get("reason")
        if intent == "multi_domain_stability" and synthesis.get("available"):
            answer = (
                str(answer)
                + " Settlement is evaluated across the full domain set rather than requiring Career, Finance and Marriage alone to define it."
            )

    return {
        "available": bool(synthesis.get("available")),
        "event": "life_settlement",
        "model_version": "v1",
        "route": "life_settlement_answer_intelligence_v1",
        "primary_intent": intent,
        "understanding": understanding,
        "synthesis": synthesis,
        "timing": timing,
        "answer": answer,
        "historical_validation": synthesis.get("historical_validation"),
        "reality_override": {
            "required": True,
            "rule": (
                "Known real-world milestones override predictive assumptions. A milestone already achieved must be treated as achieved, "
                "and historical astrology may only help interpret it rather than contradict or erase it."
            ),
        },
        "limitation": (
            "Life Settlement is a cross-domain symbolic astrology construct, not a deterministic milestone. It does not guarantee a "
            "specific settlement age/date, career success, wealth, marriage, property ownership, fertility, pregnancy, childbirth or "
            "family outcome. Missing or non-overlapping timing evidence must remain uncertain rather than being converted into a prediction."
        ),
    }
