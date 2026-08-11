from typing import Any


def _normalise_statement(statement: str) -> str:
    """
    Normalise a prediction statement so that semantically identical
    statements can be detected and deduplicated.
    """
    return " ".join(statement.strip().lower().split())


def aggregate_predictions(
    predictions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Aggregate and deduplicate prediction statements.

    Predictions with the same normalised statement are merged.
    The strongest confidence is retained and all supporting evidence
    is preserved.
    """

    grouped: dict[str, dict[str, Any]] = {}

    for prediction in predictions:
        statement = prediction.get("statement", "").strip()

        if not statement:
            continue

        key = _normalise_statement(statement)

        confidence = float(prediction.get("confidence", 0.0))
        evidence = prediction.get("evidence", {})

        if key not in grouped:
            grouped[key] = {
                "feature": prediction.get("feature"),
                "statement": statement,
                "confidence": confidence,
                "evidence": [evidence],
            }
            continue

        existing = grouped[key]

        # Keep the strongest confidence.
        existing["confidence"] = max(
            existing["confidence"],
            confidence,
        )

        # Preserve all supporting evidence.
        existing["evidence"].append(evidence)

    return list(grouped.values())