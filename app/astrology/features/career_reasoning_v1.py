from __future__ import annotations

from typing import Any

from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1


def analyze_career_v1(chart: dict[str, Any]) -> dict[str, Any]:
    """Compatibility alias for the Career & Profession natal foundation."""
    return analyze_career_profession_v1(chart)
