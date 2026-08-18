from __future__ import annotations

import re
from typing import Any

from app.astrology.features.marriage_question_intelligence_v2 import (
    analyze_marriage_question_v2,
)


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
    "relationship_stability": (
        "Relationship Stability"
    ),
    "foreign_intercultural_connection": (
        "Foreign / Intercultural Relationship"
    ),
    "spouse_traits": (
        "Spouse Traits / Partner Profile"
    ),
    "spouse_appearance": (
        "Spouse Appearance / Physical Profile"
    ),
    "spouse_education": (
        "Spouse Education / Intellectual Profile"
    ),
    "spouse_profession": (
        "Spouse Profession / Career Profile"
    ),
    "spouse_meeting": (
        "Meeting Future Spouse"
    ),
    "love_marriage": (
        "Love Marriage"
    ),
    "arranged_marriage": (
        "Arranged Marriage"
    ),
    "love_vs_arranged": (
        "Love vs Arranged Marriage"
    ),
    "general_marriage": (
        "General Marriage / Relationship Outlook"
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


def _safe_list(
    value: Any,
) -> list[Any]:

    if isinstance(
        value,
        list,
    ):
        return value

    return []


def _normalise_question(
    question: str,
) -> str:

    return " ".join(
        question.strip().lower().split()
    )


# =========================================================
# YEAR EXTRACTION
# =========================================================

def _extract_years(
    question: str,
) -> list[int]:

    values = re.findall(
        r"\b(20\d{2}|21\d{2})\b",
        question,
    )

    years = []

    for value in values:

        year = int(
            value
        )

        if year not in years:

            years.append(
                year
            )

    return years


# =========================================================
# COMPARISON DETECTION
# =========================================================

def _detect_comparison(
    question: str,
) -> dict[str, Any]:

    years = (
        _extract_years(
            question
        )
    )

    markers = (
        " or ",
        "better",
        "which year",
        "which is better",
        "more likely",
        "stronger",
        "best year",
    )

    is_comparison = (
        len(
            years
        )
        >= 2
        and any(
            marker in question
            for marker in markers
        )
    )

    if not is_comparison:

        return {
            "is_comparison": False,
            "comparison_type": None,
            "values": [],
        }

    return {
        "is_comparison": True,
        "comparison_type": (
            "calendar_years"
        ),
        "values": years,
    }


# =========================================================
# FOLLOW-UP DETECTION
# =========================================================

def _detect_follow_up(
    question: str,
) -> dict[str, Any]:

    patterns = (
        r"^what about\b",
        r"^how about\b",
        r"^and what about\b",
    )

    is_follow_up = any(
        re.search(
            pattern,
            question,
        )
        for pattern in patterns
    )

    return {
        "is_follow_up": (
            is_follow_up
        ),
        "requires_context": (
            is_follow_up
        ),
    }


# =========================================================
# FOREIGN / INTERCULTURAL DETECTION
# =========================================================

def _detect_foreign_intercultural(
    question: str,
) -> dict[str, Any] | None:

    profession_patterns = (
        r"\bwork(?:ing)? abroad\b",
        r"\bjob abroad\b",
        r"\bcareer abroad\b",
        r"\bwork(?:ing)? overseas\b",
        r"\binternational job\b",
        r"\binternational career\b",
        r"\bforeign job\b",
        r"\bforeign career\b",
        r"\bwork(?:ing)? internationally\b",
    )

    if any(
        re.search(
            pattern,
            question,
        )
        for pattern in profession_patterns
    ):

        return None

    pattern_map = (
        (
            r"\bmarry\s+(?:a\s+)?foreigner\b",
            "marry a foreigner",
        ),
        (
            r"\bmarry\s+someone\s+foreign\b",
            "marry someone foreign",
        ),
        (
            r"\bforeign\s+(?:spouse|husband|wife|partner)\b",
            "foreign spouse",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r"(?:\s+(?:be|is|come|comes))?\s+from\s+another\s+country\b",
            "spouse from another country",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r"(?:\s+(?:be|is|come|comes))?\s+from\s+(?:a\s+)?different\s+country\b",
            "spouse from a different country",
        ),
        (
            r"\bmarry\s+(?:someone|a person)\s+from\s+another\s+country\b",
            "marry someone from another country",
        ),
        (
            r"\bmarry\s+(?:someone|a person)\s+from\s+(?:a\s+)?different\s+country\b",
            "marry someone from a different country",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r"(?:\s+(?:be|is|come|comes))?\s+from\s+abroad\b",
            "spouse from abroad",
        ),
        (
            r"\bmarry\s+someone\s+from\s+abroad\b",
            "marry someone from abroad",
        ),
        (
            r"\binter[\s-]?cultural\s+marriage\b",
            "intercultural marriage",
        ),
        (
            r"\binter[\s-]?cultural\s+relationship\b",
            "intercultural relationship",
        ),
        (
            r"\bcross[\s-]?cultural\s+marriage\b",
            "cross-cultural marriage",
        ),
        (
            r"\bcross[\s-]?cultural\s+relationship\b",
            "cross-cultural relationship",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner)"
            r".{0,20}\b(?:different|another)\s+culture\b",
            "spouse from a different culture",
        ),
        (
            r"\bmarry\s+someone\s+from\s+(?:a\s+)?(?:different|another)\s+culture\b",
            "marry someone from another culture",
        ),
        (
            r"\b(?:different|another)\s+cultural\s+background\b",
            "different cultural background",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner)"
            r".{0,20}\b(?:different|another)\s+nationality\b",
            "spouse with a different nationality",
        ),
        (
            r"\b(?:different|another)\s+nationality\b",
            "different nationality",
        ),
        (
            r"\bdifferent\s+national\s+background\b",
            "different national background",
        ),
        (
            r"\bmarry\s+someone\s+from\s+(?:a\s+)?different\s+religion\b",
            "marry someone from a different religion",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner)"
            r".{0,20}\b(?:different|another)\s+religion\b",
            "spouse from a different religion",
        ),
        (
            r"\binter[\s-]?faith\s+marriage\b",
            "interfaith marriage",
        ),
        (
            r"\binter[\s-]?faith\s+relationship\b",
            "interfaith relationship",
        ),
        (
            r"\b(?:different|another)\s+ethnicity\b",
            "different ethnicity",
        ),
        (
            r"\bdifferent\s+ethnic\s+background\b",
            "different ethnic background",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner)"
            r".{0,20}\b(?:different|another)\s+state\b",
            "spouse from another state",
        ),
        (
            r"\bmarry\s+someone\s+from\s+(?:a\s+)?(?:different|another)\s+state\b",
            "marry someone from another state",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner)"
            r".{0,20}\b(?:different|another)\s+region\b",
            "spouse from a different region",
        ),
        (
            r"\bmarry\s+someone\s+from\s+(?:a\s+)?(?:different|another)\s+region\b",
            "marry someone from a different region",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner)"
            r".{0,20}\b(?:different|another)\s+community\b",
            "spouse from a different community",
        ),
        (
            r"\bmarry\s+someone\s+from\s+(?:a\s+)?(?:different|another)\s+community\b",
            "marry someone from a different community",
        ),
    )

    matched = []

    for (
        pattern,
        canonical_keyword,
    ) in pattern_map:

        if re.search(
            pattern,
            question,
        ):

            if (
                canonical_keyword
                not in matched
            ):

                matched.append(
                    canonical_keyword
                )

    if not matched:

        return None

    return {
        "event": (
            "foreign_intercultural_connection"
        ),
        "event_label": (
            EVENT_LABELS[
                "foreign_intercultural_connection"
            ]
        ),
        "matched_keywords": (
            matched
        ),
    }


