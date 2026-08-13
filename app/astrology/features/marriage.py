from typing import Any

from .base import Prediction, PredictionFeature
from .marriage_planets import analyze_marriage_planets
from .marriage_reasoning import analyze_seventh_house
from .dasha_marriage_reasoning import (
    analyze_current_dasha_for_marriage,
)


class MarriageFeature(PredictionFeature):
    """
    Vedic astrology marriage and relationship prediction feature.

    Combines:

    - 7th-house reasoning
    - 7th-lord analysis
    - Venus analysis
    - Jupiter analysis
    - Mars analysis
    - Current Vimshottari Dasha timing

    The feature converts structured astrology evidence into
    user-facing prediction statements.
    """

    name = "marriage"

    def generate(
        self,
        chart: dict[str, Any],
    ) -> list[Prediction]:

        predictions: list[Prediction] = []

        # =====================================================
        # 1. 7TH-HOUSE REASONING
        # =====================================================

        seventh_house_analysis = analyze_seventh_house(
            chart
        )

        if seventh_house_analysis.get("available"):

            seventh_house = (
                seventh_house_analysis.get(
                    "seventh_house",
                    {},
                )
            )

            seventh_sign = seventh_house.get(
                "sign"
            )

            # -------------------------------------------------
            # Spouse personality from 7th-house sign
            # -------------------------------------------------

            if seventh_sign:

                personality_traits = {
                    "Aries": [
                        "independent",
                        "direct",
                        "energetic",
                    ],
                    "Taurus": [
                        "stable",
                        "practical",
                        "loyal",
                    ],
                    "Gemini": [
                        "communicative",
                        "curious",
                        "adaptable",
                    ],
                    "Cancer": [
                        "caring",
                        "sensitive",
                        "protective",
                    ],
                    "Leo": [
                        "confident",
                        "warm",
                        "expressive",
                    ],
                    "Virgo": [
                        "practical",
                        "analytical",
                        "detail-oriented",
                    ],
                    "Libra": [
                        "balanced",
                        "social",
                        "diplomatic",
                    ],
                    "Scorpio": [
                        "intense",
                        "loyal",
                        "private",
                    ],
                    "Sagittarius": [
                        "optimistic",
                        "independent",
                        "adventurous",
                    ],
                    "Capricorn": [
                        "disciplined",
                        "ambitious",
                        "responsible",
                    ],
                    "Aquarius": [
                        "independent",
                        "intellectual",
                        "unconventional",
                    ],
                    "Pisces": [
                        "empathetic",
                        "sensitive",
                        "imaginative",
                    ],
                }

                traits = personality_traits.get(
                    seventh_sign
                )

                if traits:

                    predictions.append(
                        Prediction(
                            feature=self.name,
                            statement=(
                                "The 7th-house sign indicates "
                                "potential spouse personality "
                                f"traits: {', '.join(traits)}."
                            ),
                            confidence=0.7,
                            evidence={
                                "rule": (
                                    "7th_house_sign_personality"
                                ),
                                "seventh_house_sign": (
                                    seventh_sign
                                ),
                                "traits": traits,
                            },
                        )
                    )

            # -------------------------------------------------
            # Structured 7th-house indicators
            # -------------------------------------------------

            for indicator in (
                seventh_house_analysis.get(
                    "indicators",
                    [],
                )
            ):

                interpretation = indicator.get(
                    "interpretation"
                )

                if not interpretation:
                    continue

                predictions.append(
                    Prediction(
                        feature=self.name,
                        statement=interpretation,
                        confidence=float(
                            indicator.get(
                                "strength",
                                0.5,
                            )
                        ),
                        evidence={
                            "rule": indicator.get(
                                "factor"
                            ),
                            "value": indicator.get(
                                "value"
                            ),
                        },
                    )
                )

        # =====================================================
        # 2. PLANETARY MARRIAGE INDICATORS
        # =====================================================

        planetary_analysis = analyze_marriage_planets(
            chart
        )

        for indicator in planetary_analysis.get(
            "indicators",
            [],
        ):

            interpretation = indicator.get(
                "interpretation"
            )

            if not interpretation:
                continue

            predictions.append(
                Prediction(
                    feature=self.name,
                    statement=interpretation,
                    confidence=float(
                        indicator.get(
                            "strength",
                            0.5,
                        )
                    ),
                    evidence={
                        "rule": indicator.get(
                            "factor"
                        ),
                        "value": indicator.get(
                            "value"
                        ),
                    },
                )
            )

        # =====================================================
        # 3. CURRENT DASHA TIMING
        # =====================================================

        dasha_analysis = (
            analyze_current_dasha_for_marriage(
                chart
            )
        )

        if dasha_analysis.get("available"):

            mahadasha = dasha_analysis.get(
                "mahadasha"
            )

            antardasha = dasha_analysis.get(
                "antardasha"
            )

            outlook = dasha_analysis.get(
                "outlook"
            )

            dasha_confidence = float(
                dasha_analysis.get(
                    "confidence",
                    0.5,
                )
            )

            # -------------------------------------------------
            # Current Dasha period
            # -------------------------------------------------

            if mahadasha and antardasha:

                if outlook == "strongly_supportive":

                    statement = (
                        f"The current {mahadasha}/"
                        f"{antardasha} period strongly "
                        "activates marriage and relationship "
                        "matters."
                    )

                elif outlook == "moderately_supportive":

                    statement = (
                        f"The current {mahadasha}/"
                        f"{antardasha} period provides "
                        "moderate support for relationship "
                        "and marriage developments."
                    )

                elif outlook == "mixed":

                    statement = (
                        f"The current {mahadasha}/"
                        f"{antardasha} period has mixed "
                        "marriage indications, combining "
                        "relationship themes with factors "
                        "that may introduce delay, distance "
                        "or uncertainty."
                    )

                else:

                    statement = (
                        f"The current {mahadasha}/"
                        f"{antardasha} period does not show "
                        "strong direct activation of marriage "
                        "matters."
                    )

                predictions.append(
                    Prediction(
                        feature=self.name,
                        statement=statement,
                        confidence=dasha_confidence,
                        evidence={
                            "rule": (
                                "current_dasha_marriage_timing"
                            ),
                            "mahadasha": mahadasha,
                            "antardasha": antardasha,
                            "outlook": outlook,
                            "mahadasha_start": (
                                dasha_analysis.get(
                                    "mahadasha_start"
                                )
                            ),
                            "mahadasha_end": (
                                dasha_analysis.get(
                                    "mahadasha_end"
                                )
                            ),
                            "antardasha_start": (
                                dasha_analysis.get(
                                    "antardasha_start"
                                )
                            ),
                            "antardasha_end": (
                                dasha_analysis.get(
                                    "antardasha_end"
                                )
                            ),
                        },
                    )
                )

            # -------------------------------------------------
            # Detailed Dasha indicators
            # -------------------------------------------------

            for indicator in (
                dasha_analysis.get(
                    "indicators",
                    [],
                )
            ):

                interpretation = indicator.get(
                    "interpretation"
                )

                if not interpretation:
                    continue

                predictions.append(
                    Prediction(
                        feature=self.name,
                        statement=interpretation,
                        confidence=float(
                            indicator.get(
                                "strength",
                                0.5,
                            )
                        ),
                        evidence={
                            "rule": indicator.get(
                                "factor"
                            ),
                            "value": indicator.get(
                                "value"
                            ),
                            "type": indicator.get(
                                "type"
                            ),
                            "dasha": {
                                "mahadasha": mahadasha,
                                "antardasha": antardasha,
                            },
                        },
                    )
                )

        # =====================================================
        # 4. RETURN STRUCTURED PREDICTIONS
        # =====================================================

        return predictions