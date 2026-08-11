from typing import Any

from app.astrology.features.base import Prediction
from app.astrology.features.marriage import MarriageFeature
from app.astrology.features.spouse_personality import (
    analyze_spouse_personality,
)

FEATURES = [
    MarriageFeature(),
]


def generate_predictions(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run all registered prediction features against a validated
    astrology chart.
    """

    predictions: list[dict[str, Any]] = []

    # Run registered feature classes.
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

    # Spouse personality analysis.
    personality = analyze_spouse_personality(chart)

    if personality:
        predictions.append(
            {
                "feature": "marriage",
                "statement": (
                    "The 7th-house sign indicates the following "
                    "potential spouse personality traits: "
                    + ", ".join(personality["traits"])
                    + "."
                ),
                "confidence": personality["confidence"],
                "evidence": {
                    "rule": personality["rule"],
                    "seventh_house_sign": personality["sign"],
                    "traits": personality["traits"],
                },
            }
        )

    return predictions