from app.services.answer_experience_v2 import present_answer_v2


def test_property_answer_uses_hinglish_and_month_dates():
    routed = {"domain":"property_home","result":{"timing":{"future":{"strongest_period":{"start":"2028-08-12T00:00:00+05:30","end":"2029-05-03T00:00:00+05:30"}}}}}
    answer = present_answer_v2(routed)
    assert "Aapke chart" in answer
    assert "Aug 2028 – May 2029" in answer
    assert "2028-08-12" not in answer


def test_property_answer_includes_past_and_future_windows():
    routed = {"domain":"property_home","result":{"timing":{"past":{"strongest_period":{"start":"2025-10-01","end":"2026-01-31"}},"future":{"strongest_period":{"start":"2027-04-01","end":"2030-06-30"}}}}}
    answer = present_answer_v2(routed)
    assert "Oct 2025 – Jan 2026" in answer
    assert "Apr 2027 – Jun 2030" in answer
    assert "first home" in answer.lower()


def test_property_answer_can_be_english():
    routed = {"domain":"property_home","result":{"timing":{"future":{"strongest_period":{"start":"2028-08-12","end":"2029-05-03"}}}}}
    answer = present_answer_v2(routed, "english")
    assert "Aug 2028 – May 2029" in answer
    assert answer.startswith("Your chart shows")


def test_love_arranged_mixed_answer_is_natural_hinglish():
    routed = {"domain":"marriage","answer":"The natal evidence gives arranged/family-mediated marriage a relative support score of 55.7%. The overall pattern is classified as Mixed / Hybrid Pathway.","result":{}}
    answer = present_answer_v2(routed)
    assert "love-cum-arranged" in answer
    assert "55.7%" not in answer
    assert "Mixed / Hybrid Pathway" not in answer


def test_family_children_timing_is_specific_but_not_childbirth_prediction():
    routed = {"domain":"family_children","result":{"timing":{"past":{"strongest_period":{"start":"2024-01-01","end":"2024-08-01"}},"future":{"strongest_period":{"start":"2027-03-01","end":"2028-02-01"}}}}}
    answer = present_answer_v2(routed)
    assert "Mar 2027 – Feb 2028" in answer
    assert "Jan 2024 – Aug 2024" in answer
    assert "fixed prediction" in answer


def test_child_count_boundary_is_natural_in_each_answer_language():
    routed = {"domain":"family_children","result":{"children_question_boundary":"child_count"}}
    assert "artificial number" in present_answer_v2(routed, "hinglish")
    assert "will not invent" in present_answer_v2(routed, "english")
    assert "कृत्रिम संख्या" in present_answer_v2(routed, "hindi")


def test_foreign_travel_answer_is_not_engine_debug_copy():
    routed = {"domain":"location_settlement","answer":"Location events are ranked from natal patterns and available dasha timing; scores describe activation, not event probability.","result":{"event_result":{"future":{"timing_period":{"start":"2027-01-01","end":"2027-09-30"}}}}}
    answer = present_answer_v2(routed)
    assert "Foreign travel" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "Location events are ranked" not in answer


def test_raw_iso_dates_are_cleaned_for_fallback_domains():
    routed = {"domain":"career","answer":"A supportive phase runs from 2027-02-12 to 2027-10-19."}
    assert present_answer_v2(routed, "english") == "A supportive phase runs from Feb 2027 to Oct 2027."
