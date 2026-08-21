from __future__ import annotations

from typing import Any

from app.astrology.features.career_direction_intelligence_v1 import (
    analyze_career_direction_v1 as _analyze_career_direction_v1,
)


def analyze_career_direction_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Compatibility alias for the canonical Career Direction intelligence layer."""
    return _analyze_career_direction_v1(chart)
