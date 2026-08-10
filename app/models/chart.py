from datetime import date, time
from typing import Any

from pydantic import BaseModel, Field


class BirthInput(BaseModel):
    date: date
    time: time
    place: str = Field(min_length=2, max_length=200)


class BirthChart(BaseModel):
    methodology: dict[str, Any]
    birth: dict[str, Any]
    ascendant: dict[str, Any]
    planets: dict[str, Any]
    houses: dict[str, Any]
    dashas: dict[str, Any]
