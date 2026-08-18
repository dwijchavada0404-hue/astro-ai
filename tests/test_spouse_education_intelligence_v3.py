from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3

def test_spouse_education_detection():
    for q in ["What kind of education will my future spouse have?","Will my spouse be highly educated?","Will my spouse have a finance degree?","Will my spouse be educated abroad?","Will my spouse be intelligent and analytical?"]:
        r=analyze_marriage_question_v3(q)
        assert r["primary_event"]=="spouse_education"
        assert r["query_mode"]=="single_event"

def test_profession_not_hijacked():
    assert analyze_marriage_question_v3("Will my spouse work in finance?")["primary_event"]=="spouse_profession"
