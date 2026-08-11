from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Prediction:
    feature: str
    statement: str
    confidence: float
    evidence: Dict[str, Any]


class PredictionFeature:
    """
    Base interface for an astrology prediction feature.

    Each feature should:
    1. Receive the validated birth chart.
    2. Analyse relevant astrological factors.
    3. Return structured Prediction objects.
    """

    name = "base"

    def generate(self, chart: Any) -> list[Prediction]:
        raise NotImplementedError(
            "Prediction features must implement generate()."
        )
