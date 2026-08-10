from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.astrology.calculator import calculate_chart
from app.astrology.dasha import (
    build_vimshottari_dasha,
    find_current_period,
)
from app.models.chart import BirthInput
from app.services.geocoding import resolve_place


def build_chart(payload: BirthInput) -> dict:
    place = resolve_place(payload.place)

    local_tz = ZoneInfo(place["timezone"])

    local_birth = datetime(
        payload.date.year,
        payload.date.month,
        payload.date.day,
        payload.time.hour,
        payload.time.minute,
        payload.time.second,
        payload.time.microsecond,
        tzinfo=local_tz,
    )

    birth_utc = local_birth.astimezone(timezone.utc)

    calculated = calculate_chart(
        birth_utc=birth_utc,
        latitude=place["latitude"],
        longitude=place["longitude"],
    )

    moon_longitude = calculated["planets"]["Moon"]["longitude"]

    dasha = build_vimshottari_dasha(
        birth_local=local_birth,
        moon_longitude=moon_longitude,
    )

    now_local = datetime.now(local_tz)
    current_period = find_current_period(dasha, now_local)

    return {
        "methodology": {
            "astrology": "Vedic",
            "zodiac": "sidereal",
            "ayanamsa": "Lahiri",
            "house_system": "Whole Sign",
            "node": "Mean Node",
            "ephemeris": "Swiss Ephemeris",
        },
        "birth": {
            "date": payload.date.isoformat(),
            "time": payload.time.isoformat(),
            "local_datetime": local_birth.isoformat(),
            "utc_datetime": birth_utc.isoformat(),
            "place_query": payload.place,
            "resolved_place": place["resolved_name"],
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "timezone": place["timezone"],
        },
        "ascendant": calculated["ascendant"],
        "planets": calculated["planets"],
        "houses": calculated["houses"],
        "dashas": {
            **dasha,
            "current_period": current_period,
        },
    }
