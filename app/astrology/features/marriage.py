from typing import Any

from .base import Prediction, PredictionFeature
from .marriage_planets import analyze_marriage_planets
from .marriage_reasoning import analyze_seventh_house


class MarriageFeature(PredictionFeature):
    """
    Vedic astrology marriage and relationship prediction feature.

    Combines:
    - 7th-house reasoning
    - 7th-lord analysis
    - Venus analysis
    - Jupiter analysis
    - Mars analysis

    The feature converts structured astrology evidence into
    user-facing prediction statements.
    """

    name = "marriage"

    def generate(self, chart: dict[str, Any]) -> list[Prediction]:
        predictions: list[Prediction] = []

        seventh_house_analysis = analyze_seventh_house(chart)
        planetary_analysis = analyze_marriage_planets(chart)

        # -----------------------------------------------------
        # 7th-house reasoning
        # -----------------------------------------------------

        if seventh_house_analysis.get("available"):
            seventh_house = seventh_house_analysis.get(
                "seventh_house",
                {},
            )

            seventh_sign = seventh_house.get("sign")

            if seventh_sign:
                personality_traits = {
                    "Aries": ["independent", "direct", "energetic"],
                    "Taurus": ["stable", "practical", "loyal"],
                    "Gemini": ["communicative", "curious", "adaptable"],
                    "Cancer": ["caring", "sensitive", "protective"],
                    "Leo": ["confident", "warm", "expressive"],
                    "Virgo": ["practical", "analytical", "detail-oriented"],
                    "Libra": ["balanced", "social", "diplomatic"],
                    "Scorpio": ["intense", "loyal", "private"],
                    "Sagittarius": ["optimistic", "independent", "adventurous"],
                    "Capricorn": ["disciplined", "ambitious", "responsible"],
                    "Aquarius": ["independent", "intellectual", "unconventional"],
                    "Pisces": ["empathetic", "sensitive", "imaginative"],
                }

                traits = personality_traits.get(seventh_sign)

                if traits:
                    predictions.append(
                        Prediction(
                            feature=self.name,
                            statement=(
                                "The 7th-house sign indicates potential "
                                f"spouse personality traits: {', '.join(traits)}."
                            ),
                            confidence=0.7,
                            evidence={
                                "rule": "7th_house_sign_personality",
                                "seventh_house_sign": seventh_sign,
                                "traits": traits,
                            },
                        )
                    )

            # Convert structured 7th-house indicators into predictions.
            for indicator in seventh_house_analysis.get("indicators", []):
                interpretation = indicator.get("interpretation")

                if not interpretation:
                    continue

                predictions.append(
                    Prediction(
                        feature=self.name,
                        statement=interpretation,
                        confidence=float(
                            indicator.get("strength", 0.5)
                        ),
                        evidence={
                            "rule": indicator.get("factor"),
                            "value": indicator.get("value"),
                        },
                    )
                )

        # -----------------------------------------------------
        # Planetary marriage indicators
        # -----------------------------------------------------

        for indicator in planetary_analysis.get("indicators", []):
            interpretation = indicator.get("interpretation")

            if not interpretation:
                continue

            predictions.append(
                Prediction(
                    feature=self.name,
                    statement=interpretation,
                    confidence=float(
                        indicator.get("strength", 0.5)
                    ),
                    evidence={
                        "rule": indicator.get("factor"),
                        "value": indicator.get("value"),
                    },
                )
            )

        return predictions