# =========================================================
# SPOUSE PROFESSION DETECTION
# =========================================================

def _detect_spouse_profession(
    question: str,
) -> dict[str, Any] | None:

    spouse_markers = (
        "spouse",
        "future spouse",
        "partner",
        "future partner",
        "person i marry",
        "person i will marry",
        "husband",
        "wife",
    )

    if not any(
        marker in question
        for marker in spouse_markers
    ):

        return None

    general_profession_keywords = (
        "profession",
        "career",
        "job",
        "occupation",
        "work for",
        "do for work",
        "does for work",
        "working in",
        "work in",
        "work as",
        "working as",
        "career field",
        "professional field",
    )

    targeted_profession_keywords = (
        "work abroad",
        "working abroad",
        "job abroad",
        "career abroad",
        "work overseas",
        "working overseas",
        "international job",
        "international career",
        "work internationally",
        "working internationally",
        "foreign job",
        "foreign career",

        "lawyer",
        "advocate",
        "legal profession",
        "legal career",
        "legal job",
        "work in law",
        "working in law",

        "corporate job",
        "corporate career",
        "corporate work",
        "work in corporate",
        "working in corporate",
        "corporate sector",

        "consultant",
        "consulting",
        "advisory job",
        "advisory career",
        "advisory profession",

        "finance",
        "banking",
        "banker",
        "financial sector",
        "financial career",
        "financial job",

        "designer",
        "design",
        "creative career",
        "creative profession",
        "creative job",
        "fashion",
        "luxury",
        "media",

        "technology",
        "tech job",
        "tech career",
        "software",
        "software engineer",
        "it job",
        "it career",
        "information technology",

        "business",
        "entrepreneur",
        "entrepreneurship",
        "self employed",
        "self-employed",
        "own business",
        "run a business",
        "start a business",
    )

    matched = []

    for keyword in (
        general_profession_keywords
        + targeted_profession_keywords
    ):

        if keyword in question:

            matched.append(
                keyword
            )

    if not matched:

        return None

    return {
        "event": (
            "spouse_profession"
        ),
        "event_label": (
            EVENT_LABELS[
                "spouse_profession"
            ]
        ),
        "matched_keywords": (
            matched
        ),
    }


