from typing import Any

from .base import Prediction, PredictionFeature
from .marriage_interpretation import (
    calculate_marriage_score,
    interpret_marriage_evidence,
)
from .marriage_rules import evaluate_marriage_rules


SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}


class MarriageFeature(PredictionFeature):
    """
    Marriage prediction feature.

    Pipeline:

        chart
          ↓
        raw marriage rules
          ↓
        interpreted indicators
          ↓
        preliminary score
          ↓
        structured Predictions
    """

    name = "marriage"

    def generate(self, chart: dict[str, Any]) -> list[Prediction]:
        predictions: list[Prediction] = []

        houses = chart.get("houses", {})
        planets = chart.get("planets", {})

        seventh_house = houses.get("7")

        if not seventh_house:
            return predictions

        seventh_sign = seventh_house.get("sign")
        seventh_lord = SIGN_LORDS.get(seventh_sign)

        # ---------------------------------------------------------
        # 1. Extract raw astrological evidence
        # ---------------------------------------------------------

        evidence = evaluate_marriage_rules(
            chart=chart,
            seventh_lord=seventh_lord,
        )

        # ---------------------------------------------------------
        # 2. Interpret the evidence
        # ---------------------------------------------------------

        interpretations = interpret_marriage_evidence(evidence)

        # ---------------------------------------------------------
        # 3. Calculate preliminary score
        # ---------------------------------------------------------

        score = calculate_marriage_score(interpretations)

        # ---------------------------------------------------------
        # 4. Return individual interpreted indicators
        # ---------------------------------------------------------

        for interpretation in interpretations:
            predictions.append(
                Prediction(
                    feature=self.name,
                    statement=interpretation["indicator"],
                    confidence=float(
                        interpretation.get("confidence", 0.5)
                    ),
                    evidence=interpretation,
                )
            )

        # ---------------------------------------------------------
        # 5. Return overall assessment
        # ---------------------------------------------------------

        predictions.append(
            Prediction(
                feature=self.name,
                statement=(
                    "Preliminary marriage indicator assessment: "
                    f"{score['assessment']}."
                ),
                confidence=0.6,
                evidence={
                    "score": score["score"],
                    "indicator_count": score["indicator_count"],
                    "seventh_house": seventh_house,
                    "seventh_lord": seventh_lord,
                    "raw_evidence": evidence,
                    "interpretations": interpretations,
                },
            )
        )

        return predictions