from typing import Any

from .base import Prediction, PredictionFeature
from .marriage_reasoning import analyze_seventh_house
from .marriage_rules import evaluate_marriage_rules


class MarriageFeature(PredictionFeature):
    """
    Vedic astrology marriage and relationship prediction feature.

    The feature separates:
    1. Raw astrological evidence
    2. Interpretation
    3. User-facing prediction statements
    """

    name = "marriage"

    def generate(self, chart: dict[str, Any]) -> list[Prediction]:
        predictions: list[Prediction] = []

        reasoning = analyze_seventh_house(chart)

        if not reasoning.get("available"):
            return [
                Prediction(
                    feature=self.name,
                    statement=(
                        "Marriage analysis could not be completed because "
                        "7th-house data is unavailable."
                    ),
                    confidence=0.0,
                    evidence=reasoning,
                )
            ]

        seventh_house = reasoning["seventh_house"]
        seventh_lord = reasoning["seventh_lord"]

        sign = seventh_house.get("sign")
        lord_planet = seventh_lord.get("planet")
        lord_house = seventh_lord.get("house")
        lord_sign = seventh_lord.get("sign")

        # ---------------------------------------------------------
        # Raw evidence
        # ---------------------------------------------------------

        raw_evidence = evaluate_marriage_rules(
            chart,
            lord_planet,
        )

        # ---------------------------------------------------------
        # 1. Spouse personality
        # ---------------------------------------------------------

        sign_traits = {
            "Aries": ["independent", "direct", "energetic"],
            "Taurus": ["stable", "practical", "comfort-oriented"],
            "Gemini": ["communicative", "curious", "adaptable"],
            "Cancer": ["caring", "emotional", "protective"],
            "Leo": ["confident", "warm", "expressive"],
            "Virgo": ["practical", "analytical", "detail-oriented"],
            "Libra": ["balanced", "social", "relationship-oriented"],
            "Scorpio": ["intense", "loyal", "private"],
            "Sagittarius": ["optimistic", "independent", "adventurous"],
            "Capricorn": ["disciplined", "practical", "ambitious"],
            "Aquarius": ["independent", "intellectual", "unconventional"],
            "Pisces": ["empathetic", "sensitive", "imaginative"],
        }

        traits = sign_traits.get(sign, [])

        if traits:
            predictions.append(
                Prediction(
                    feature=self.name,
                    statement=(
                        "The 7th-house sign indicates potential spouse "
                        f"personality traits: {', '.join(traits)}."
                    ),
                    confidence=0.70,
                    evidence={
                        "rule": "7th_house_sign_personality",
                        "seventh_house_sign": sign,
                        "traits": traits,
                    },
                )
            )

        # ---------------------------------------------------------
        # 2. 7th lord placement
        # ---------------------------------------------------------

        if lord_planet and lord_house is not None:
            predictions.append(
                Prediction(
                    feature=self.name,
                    statement=(
                        f"The 7th lord, {lord_planet}, is placed in the "
                        f"{lord_house}th house, making this house an "
                        "important channel through which marriage and "
                        "spouse-related matters may manifest."
                    ),
                    confidence=0.75,
                    evidence={
                        "rule": "seventh_lord_placement",
                        "planet": lord_planet,
                        "house": lord_house,
                        "sign": lord_sign,
                    },
                )
            )

        # ---------------------------------------------------------
        # 3. Reasoning indicators
        #
        # Do NOT repeat the raw seventh-lord placement here because
        # it has already been converted into a prediction above.
        # ---------------------------------------------------------

        for indicator in reasoning["indicators"]:
            if indicator["factor"] == "seventh_lord_house":
                continue

            predictions.append(
                Prediction(
                    feature=self.name,
                    statement=indicator["interpretation"],
                    confidence=min(
                        max(float(indicator.get("strength", 0.5)), 0.0),
                        1.0,
                    ),
                    evidence={
                        "rule": indicator["factor"],
                        "value": indicator["value"],
                    },
                )
            )

        # ---------------------------------------------------------
        # 4. Preserve raw planetary evidence for future synthesis
        #
        # We expose this as evidence but do not generate separate
        # user-facing predictions for Venus/Jupiter/Mars yet.
        # ---------------------------------------------------------

        if raw_evidence:
            predictions.append(
                Prediction(
                    feature=self.name,
                    statement=(
                        "Marriage analysis includes Venus, Jupiter, Mars "
                        "and 7th-lord placement as supporting evidence."
                    ),
                    confidence=0.50,
                    evidence={
                        "rule": "marriage_planetary_evidence",
                        "raw_evidence": raw_evidence,
                    },
                )
            )

        return predictions