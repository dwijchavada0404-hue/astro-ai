from datetime import datetime, timedelta
from typing import Any

from app.astrology.constants import DASHA_ORDER, DASHA_YEARS, NAKSHATRAS


DAYS_PER_YEAR = 365.2425


def _add_years(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * DAYS_PER_YEAR)


def _next_planet(planet: str) -> str:
    index = DASHA_ORDER.index(planet)
    return DASHA_ORDER[(index + 1) % len(DASHA_ORDER)]


def _dasha_sequence(start_planet: str):
    planet = start_planet
    for _ in range(len(DASHA_ORDER)):
        yield planet
        planet = _next_planet(planet)


def build_vimshottari_dasha(
    birth_local: datetime,
    moon_longitude: float,
    years_to_generate: float = 120.0,
) -> dict[str, Any]:
    """
    Calculates Vimshottari Mahadasha and Antardasha.

    The first Mahadasha is determined by the Moon's nakshatra.
    The elapsed portion of that nakshatra reduces the first
    Mahadasha proportionally.
    """
    nak_span = 360.0 / 27.0
    nak_index = min(int((moon_longitude % 360.0) / nak_span), 26)
    within_nak = (moon_longitude % 360.0) - nak_index * nak_span

    nak_fraction_elapsed = within_nak / nak_span
    nak_name, first_planet = NAKSHATRAS[nak_index]

    remaining_fraction = 1.0 - nak_fraction_elapsed
    first_duration = DASHA_YEARS[first_planet] * remaining_fraction

    mahadashas = []
    cursor = birth_local
    generated_days = 0.0

    planet = first_planet
    first = True

    while generated_days < years_to_generate * DAYS_PER_YEAR:
        full_years = DASHA_YEARS[planet]
        duration_years = first_duration if first else full_years

        start = cursor
        end = _add_years(start, duration_years)

        antardashas = []
        ad_cursor = start

        # Antardasha order starts from the Mahadasha lord.
        for ad_planet in _dasha_sequence(planet):
            ad_years = (
                duration_years
                * DASHA_YEARS[ad_planet]
                / 120.0
            )
            ad_start = ad_cursor
            ad_end = _add_years(ad_start, ad_years)

            antardashas.append({
                "planet": ad_planet,
                "start": ad_start.isoformat(),
                "end": ad_end.isoformat(),
                "duration_years": round(ad_years, 8),
            })
            ad_cursor = ad_end

        mahadashas.append({
            "planet": planet,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "duration_years": round(duration_years, 8),
            "antardashas": antardashas,
        })

        generated_days += duration_years * DAYS_PER_YEAR
        cursor = end
        planet = _next_planet(planet)
        first = False

    return {
        "system": "Vimshottari",
        "moon_nakshatra": nak_name,
        "first_mahadasha_lord": first_planet,
        "nakshatra_elapsed_fraction": round(nak_fraction_elapsed, 8),
        "mahadashas": mahadashas,
    }


def find_current_period(
    dashas: dict[str, Any],
    moment: datetime,
) -> dict[str, Any] | None:
    target = moment

    for md in dashas["mahadashas"]:
        start = datetime.fromisoformat(md["start"])
        end = datetime.fromisoformat(md["end"])

        if start <= target < end:
            for ad in md["antardashas"]:
                ad_start = datetime.fromisoformat(ad["start"])
                ad_end = datetime.fromisoformat(ad["end"])
                if ad_start <= target < ad_end:
                    return {
                        "mahadasha": md["planet"],
                        "mahadasha_start": md["start"],
                        "mahadasha_end": md["end"],
                        "antardasha": ad["planet"],
                        "antardasha_start": ad["start"],
                        "antardasha_end": ad["end"],
                    }

    return None