# =========================================================
# SPOUSE EDUCATION DETECTION
# =========================================================

def _detect_spouse_education(question: str) -> dict[str, Any] | None:
    spouse_markers=("spouse","future spouse","partner","future partner","husband","wife","person i marry","person i will marry")
    if not any(x in question for x in spouse_markers): return None
    patterns=((r"\beducation\b","spouse education"),(r"\beducated\b","spouse educated"),(r"\bqualification\b","spouse qualification"),(r"\bqualified\b","spouse qualification"),(r"\bdegree\b","spouse degree"),(r"\bpostgraduate\b","spouse higher education"),(r"\bpost graduate\b","spouse higher education"),(r"\bmasters?\s+degree\b","spouse higher education"),(r"\bmaster's\s+degree\b","spouse higher education"),(r"\bdoctorate\b","spouse higher education"),(r"\bphd\b","spouse higher education"),(r"\bstudy\s+abroad\b","spouse international education"),(r"\bstudied\s+abroad\b","spouse international education"),(r"\beducated\s+abroad\b","spouse international education"),(r"\bforeign\s+university\b","spouse international education"),(r"\bstudy\s+law\b","spouse law education"),(r"\blaw\s+degree\b","spouse law education"),(r"\bstudy\s+design\b","spouse creative education"),(r"\bdesign\s+degree\b","spouse creative education"),(r"\bfinance\s+degree\b","spouse finance education"),(r"\bcommerce\s+(?:degree|background)\b","spouse commerce education"),(r"\bresearch\s+degree\b","spouse research education"),(r"\btechnical\s+(?:education|degree)\b","spouse technical education"),(r"\bcomputer\s+science\b","spouse technical education"),(r"\bprofessional\s+(?:qualification|degree)\b","spouse professional qualification"),(r"\bprofessionally\s+qualified\b","spouse professional qualification"),(r"\bchartered\s+accountant\b","spouse professional qualification"),(r"\bca\s+qualification\b","spouse professional qualification"),(r"\bmba\b","spouse professional qualification"),(r"\bintelligent\b","spouse intellect"),(r"\bintellectual\b","spouse intellect"),(r"\banalytical\b","spouse intellect"),(r"\bacademic[-\s]minded\b","spouse intellect"),(r"\blearning\s+style\b","spouse intellect"))
    matched=[]
    for pattern,label in patterns:
        if re.search(pattern,question) and label not in matched: matched.append(label)
    if not matched:return None
    return {"event":"spouse_education","event_label":EVENT_LABELS["spouse_education"],"matched_keywords":matched}


# =========================================================
# SPOUSE APPEARANCE DETECTION
# =========================================================

