from app.services.question_language_aliases_v1 import normalize_question_for_routing_v1
from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3
from app.astrology.features.family_children_question_intelligence_v1 import analyze_family_children_question_v1


def test_hinglish_love_vs_arranged_maps_to_supported_marriage_question():
    routed = normalize_question_for_routing_v1("Meri Love marriage hogi ya arranged marriage")
    assert routed == "love marriage or arranged marriage"
    analysis = analyze_marriage_question_v3(routed)
    assert analysis["available"] is True
    assert analysis["primary_event"] in {"love_vs_arranged", "love_marriage", "arranged_marriage"}


def test_hinglish_shaadi_kab_hogi_maps_to_marriage_timing():
    routed = normalize_question_for_routing_v1("meri shaadi kab hogi")
    assert routed == "when will i get married"
    analysis = analyze_marriage_question_v3(routed)
    assert analysis["available"] is True
    assert analysis["primary_event"] == "marriage_timing"


def test_hinglish_first_child_timing_maps_to_family_timing():
    routed = normalize_question_for_routing_v1("Mera pehla bacha kab hoga")
    assert routed == "when will i have my first child"
    analysis = analyze_family_children_question_v1(routed)
    assert analysis["available"] is True
    assert analysis["requires_timing_engine"] is True


def test_english_first_kid_timing_remains_supported():
    routed = normalize_question_for_routing_v1("When will I have my 1st kid?")
    analysis = analyze_family_children_question_v1(routed)
    assert analysis["available"] is True
    assert analysis["requires_timing_engine"] is True
