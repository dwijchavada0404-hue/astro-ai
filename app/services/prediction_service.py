from typing import Any

from app.astrology.features.marriage import MarriageFeature
from app.astrology.features.evidence_aggregator import aggregate_predictions


FEATURES = [
    MarriageFeature(),
]


def generate_predictions(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run all registered prediction features against a validated
    astrology chart and aggregate the resulting predictions.
    """

    predictions: list[dict[str, Any]] = []

    for feature in FEATURES:
        feature_predictions = feature.generate(chart)

        for prediction in feature_predictions:
            predictions.append(
                {
                    "feature": prediction.feature,
                    "statement": prediction.statement,
                    "confidence": prediction.confidence,
                    "evidence": prediction.evidence,
                }
            )

    return aggregate_predictions(predictions)