def _detect_spouse_appearance(
    question: str,
) -> dict[str, Any] | None:

    spouse_markers = (
        "spouse",
        "future spouse",
        "partner",
        "future partner",
        "husband",
        "wife",
        "person i marry",
        "person i will marry",
    )

    if not any(
        marker in question
        for marker in spouse_markers
    ):

        return None

    pattern_map = (
        (
            r"\bwhat\s+will\s+(?:my\s+)?(?:future\s+)?"
            r"(?:spouse|partner|husband|wife)\s+look\s+like\b",
            "what will my spouse look like",
        ),
        (
            r"\bwhat\s+does\s+(?:my\s+)?(?:future\s+)?"
            r"(?:spouse|partner|husband|wife)\s+look\s+like\b",
            "what does my spouse look like",
        ),
        (
            r"\bdescribe\s+(?:my\s+)?(?:future\s+)?"
            r"(?:spouse|partner|husband|wife)(?:'s)?\s+appearance\b",
            "describe spouse appearance",
        ),
        (
            r"\bphysical\s+appearance\b",
            "physical appearance",
        ),
        (
            r"\bappearance\s+of\s+(?:my\s+)?(?:future\s+)?"
            r"(?:spouse|partner|husband|wife)\b",
            "spouse appearance",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:tall|short)\b",
            "spouse height",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:height|how tall)\b",
            "spouse height",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:slim|slender|lean|athletic|well-built|well built)\b",
            "spouse build",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:body type|body build|physique|build)\b",
            "spouse build",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:attractive|beautiful|handsome|pretty|good-looking|good looking)\b",
            "spouse attractiveness",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:facial features|sharp features|soft features|defined features)\b",
            "spouse facial features",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r"(?:'s)?\s+(?:face|eyes|eye|expression)\b",
            "spouse facial appearance",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:youthful|young-looking|young looking|look younger)\b",
            "spouse youthful appearance",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:mature-looking|mature looking|look mature|older-looking|older looking)\b",
            "spouse mature appearance",
        ),
        (
            r"\b(?:spouse|future spouse|partner|future partner|husband|wife)"
            r".{0,30}\b(?:striking|distinctive)\s+(?:appearance|presence|look)\b",
            "spouse visual presence",
        ),
        (
            r"\bwhat\s+kind\s+of\s+appearance\s+will\s+"
            r"(?:my\s+)?(?:future\s+)?(?:spouse|partner|husband|wife)\s+have\b",
            "spouse appearance",
        ),
    )

    matched = []

    for (
        pattern,
        canonical_keyword,
    ) in pattern_map:

        if re.search(
            pattern,
            question,
        ):

            if (
                canonical_keyword
                not in matched
            ):

                matched.append(
                    canonical_keyword
                )

    if not matched:

        return None

    return {
        "event": (
            "spouse_appearance"
        ),
        "event_label": (
            EVENT_LABELS[
                "spouse_appearance"
            ]
        ),
        "matched_keywords": (
            matched
        ),
    }


# =========================================================
# SPECIAL EVENT DETECTION
# =========================================================

