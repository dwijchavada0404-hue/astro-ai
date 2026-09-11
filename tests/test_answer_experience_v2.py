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


def test_finance_timing_uses_a_natural_safe_answer_in_each_language():
    routed = {"domain":"finance_wealth","result":{"timing":{"future":{"strongest_period":{"start":"2027-03-01","end":"2028-02-01"}}}}}
    assert "Mar 2027 – Feb 2028" in present_answer_v2(routed, "hinglish")
    assert "fixed guarantee" in present_answer_v2(routed, "english")
    assert "निश्चित गारंटी" in present_answer_v2(routed, "hindi")


def test_finance_source_answer_hides_raw_scores():
    routed = {"domain":"finance_wealth","result":{"source_of_wealth":{"primary_source_label":"salary, career and profession-linked income","secondary_source_label":"networks, scaling, side income and multiple-income opportunities","primary_score":0.91}}}
    answer = present_answer_v2(routed, "hinglish")
    assert "0.91" not in answer
    assert "salary, career and profession-linked income" in answer


def test_education_answer_uses_natural_timing_without_guarantees():
    routed = {"domain":"education_learning","result":{"synthesis":{"strongest_area":"skill_development","strongest_future_period":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "skill development" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "guarantee" in answer


def test_purpose_answer_is_natural_and_not_fixed_destiny():
    routed = {"domain":"purpose_personal_growth","result":{"synthesis":{"strongest_area":"creative_expression","strongest_future_period":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "creative expression" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "fixed destiny" in answer


def test_social_answer_is_natural_without_specific_person_claims():
    routed = {"domain":"friends_social_community","result":{"synthesis":{"strongest_area":"networking","strongest_future_period":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "networking" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "specific person" in answer


def test_parents_elders_answer_keeps_other_person_boundary():
    routed = {"domain":"parents_elders","result":{"synthesis":{"strongest_area":"guidance_mentorship","strongest_future_period":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "guidance mentorship" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "other person ke behaviour" in answer


def test_siblings_answer_keeps_specific_person_boundary():
    routed = {"domain":"siblings_communication","result":{"synthesis":{"strongest_area":"communication_expression","strongest_future_period":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "communication expression" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "specific person" in answer


def test_legal_conflict_answer_is_natural_and_not_a_case_prediction():
    routed = {"domain":"legal_disputes_conflict","result":{"synthesis":{"strongest_area":"negotiation_mediation","strongest_future_period":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "negotiation mediation" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "legal outcome" in answer


def test_legal_conflict_safety_boundary_is_natural_in_each_language():
    routed = {"domain":"legal_disputes_conflict","result":{"route":"legal_disputes_conflict_safety_boundary_v1"}}
    assert "case ka result" in present_answer_v2(routed)
    assert "court verdict" in present_answer_v2(routed, "english")
    assert "अदालत का फैसला" in present_answer_v2(routed, "hindi")


def test_foreign_travel_answer_is_not_engine_debug_copy():
    routed = {"domain":"location_settlement","answer":"Location events are ranked from natal patterns and available dasha timing; scores describe activation, not event probability.","result":{"event_result":{"future":{"timing_period":{"start":"2027-01-01","end":"2027-09-30"}}}}}
    answer = present_answer_v2(routed)
    assert "Foreign travel" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "Location events are ranked" not in answer


def test_travel_overview_uses_a_natural_answer():
    routed = {"domain":"travel_journeys","result":{"synthesis":{"strongest_area":"international_exposure"}}}
    answer = present_answer_v2(routed)
    assert "international exposure" in answer
    assert "combined Travel" not in answer


def test_travel_safety_boundary_is_natural_in_hinglish():
    routed = {"domain":"travel_journeys","result":{"route":"travel_journeys_safety_boundary_v1"}}
    answer = present_answer_v2(routed)
    assert "visa approval" in answer
    assert "symbolic" not in answer.lower()


def test_health_answer_is_natural_and_non_medical():
    routed = {"domain":"health_wellbeing","result":{"synthesis":{"strongest_area":"stress_balance","strongest_future_period":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "stress balance" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "medical prediction" in answer


def test_health_safety_boundary_is_natural_in_hindi():
    routed = {"domain":"health_wellbeing","result":{"route":"health_wellbeing_safety_boundary_v1"}}
    answer = present_answer_v2(routed, "hindi")
    assert "चिकित्सकीय सलाह" in answer
    assert "disease" not in answer.lower()


def test_raw_iso_dates_are_cleaned_for_fallback_domains():
    routed = {"domain":"career","answer":"A supportive phase runs from 2027-02-12 to 2027-10-19."}
    assert present_answer_v2(routed, "english") == "A supportive phase runs from Feb 2027 to Oct 2027."


def test_life_settlement_answer_uses_natural_combined_timing_without_a_deadline():
    routed = {"domain":"life_settlement","result":{"timing":{"strongest_convergence_window":{"start":"2027-01-01","end":"2027-09-30"}}}}
    answer = present_answer_v2(routed)
    assert "Jan 2027 – Sep 2027" in answer
    assert "fixed deadline" in answer
    assert "cross-domain" not in answer.lower()


def test_life_settlement_overview_uses_natural_foundations():
    routed = {"domain":"life_settlement","result":{"synthesis":{"strongest_domains":["career","property_home"]}}}
    answer = present_answer_v2(routed, "english")
    assert "career, property home" in answer
    assert "fixed settled-life outcome" in answer


def test_location_settlement_answer_is_distinct_from_short_travel():
    routed = {"domain":"location_settlement","result":{"primary_intent":"foreign_settlement","event_result":{"label":"establishing a longer-term base outside the place of origin","future":{"timing_period":{"start":"2027-01-01","end":"2027-09-30"}}}}}
    answer = present_answer_v2(routed)
    assert "longer-term base" in answer
    assert "Jan 2027 – Sep 2027" in answer
    assert "visa, immigration, citizenship" in answer
    assert not answer.startswith("Foreign travel")
