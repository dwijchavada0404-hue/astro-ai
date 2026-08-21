from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.astrology.features.life_settlement_synthesis_v1 import DOMAIN_LABELS, DOMAIN_ORDER, analyze_life_settlement_synthesis_v1


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
    return dt.replace(tzinfo=tzinfo) if dt.tzinfo is None else dt


def _period_score(period: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        if period.get(key) is not None:
            return _bounded(_safe_float(period.get(key)))
    if period.get("score") is not None:
        return _bounded(_safe_float(period.get("score")))
    return None


def _candidate_from_period(domain: str, period: Any, reference_moment: datetime, score_keys: tuple[str, ...]) -> dict[str, Any] | None:
    if not isinstance(period, dict):
        return None
    start = _parse_dt(period.get("start"), reference_moment.tzinfo)
    end = _parse_dt(period.get("end"), reference_moment.tzinfo)
    if not start or not end or end <= start:
        return None
    score = _period_score(period, score_keys)
    if score is None:
        return None
    return {"domain": domain, "start": start, "end": end, "score": score, "source": period}


def _domain_future_candidates(domain: str, component: dict[str, Any], reference_moment: datetime) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    score_keys = {
        "career": ("career_support_score",),
        "finance": ("finance_support_score", "wealth_support_score", "financial_support_score"),
        "marriage": ("marriage_support_score", "support_score"),
        "property_home": ("home_property_support_score",),
        "family_children": ("family_support_score",),
        "location_settlement": ("foreign_settlement_support_score", "foreign_exposure_score", "relocation_activation_score"),
    }[domain]

    direct = component.get("strongest_future_period") or component.get("strongest_future_window")
    candidate = _candidate_from_period(domain, direct, reference_moment, score_keys)
    if candidate:
        candidates.append(candidate)

    timing = component.get("components", {}).get("timing") if isinstance(component.get("components"), dict) else None
    if isinstance(timing, dict):
        future = timing.get("future") if isinstance(timing.get("future"), dict) else {}
        for key in ("strongest_period", "strongest_window"):
            candidate = _candidate_from_period(domain, future.get(key), reference_moment, score_keys)
            if candidate:
                candidates.append(candidate)

    if domain == "marriage" and isinstance(component.get("components"), dict):
        for slot in ("marriage_timing", "spouse_meeting"):
            routed = component["components"].get(slot)
            if not isinstance(routed, dict):
                continue
            for key in ("strongest_future_period", "strongest_future_window", "best_window"):
                candidate = _candidate_from_period(domain, routed.get(key), reference_moment, score_keys)
                if candidate:
                    candidates.append(candidate)
            for key in ("future_windows", "windows", "ranked_windows"):
                values = routed.get(key)
                if isinstance(values, list):
                    for value in values:
                        candidate = _candidate_from_period(domain, value, reference_moment, score_keys)
                        if candidate:
                            candidates.append(candidate)

    unique: dict[tuple[str, str, float], dict[str, Any]] = {}
    for item in candidates:
        unique[(item["start"].isoformat(), item["end"].isoformat(), item["score"])] = item
    return list(unique.values())


def _overlap_windows(candidates: list[dict[str, Any]], minimum_domains: int = 2) -> list[dict[str, Any]]:
    if not candidates:
        return []
    boundaries = sorted({item["start"] for item in candidates} | {item["end"] for item in candidates})
    windows: list[dict[str, Any]] = []
    for start, end in zip(boundaries, boundaries[1:]):
        if end <= start:
            continue
        active = [item for item in candidates if item["start"] < end and item["end"] > start]
        domains = sorted({item["domain"] for item in active}, key=DOMAIN_ORDER.index)
        if len(domains) < minimum_domains:
            continue
        domain_scores = {domain: max(item["score"] for item in active if item["domain"] == domain) for domain in domains}
        mean_score = sum(domain_scores.values()) / len(domain_scores)
        convergence_score = _bounded(mean_score + 0.06 * max(0, len(domains) - minimum_domains))
        windows.append({
            "start": start.isoformat(), "end": end.isoformat(), "domain_count": len(domains), "domains": domains,
            "domain_labels": [DOMAIN_LABELS[domain] for domain in domains], "domain_scores": domain_scores,
            "convergence_score": convergence_score,
        })
    return sorted(windows, key=lambda item: (item["convergence_score"], item["domain_count"]), reverse=True)


def analyze_life_settlement_timing_v1(chart: dict[str, Any], reference_moment: datetime, *, lookahead_years: int = 7, minimum_domains: int = 2) -> dict[str, Any]:
    """Identify future periods where multiple mature life domains converge."""
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    if not 1 <= lookahead_years <= 10:
        raise ValueError("lookahead_years must be between 1 and 10.")
    if not 2 <= minimum_domains <= len(DOMAIN_ORDER):
        raise ValueError("minimum_domains must be between 2 and the number of supported domains.")

    synthesis = analyze_life_settlement_synthesis_v1(chart, reference_moment)
    if not synthesis.get("available"):
        return {"available": False, "event": "life_settlement_timing", "model_version": "v1", "reason": "Cross-domain life synthesis is unavailable.", "synthesis": synthesis}

    horizon_end = reference_moment + timedelta(days=365 * lookahead_years)
    candidates: list[dict[str, Any]] = []
    components = synthesis.get("components") if isinstance(synthesis.get("components"), dict) else {}
    for domain in DOMAIN_ORDER:
        component = components.get(domain)
        if not isinstance(component, dict) or not component.get("available"):
            continue
        for candidate in _domain_future_candidates(domain, component, reference_moment):
            if candidate["end"] <= reference_moment or candidate["start"] >= horizon_end:
                continue
            candidate["start"] = max(candidate["start"], reference_moment)
            candidate["end"] = min(candidate["end"], horizon_end)
            candidates.append(candidate)

    windows = _overlap_windows(candidates, minimum_domains=minimum_domains)
    strongest = windows[0] if windows else None
    participating_domains = sorted({item["domain"] for item in candidates}, key=DOMAIN_ORDER.index)
    if strongest:
        outlook = "cross_domain_convergence_identified"
        answer = "A future cross-domain convergence window was identified across " + ", ".join(strongest["domain_labels"]) + ". This is a symbolic period of simultaneous support, not a guaranteed settlement date."
    elif candidates:
        outlook = "domain_windows_present_without_material_overlap"
        answer = "Future domain-support windows are present, but no sufficiently overlapping multi-domain settlement window was identified."
    else:
        outlook = "timing_evidence_insufficient"
        answer = "The mature domain engines did not provide enough date-bounded future timing evidence for cross-domain convergence analysis."

    coverage = len(participating_domains) / len(DOMAIN_ORDER)
    confidence = _bounded(0.35 + 0.30 * coverage + (0.20 * strongest["convergence_score"] if strongest else 0.0))
    return {
        "available": bool(candidates), "event": "life_settlement_timing", "model_version": "v1",
        "reference_moment": reference_moment.isoformat(), "lookahead_years": lookahead_years, "minimum_domains": minimum_domains,
        "timing_outlook": outlook, "confidence": confidence, "timing_domain_coverage": round(coverage, 3),
        "participating_domains": participating_domains, "candidate_period_count": len(candidates), "convergence_window_count": len(windows),
        "strongest_convergence_window": strongest, "ranked_convergence_windows": windows[:10],
        "domain_future_periods": {domain: [{"start": item["start"].isoformat(), "end": item["end"].isoformat(), "score": item["score"]} for item in candidates if item["domain"] == domain] for domain in participating_domains},
        "synthesis": synthesis, "historical_validation": synthesis.get("historical_validation"), "answer": answer,
        "limitation": (
            "This is symbolic astrological timing synthesis only. A convergence window is not a promise that a person will become 'settled', nor does it guarantee employment, income, wealth, marriage, property ownership, conception, pregnancy, childbirth, family outcomes, relocation, immigration, citizenship or foreign settlement. The engine intentionally does not manufacture a precise settlement age/date where the underlying timing evidence does not support one."
        ),
    }
