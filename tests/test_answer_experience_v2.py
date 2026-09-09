from app.services.answer_experience_v2 import present_answer_v2


def test_property_answer_uses_hinglish_and_month_dates():
    routed = {
        "domain": "property_home",
        "answer": "Property & Home timing is compared across recent past, present and future dasha periods.",
        "result": {"timing": {"future": {"strongest_period": {"start": "2028-08-12T00:00:00+05:30", "end": "2029-05-03T00:00:00+05:30"}}}},
    }
    answer = present_answer_v2(routed)
    assert "Aapke chart" in answer
    assert "Aug 2028 – May 2029" in answer
    assert "2028-08-12" not in answer


def test_property_answer_can_be_english():
    routed = {"domain": "property_home", "result": {"timing": {"future": {"strongest_period": {"start": "2028-08-12", "end": "2029-05-03"}}}}}
    answer = present_answer_v2(routed, "english")
    assert answer.startswith("Your chart shows Aug 2028 – May 2029")


def test_foreign_travel_answer_is_not_engine_debug_copy():
    routed = {
        "domain": "location_settlement",
        "answer": "Location events are ranked from natal patterns and available dasha timing; scores describe activation, not event probability.",
        "result": {"event_result": {"future": {"timing_period": {"start": "2027-01-01", "end": "2027-09-30"}}}},
    }
    answer = present_answer_v2(routed)
    assert "Foreign travel" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "Location events are ranked" not in answer


def test_raw_iso_dates_are_cleaned_for_fallback_domains():
    routed = {"domain": "career", "answer": "A supportive phase runs from 2027-02-12 to 2027-10-19."}
    assert present_answer_v2(routed, "english") == "A supportive phase runs from Feb 2027 to Oct 2027."