def _detect_special_events(
    question: str,
) -> list[dict[str, Any]]:

    detected = []

    # -----------------------------------------------------
    # SPOUSE MEETING
    # -----------------------------------------------------

    spouse_meeting_keywords = (
        "meet my future spouse",
        "meet future spouse",
        "meet my spouse",
        "when will i meet",
        "when do i meet",
        "meet the person i marry",
        "meet the person i will marry",
    )

    matched = [
        keyword
        for keyword in spouse_meeting_keywords
        if keyword in question
    ]

    if matched:

        detected.append(
            {
                "event": (
                    "spouse_meeting"
                ),
                "event_label": (
                    EVENT_LABELS[
                        "spouse_meeting"
                    ]
                ),
                "matched_keywords": (
                    matched
                ),
            }
        )

    # -----------------------------------------------------
    # FOREIGN / INTERCULTURAL RELATIONSHIP
    # -----------------------------------------------------

    foreign_intercultural = (
        _detect_foreign_intercultural(
            question
        )
    )

    if foreign_intercultural:

        detected.append(
            foreign_intercultural
        )

    # -----------------------------------------------------
    # SPOUSE PROFESSION
    # -----------------------------------------------------

    spouse_profession = (
        _detect_spouse_profession(
            question
        )
    )

    if spouse_profession:

        detected.append(
            spouse_profession
        )

    # -----------------------------------------------------
    # SPOUSE EDUCATION
    # -----------------------------------------------------

    spouse_education = _detect_spouse_education(question)
    if spouse_education:
        detected.append(spouse_education)

    # -----------------------------------------------------
    # SPOUSE APPEARANCE
    # -----------------------------------------------------

    spouse_appearance = (
        _detect_spouse_appearance(
            question
        )
    )

    if spouse_appearance:

        detected.append(
            spouse_appearance
        )

    # -----------------------------------------------------
    # SPOUSE TRAITS / PROFILE
    # -----------------------------------------------------

    spouse_traits_keywords = (
        "what will my future spouse be like",
        "what will my spouse be like",
        "what will my partner be like",
        "what kind of person will i marry",
        "what kind of person will i end up marrying",
        "what kind of personality will my spouse have",
        "what personality will my spouse have",
        "what kind of personality will my partner have",
        "describe my future spouse",
        "describe my spouse",
        "describe my future partner",
        "future spouse personality",
        "spouse personality",
        "partner personality",
        "future spouse traits",
        "spouse traits",
        "partner traits",
        "nature of my spouse",
        "nature of future spouse",
        "character of my spouse",
        "character of future spouse",
        "how will my spouse be",
        "how will my future spouse be",
        "who will i marry",
        "what type of person will i marry",
        "what type of spouse will i have",
        "what kind of spouse will i have",
    )

    matched = [
        keyword
        for keyword in spouse_traits_keywords
        if keyword in question
    ]

    if matched:

        detected.append(
            {
                "event": (
                    "spouse_traits"
                ),
                "event_label": (
                    EVENT_LABELS[
                        "spouse_traits"
                    ]
                ),
                "matched_keywords": (
                    matched
                ),
            }
        )

    # -----------------------------------------------------
    # LOVE VS ARRANGED
    # -----------------------------------------------------

    love_arranged_keywords = (
        "love marriage or arranged marriage",
        "love or arranged marriage",
        "love vs arranged",
        "arranged or love marriage",
        "arranged marriage or love marriage",
    )

    matched = [
        keyword
        for keyword in love_arranged_keywords
        if keyword in question
    ]

    if matched:

        detected.append(
            {
                "event": (
                    "love_vs_arranged"
                ),
                "event_label": (
                    EVENT_LABELS[
                        "love_vs_arranged"
                    ]
                ),
                "matched_keywords": (
                    matched
                ),
            }
        )

        return detected

    # -----------------------------------------------------
    # LOVE MARRIAGE
    # -----------------------------------------------------

    love_keywords = (
        "love marriage",
        "marry someone i love",
        "marry my partner",
        "marry my boyfriend",
        "marry my girlfriend",
    )

    matched = [
        keyword
        for keyword in love_keywords
        if keyword in question
    ]

    if matched:

        detected.append(
            {
                "event": (
                    "love_marriage"
                ),
                "event_label": (
                    EVENT_LABELS[
                        "love_marriage"
                    ]
                ),
                "matched_keywords": (
                    matched
                ),
            }
        )

    # -----------------------------------------------------
    # ARRANGED MARRIAGE
    # -----------------------------------------------------

    arranged_keywords = (
        "arranged marriage",
        "family arranged",
        "family will arrange",
    )

    matched = [
        keyword
        for keyword in arranged_keywords
        if keyword in question
    ]

    if matched:

        detected.append(
            {
                "event": (
                    "arranged_marriage"
                ),
                "event_label": (
                    EVENT_LABELS[
                        "arranged_marriage"
                    ]
                ),
                "matched_keywords": (
                    matched
                ),
            }
        )

    return detected


# =========================================================
# BASE EVENT CLEANUP
# =========================================================

