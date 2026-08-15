from typing import Any


# =========================================================
# EVENT LABELS
# =========================================================

EVENT_LABELS = {
    "marriage_timing": (
        "Marriage Timing"
    ),
    "relationship_commitment": (
        "Relationship / Commitment"
    ),
    "marriage_delay_challenge": (
        "Marriage Delay / Challenge"
    ),
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _safe_dict(
    value: Any,
) -> dict[str, Any]:

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# =========================================================
# PLANET ACCESS
# =========================================================

def _planet_data(
    mapped_transits: dict[str, Any],
    planet: str,
) -> dict[str, Any]:

    planets = _safe_dict(
        mapped_transits.get(
            "planets"
        )
    )

    return _safe_dict(
        planets.get(
            planet
        )
    )


def _planet_house(
    mapped_transits: dict[str, Any],
    planet: str,
) -> int | None:

    data = _planet_data(
        mapped_transits,
        planet,
    )

    house = data.get(
        "natal_house"
    )

    if isinstance(
        house,
        int,
    ):
        return house

    return None


# =========================================================
# HOUSE RELEVANCE
# =========================================================

def _house_support_score(
    house: int | None,
    planet: str,
) -> float:
    """
    Marriage-oriented transit support.

    Strongest houses:

        1  self / life direction
        5  romance / affection
        7  partnership / marriage
        9  fortune / blessings
        11 gains / fulfilment / social support

    Planet-specific weighting is applied because
    Jupiter/Venus in these houses are not equivalent
    to Rahu/Ketu/Saturn occupying the same houses.
    """

    if house is None:
        return 0.0

    general_support = {
        1: 0.65,
        2: 0.45,
        5: 0.80,
        7: 1.00,
        9: 0.65,
        11: 0.70,
    }

    value = general_support.get(
        house,
        0.0,
    )

    benefic_multipliers = {
        "Jupiter": 1.00,
        "Venus": 1.00,
        "Moon": 0.75,
        "Mercury": 0.60,
        "Sun": 0.45,
        "Mars": 0.30,
        "Saturn": 0.35,
        "Rahu": 0.20,
        "Ketu": 0.15,
    }

    multiplier = (
        benefic_multipliers.get(
            planet,
            0.40,
        )
    )

    return _clamp(
        value
        * multiplier
    )


# =========================================================
# CHALLENGE RELEVANCE
# =========================================================

def _house_challenge_score(
    house: int | None,
    planet: str,
) -> float:
    """
    Challenge signal for marriage / relationships.

    Malefic occupancy of 1, 7, 8 and 12 receives
    stronger attention.

    This represents complexity, pressure, uncertainty
    or unconventional developments — not automatic
    denial of marriage.
    """

    if house is None:
        return 0.0

    sensitive_houses = {
        1: 0.55,
        5: 0.40,
        7: 1.00,
        8: 0.70,
        12: 0.55,
    }

    house_weight = (
        sensitive_houses.get(
            house,
            0.0,
        )
    )

    planet_weights = {
        "Saturn": 0.70,
        "Rahu": 0.85,
        "Ketu": 0.80,
        "Mars": 0.65,
        "Sun": 0.30,
    }

    planet_weight = (
        planet_weights.get(
            planet,
            0.0,
        )
    )

    return _clamp(
        house_weight
        * planet_weight
    )


# =========================================================
# JUPITER SUPPORT
# =========================================================

def _jupiter_support(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:

    house = _planet_house(
        mapped_transits,
        "Jupiter",
    )

    base = _house_support_score(
        house,
        "Jupiter",
    )

    # Jupiter in Lagna can support major life
    # developments and commitment orientation.

    if house == 1:
        base = max(
            base,
            0.80,
        )

    if house == 5:
        base = max(
            base,
            0.90,
        )

    if house == 7:
        base = 1.00

    if house == 9:
        base = max(
            base,
            0.75,
        )

    if house == 11:
        base = max(
            base,
            0.80,
        )

    return {
        "planet": "Jupiter",
        "house": house,
        "support": round(
            base,
            3,
        ),
    }


# =========================================================
# VENUS SUPPORT
# =========================================================

def _venus_support(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:

    house = _planet_house(
        mapped_transits,
        "Venus",
    )

    base = _house_support_score(
        house,
        "Venus",
    )

    if house == 5:
        base = 1.00

    elif house == 7:
        base = 1.00

    elif house == 11:
        base = max(
            base,
            0.85,
        )

    elif house in (
        1,
        2,
        9,
    ):
        base = max(
            base,
            0.65,
        )

    return {
        "planet": "Venus",
        "house": house,
        "support": round(
            base,
            3,
        ),
    }


# =========================================================
# MOON SUPPORT
# =========================================================

def _moon_support(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:

    house = _planet_house(
        mapped_transits,
        "Moon",
    )

    base = _house_support_score(
        house,
        "Moon",
    )

    return {
        "planet": "Moon",
        "house": house,
        "support": round(
            base,
            3,
        ),
    }


# =========================================================
# SEVENTH-HOUSE ACTIVATION
# =========================================================

def _seventh_house_activation(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:
    """
    Identify direct transit occupancy of natal 7th house.

    Benefics increase relationship activation.
    Malefics can activate the same house but may produce
    more complexity or unconventional circumstances.
    """

    planets = _safe_dict(
        mapped_transits.get(
            "planets"
        )
    )

    occupants = []

    support = 0.0
    challenge = 0.0

    for (
        planet,
        raw_data,
    ) in planets.items():

        data = _safe_dict(
            raw_data
        )

        if data.get(
            "natal_house"
        ) != 7:
            continue

        occupants.append(
            planet
        )

        support += (
            _house_support_score(
                7,
                planet,
            )
        )

        challenge += (
            _house_challenge_score(
                7,
                planet,
            )
        )

    support = _clamp(
        support
    )

    challenge = _clamp(
        challenge
    )

    return {
        "house": 7,
        "occupants": (
            occupants
        ),
        "support": round(
            support,
            3,
        ),
        "challenge": round(
            challenge,
            3,
        ),
    }


# =========================================================
# NODE / SATURN PRESSURE
# =========================================================

def _challenge_analysis(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:

    details = []

    scores = []

    for planet in (
        "Saturn",
        "Rahu",
        "Ketu",
        "Mars",
    ):

        house = _planet_house(
            mapped_transits,
            planet,
        )

        score = (
            _house_challenge_score(
                house,
                planet,
            )
        )

        details.append(
            {
                "planet": (
                    planet
                ),
                "house": (
                    house
                ),
                "challenge": round(
                    score,
                    3,
                ),
            }
        )

        scores.append(
            score
        )

    if scores:

        strongest = max(
            scores
        )

        average = (
            sum(
                scores
            )
            / len(
                scores
            )
        )

    else:

        strongest = 0.0
        average = 0.0

    combined = _clamp(
        strongest
        * 0.70
        + average
        * 0.30
    )

    return {
        "combined_challenge": round(
            combined,
            3,
        ),
        "details": (
            details
        ),
    }


# =========================================================
# TRANSIT CONFIRMATION
# =========================================================

def _confirmation_label(
    support: float,
    challenge: float,
) -> str:

    if (
        support >= 0.70
        and challenge < 0.50
    ):
        return "strong_transit_support"

    if (
        support >= 0.55
        and challenge < 0.70
    ):
        return "transit_supported"

    if (
        support >= 0.40
    ):
        return "mixed_transit_support"

    if challenge >= 0.65:
        return "challenging_transits"

    return "weak_transit_support"


# =========================================================
# MAIN TRANSIT ANALYSIS
# =========================================================

def analyze_marriage_transits_v2(
    mapped_transits: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert mapped sidereal transits into marriage /
    relationship event evidence.

    No transit calculation occurs here.

    Expected input:

        map_transits_to_natal_houses(...)

    Current Phase 1 events:

        marriage_timing
        relationship_commitment
        marriage_delay_challenge
    """

    if not isinstance(
        mapped_transits,
        dict,
    ):
        raise ValueError(
            "mapped_transits must be a dictionary."
        )

    if not mapped_transits.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Mapped transit data is unavailable."
            ),
        }

    jupiter = (
        _jupiter_support(
            mapped_transits
        )
    )

    venus = (
        _venus_support(
            mapped_transits
        )
    )

    moon = (
        _moon_support(
            mapped_transits
        )
    )

    seventh_house = (
        _seventh_house_activation(
            mapped_transits
        )
    )

    challenges = (
        _challenge_analysis(
            mapped_transits
        )
    )

    jupiter_support = _safe_float(
        jupiter.get(
            "support"
        )
    )

    venus_support = _safe_float(
        venus.get(
            "support"
        )
    )

    moon_support = _safe_float(
        moon.get(
            "support"
        )
    )

    seventh_support = _safe_float(
        seventh_house.get(
            "support"
        )
    )

    seventh_challenge = _safe_float(
        seventh_house.get(
            "challenge"
        )
    )

    general_challenge = _safe_float(
        challenges.get(
            "combined_challenge"
        )
    )

    # -----------------------------------------------------
    # MARRIAGE TIMING TRANSIT SUPPORT
    # -----------------------------------------------------

    marriage_support = (
        jupiter_support
        * 0.35
        + venus_support
        * 0.30
        + seventh_support
        * 0.25
        + moon_support
        * 0.10
    )

    marriage_support = (
        _clamp(
            marriage_support
        )
    )

    # -----------------------------------------------------
    # RELATIONSHIP COMMITMENT TRANSIT SUPPORT
    # -----------------------------------------------------

    commitment_support = (
        venus_support
        * 0.35
        + jupiter_support
        * 0.25
        + seventh_support
        * 0.25
        + moon_support
        * 0.15
    )

    commitment_support = (
        _clamp(
            commitment_support
        )
    )

    # -----------------------------------------------------
    # CHALLENGE SCORE
    # -----------------------------------------------------

    challenge_score = (
        general_challenge
        * 0.70
        + seventh_challenge
        * 0.30
    )

    challenge_score = _clamp(
        challenge_score
    )

    marriage_confirmation = (
        _confirmation_label(
            marriage_support,
            challenge_score,
        )
    )

    commitment_confirmation = (
        _confirmation_label(
            commitment_support,
            challenge_score,
        )
    )

    return {
        "available": True,

        "moment": (
            mapped_transits.get(
                "moment"
            )
        ),

        "components": {
            "jupiter": (
                jupiter
            ),

            "venus": (
                venus
            ),

            "moon": (
                moon
            ),

            "seventh_house": (
                seventh_house
            ),

            "challenge_analysis": (
                challenges
            ),
        },

        "event_scores": {
            "marriage_timing": round(
                marriage_support,
                3,
            ),

            "relationship_commitment": round(
                commitment_support,
                3,
            ),

            "marriage_delay_challenge": round(
                challenge_score,
                3,
            ),
        },

        "confirmations": {
            "marriage_timing": (
                marriage_confirmation
            ),

            "relationship_commitment": (
                commitment_confirmation
            ),

            "marriage_delay_challenge": (
                (
                    "strong_challenge_signal"
                    if challenge_score
                    >= 0.70
                    else (
                        "moderate_challenge_signal"
                        if challenge_score
                        >= 0.50
                        else "weak_challenge_signal"
                    )
                )
            ),
        },
    }