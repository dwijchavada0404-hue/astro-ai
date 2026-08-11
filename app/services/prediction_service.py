from typing import Any

from app.astrology.features.marriage import MarriageFeature


FEATURES = [
    MarriageFeature(),
]


def generate_predictions(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run all registered prediction features against a validated
    astrology chart.
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

    return predictions