def _clean_base_events(
    base_events: list[Any],
    special_events: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    special_names = {
        str(
            item.get(
                "event",
                "",
            )
        )
        for item in special_events
        if isinstance(
            item,
            dict,
        )
    }

    cleaned = []

    for raw_item in base_events:

        if not isinstance(
            raw_item,
            dict,
        ):

            continue

        event_name = str(
            raw_item.get(
                "event",
                "",
            )
        )

        if (
            "spouse_meeting"
            in special_names
            and event_name
            in (
                "spouse_traits",
                "spouse_appearance",
                "general_marriage",
            )
        ):

            continue

        if (
            "foreign_intercultural_connection"
            in special_names
            and event_name
            in (
                "spouse_traits",
                "spouse_appearance",
                "marriage_timing",
                "general_marriage",
            )
        ):

            continue

        if (
            "spouse_profession"
            in special_names
            and event_name
            in (
                "spouse_traits",
                "spouse_appearance",
                "marriage_timing",
                "general_marriage",
            )
        ):

            continue

        if (
            "spouse_education" in special_names
            and event_name in ("spouse_profession","spouse_traits","spouse_appearance","marriage_timing","general_marriage")
        ):
            continue

        if (
            "spouse_appearance"
            in special_names
            and event_name
            in (
                "spouse_traits",
                "marriage_timing",
                "general_marriage",
            )
        ):

            continue

        if (
            "spouse_traits"
            in special_names
            and event_name
            in (
                "marriage_timing",
                "general_marriage",
            )
        ):

            continue

        if (
            "love_vs_arranged"
            in special_names
            and event_name
            in (
                "marriage_timing",
                "love_marriage",
                "arranged_marriage",
            )
        ):

            continue

        cleaned.append(
            raw_item
        )

    return cleaned


# =========================================================
# SPECIAL EVENT CONFLICT CLEANUP
# =========================================================

def _clean_special_event_conflicts(
    special_events: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    names = {
        str(
            item.get(
                "event",
                "",
            )
        )
        for item in special_events
        if isinstance(
            item,
            dict,
        )
    }

    cleaned = []

    for item in special_events:

        if not isinstance(
            item,
            dict,
        ):

            continue

        event_name = str(
            item.get(
                "event",
                "",
            )
        )

        if (
            "spouse_meeting"
            in names
            and event_name
            in (
                "spouse_traits",
                "spouse_appearance",
                "spouse_profession",
                "foreign_intercultural_connection",
            )
        ):

            continue

        if (
            "spouse_education" in names
            and event_name in ("spouse_profession","foreign_intercultural_connection","spouse_appearance","spouse_traits")
        ):
            continue

        if (
            "spouse_profession"
            in names
            and event_name
            in (
                "foreign_intercultural_connection",
                "spouse_appearance",
                "spouse_traits",
            )
        ):

            continue

        if (
            "foreign_intercultural_connection"
            in names
            and event_name
            in (
                "spouse_appearance",
                "spouse_traits",
            )
        ):

            continue

        if (
            "spouse_appearance"
            in names
            and event_name
            == "spouse_traits"
        ):

            continue

        cleaned.append(
            item
        )

    return cleaned


# =========================================================
# EVENT MERGING
# =========================================================

def _merge_events(
    base_events: list[Any],
    special_events: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    cleaned_special = (
        _clean_special_event_conflicts(
            special_events
        )
    )

    cleaned_base = (
        _clean_base_events(
            base_events,
            cleaned_special,
        )
    )

    merged = []

    seen = set()

    for item in (
        cleaned_base
        + cleaned_special
    ):

        if not isinstance(
            item,
            dict,
        ):

            continue

        event_name = str(
            item.get(
                "event",
                "",
            )
        )

        if not event_name:

            continue

        if event_name in seen:

            continue

        seen.add(
            event_name
        )

        merged.append(
            item
        )

    return merged


# =========================================================
# COMPARISON EVENT INJECTION
# =========================================================

def _inject_comparison_event(
    detected_events: list[dict[str, Any]],
    comparison: dict[str, Any],
    question: str,
) -> list[dict[str, Any]]:

    if not comparison.get(
        "is_comparison"
    ):

        return detected_events

    if not (
        "marriage" in question
        or "marry" in question
    ):

        return detected_events

    existing_names = {
        item.get(
            "event"
        )
        for item in detected_events
    }

    specific_events = {
        "relationship_commitment",
        "marriage_delay_challenge",
        "relationship_stability",
        "foreign_intercultural_connection",
        "spouse_traits",
        "spouse_appearance",
        "spouse_education",
        "spouse_profession",
        "spouse_meeting",
        "love_marriage",
        "arranged_marriage",
        "love_vs_arranged",
    }

    if existing_names.intersection(
        specific_events
    ):

        return detected_events

    if (
        "marriage_timing"
        in existing_names
    ):

        return detected_events

    return (
        detected_events
        + [
            {
                "event": (
                    "marriage_timing"
                ),
                "event_label": (
                    EVENT_LABELS[
                        "marriage_timing"
                    ]
                ),
                "matched_keywords": [
                    "marriage"
                ],
            }
        ]
    )


# =========================================================
# PRIMARY EVENT
# =========================================================

def _resolve_primary_event(
    base_analysis: dict[str, Any],
    detected_events: list[dict[str, Any]],
    comparison: dict[str, Any],
    question: str,
) -> str:

    detected_names = {
        item.get(
            "event"
        )
        for item in detected_events
    }

    priority = (
        "love_vs_arranged",
        "spouse_meeting",
        "spouse_education",
        "spouse_profession",
        "foreign_intercultural_connection",
        "spouse_appearance",
        "spouse_traits",
        "love_marriage",
        "arranged_marriage",
        "marriage_delay_challenge",
        "relationship_stability",
        "relationship_commitment",
        "marriage_timing",
    )

    for event_name in priority:

        if event_name in detected_names:

            return event_name

    if (
        comparison.get(
            "is_comparison"
        )
        and (
            "marriage" in question
            or "marry" in question
        )
    ):

        return (
            "marriage_timing"
        )

    base_primary = str(
        base_analysis.get(
            "primary_event",
            "",
        )
        or ""
    )

    if (
        base_primary
        and base_primary
        != "general_marriage"
    ):

        return (
            base_primary
        )

    return (
        "general_marriage"
    )


# =========================================================
# QUESTION TYPE
# =========================================================

def _resolve_question_type(
    question: str,
    primary_event: str,
    base_analysis: dict[str, Any],
    comparison: dict[str, Any],
) -> str:

    if comparison.get(
        "is_comparison"
    ):

        return (
            "comparison"
        )

    if primary_event in (
        "spouse_traits",
        "love_vs_arranged",
    ):

        return (
            "general_outlook"
        )

    if primary_event in (
        "spouse_profession",
        "spouse_appearance",
        "spouse_education",
        "foreign_intercultural_connection",
    ):

        probability_prefixes = (
            "will ",
            "could ",
            "can ",
            "is ",
            "does ",
            "do ",
            "would ",
            "am i ",
        )

        if any(
            question.startswith(
                prefix
            )
            for prefix in probability_prefixes
        ):

            return (
                "probability"
            )

        return (
            "general_outlook"
        )

    if (
        question.startswith(
            "when "
        )
        or "when will" in question
        or "when do" in question
    ):

        return (
            "timing"
        )

    if any(
        question.startswith(
            prefix
        )
        for prefix in (
            "will ",
            "could ",
            "can ",
            "is ",
            "am i ",
            "do i ",
            "would ",
        )
    ):

        return (
            "probability"
        )

    base_intent = _safe_dict(
        base_analysis.get(
            "intent"
        )
    )

    return str(
        base_intent.get(
            "question_type",
            "general_outlook",
        )
    )


# =========================================================
# DIRECTION
# =========================================================

def _resolve_direction(
    primary_event: str,
    base_analysis: dict[str, Any],
) -> str:

    if (
        primary_event
        == "marriage_delay_challenge"
    ):

        return (
            "increase"
        )

    if primary_event in (
        "marriage_timing",
        "relationship_commitment",
        "spouse_meeting",
        "love_marriage",
        "arranged_marriage",
        "foreign_intercultural_connection",
    ):

        return (
            "occurrence"
        )

    if primary_event in (
        "spouse_traits",
        "spouse_appearance",
        "spouse_education",
        "spouse_profession",
        "love_vs_arranged",
    ):

        return (
            "neutral"
        )

    if (
        primary_event
        == "relationship_stability"
    ):

        return (
            "increase"
        )

    base_intent = _safe_dict(
        base_analysis.get(
            "intent"
        )
    )

    return str(
        base_intent.get(
            "direction",
            "neutral",
        )
    )


# =========================================================
# CONFIDENCE
# =========================================================

def _resolve_confidence(
    primary_event: str,
    base_analysis: dict[str, Any],
    comparison: dict[str, Any],
) -> float:

    base_intent = _safe_dict(
        base_analysis.get(
            "intent"
        )
    )

    base_confidence = float(
        base_intent.get(
            "confidence",
            0.60,
        )
        or 0.60
    )

    if comparison.get(
        "is_comparison"
    ):

        return max(
            base_confidence,
            0.82,
        )

    if primary_event in (
        "love_vs_arranged",
        "spouse_meeting",
        "spouse_traits",
        "spouse_appearance",
        "spouse_education",
        "spouse_profession",
        "foreign_intercultural_connection",
        "love_marriage",
        "arranged_marriage",
    ):

        return max(
            base_confidence,
            0.82,
        )

    return (
        base_confidence
    )


# =========================================================
# QUERY MODE
# =========================================================

def _resolve_query_mode(
    comparison: dict[str, Any],
    follow_up: dict[str, Any],
    detected_events: list[dict[str, Any]],
) -> str:

    if follow_up.get(
        "is_follow_up"
    ):

        return (
            "follow_up"
        )

    if comparison.get(
        "is_comparison"
    ):

        return (
            "comparison"
        )

    if len(
        detected_events
    ) > 1:

        return (
            "multi_event"
        )

    return (
        "single_event"
    )


# =========================================================
# COMPLEXITY
# =========================================================

def _resolve_complexity(
    query_mode: str,
    event_count: int,
) -> str:

    if (
        query_mode
        in (
            "comparison",
            "multi_event",
            "follow_up",
        )
        or event_count > 1
    ):

        return (
            "enhanced"
        )

    return (
        "standard"
    )


# =========================================================
# MAIN ANALYZER
# =========================================================

def analyze_marriage_question_v3(
    question: str,
) -> dict[str, Any]:

    if not isinstance(
        question,
        str,
    ):

        raise ValueError(
            "question must be a string."
        )

    normalised = (
        _normalise_question(
            question
        )
    )

    if not normalised:

        raise ValueError(
            "question must not be empty."
        )

    base_analysis = (
        analyze_marriage_question_v2(
            question
        )
    )

    base_events = _safe_list(
        base_analysis.get(
            "detected_events"
        )
    )

    special_events = (
        _detect_special_events(
            normalised
        )
    )

    comparison = (
        _detect_comparison(
            normalised
        )
    )

    follow_up = (
        _detect_follow_up(
            normalised
        )
    )

    detected_events = (
        _merge_events(
            base_events,
            special_events,
        )
    )

    detected_events = (
        _inject_comparison_event(
            detected_events,
            comparison,
            normalised,
        )
    )

    primary_event = (
        _resolve_primary_event(
            base_analysis,
            detected_events,
            comparison,
            normalised,
        )
    )

    primary_event_label = (
        EVENT_LABELS.get(
            primary_event,
            str(
                base_analysis.get(
                    "primary_event_label",
                    primary_event,
                )
            ),
        )
    )

    question_type = (
        _resolve_question_type(
            normalised,
            primary_event,
            base_analysis,
            comparison,
        )
    )

    direction = (
        _resolve_direction(
            primary_event,
            base_analysis,
        )
    )

    confidence = (
        _resolve_confidence(
            primary_event,
            base_analysis,
            comparison,
        )
    )

    query_mode = (
        _resolve_query_mode(
            comparison,
            follow_up,
            detected_events,
        )
    )

    event_count = len(
        detected_events
    )

    complexity = (
        _resolve_complexity(
            query_mode,
            event_count,
        )
    )

    result = dict(
        base_analysis
    )

    result.update(
        {
            "available": True,
            "original_question": (
                question
            ),
            "normalised_question": (
                normalised
            ),
            "query_mode": (
                query_mode
            ),
            "complexity": (
                complexity
            ),
            "primary_event": (
                primary_event
            ),
            "primary_event_label": (
                primary_event_label
            ),
            "detected_events": (
                detected_events
            ),
            "event_count": (
                event_count
            ),
            "is_multi_event": (
                event_count > 1
            ),
            "comparison": (
                comparison
            ),
            "follow_up": (
                follow_up
            ),
            "intent": {
                "domain": (
                    "marriage"
                ),
                "event": (
                    primary_event
                ),
                "event_label": (
                    primary_event_label
                ),
                "question_type": (
                    question_type
                ),
                "direction": (
                    direction
                ),
                "confidence": (
                    confidence
                ),
            },
        }
    )

    return (
        result
    )