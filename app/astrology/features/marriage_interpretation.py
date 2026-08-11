from typing import Any


def interpret_seventh_lord_placement(
    evidence: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Interpret the house placement of the 7th lord.

    This is intentionally conservative. A single placement should
    create an indicator, not a definitive prediction.
    """

    house = evidence.get("house")

    if house is None:
        return None

    interpretations = {
        1: {
            "indicator": "marriage strongly connected with identity and life direction",
            "score": 1.0,
        },
        2: {
            "indicator": "marriage may have a strong connection with family and finances",
            "score": 1.0,
        },
        3: {
            "indicator": "marriage may involve communication, networking or the immediate environment",
            "score": 0.8,
        },
        4: {
            "indicator": "marriage may have a strong connection with home and domestic life",
            "score": 1.0,
        },
        5: {
            "indicator": "romance and emotional attraction may play an important role in marriage",
            "score": 1.2,
        },
        6: {
            "indicator": "marriage may require effort in managing disagreements and practical responsibilities",
            "score": -0.8,
        },
        7: {
            "indicator": "marriage is strongly emphasized in the life pattern",
            "score": 1.5,
        },
        8: {
            "indicator": "marriage may bring significant transformation and deeper emotional experiences",
            "score": 0.5,
        },
        9: {
            "indicator": "marriage may be connected with travel, higher learning, different cultural influences or fortune",
            "score": 1.0,
        },
        10: {
            "indicator": "marriage may have a strong connection with career, status or professional circumstances",
            "score": 1.0,
        },
        11: {
            "indicator": "marriage may be connected with social networks, friendships, gains and fulfillment of desires",
            "score": 1.3,
        },
        12: {
            "indicator": "marriage may involve distance, relocation, foreign connections, privacy or living away from the birthplace",
            "score": 1.0,
        },
    }

    interpretation = interpretations.get(house)

    if interpretation is None:
        return None

    return {
        "rule": "seventh_lord_house_interpretation",
        "house": house,
        "indicator": interpretation["indicator"],
        "score": interpretation["score"],
        "confidence": 0.65,
    }


def interpret_venus(
    evidence: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Interpret Venus as a relationship significator.

    This first version uses house placement only.
    """

    house = evidence.get("house")

    if house is None:
        return None

    interpretations = {
        1: "strong personal emphasis on attraction, charm and relationships",
        2: "relationship themes may connect with family, speech and material stability",
        3: "relationships may develop through communication, social interaction or networking",
        4: "strong desire for emotional comfort and harmony in domestic life",
        5: "strong romantic and affectionate relationship tendencies",
        6: "relationships may require practical adjustment and conflict management",
        7: "partnership and marriage are strongly emphasized",
        8: "relationships may be emotionally intense and transformative",
        9: "relationships may involve travel, different backgrounds or broader cultural influences",
        10: "relationships may intersect with career or public life",
        11: "relationships may develop through friends, networks or social circles",
        12: "relationships may involve privacy, distance, travel or foreign connections",
    }

    indicator = interpretations.get(house)

    if indicator is None:
        return None

    return {
        "rule": "venus_house_interpretation",
        "house": house,
        "indicator": indicator,
        "score": 1.0,
        "confidence": 0.6,
    }


def interpret_jupiter(
    evidence: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Interpret Jupiter as a supporting marriage significator.
    """

    house = evidence.get("house")

    if house is None:
        return None

    interpretations = {
        1: "Jupiter supports optimism, growth and constructive partnership tendencies",
        2: "Jupiter connects marriage with family growth and material stability",
        3: "Jupiter supports communication, learning and social interaction",
        4: "Jupiter supports domestic stability and family-oriented partnership",
        5: "Jupiter supports romance, affection and emotional generosity",
        6: "Jupiter may encourage growth through practical relationship challenges",
        7: "Jupiter strongly supports partnership and marriage themes",
        8: "Jupiter can support emotional depth and transformation within marriage",
        9: "Jupiter supports travel, different backgrounds, learning and broader perspectives",
        10: "Jupiter connects partnership with career development and social standing",
        11: "Jupiter supports gains, friendships and fulfillment through partnership",
        12: "Jupiter may connect marriage with travel, foreign environments, distance or private life",
    }

    indicator = interpretations.get(house)

    if indicator is None:
        return None

    return {
        "rule": "jupiter_house_interpretation",
        "house": house,
        "indicator": indicator,
        "score": 0.7,
        "confidence": 0.55,
    }


def interpret_marriage_evidence(
    evidence_list: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert raw marriage evidence into interpreted indicators.
    """

    interpretations: list[dict[str, Any]] = []

    for evidence in evidence_list:
        rule = evidence.get("rule")

        result = None

        if rule == "seventh_lord_placement":
            result = interpret_seventh_lord_placement(evidence)

        elif rule == "venus_placement":
            result = interpret_venus(evidence)

        elif rule == "jupiter_placement":
            result = interpret_jupiter(evidence)

        if result is not None:
            interpretations.append(result)

    return interpretations


def calculate_marriage_score(
    interpretations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate an overall preliminary marriage indicator score.

    This is NOT a probability of marriage.
    It is an internal strength score used by the prediction engine.
    """

    if not interpretations:
        return {
            "score": 0.0,
            "indicator_count": 0,
            "assessment": "insufficient_evidence",
        }

    score = sum(
        float(item.get("score", 0.0))
        for item in interpretations
    )

    if score >= 3.0:
        assessment = "strong"
    elif score >= 1.5:
        assessment = "moderately_strong"
    elif score >= 0.5:
        assessment = "mixed"
    else:
        assessment = "challenging"

    return {
        "score": round(score, 2),
        "indicator_count": len(interpretations),
        "assessment": assessment,
    }